"""Installed entry point for verification environment preparation."""

import argparse
from json import dumps
from pathlib import Path
from shlex import join
from uuid import uuid4

from aitm_core.models.binding import StoryRef
from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.services import preflight_policy
from aitm_core.setup.init import _active_installation
from aitm_core.store.objects import GitCommandError, Repository
from aitm_core.store.workspace import BindingConflict, Workspace
from aitm_core.verification.capture import CaptureUnavailable, _discard, capture_inputs
from aitm_core.verification.provision import provision


def handle(route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    parser = argparse.ArgumentParser(
        prog=f"aitm {' '.join(route)}", exit_on_error=False
    )
    parser.add_argument("story", type=int)
    parser.add_argument("--binding", required=True)
    parser.add_argument("--generation", type=int, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--offline", action="store_true")
    operation_id = uuid4().hex
    retry = f"Retry with `{join(('aitm', *route, *arguments))}` after preparation is available."
    capture = None
    try:
        args = parser.parse_args(arguments)
        installation, _ = _active_installation(
            Repository(Path.cwd(), "refs/heads/aitm-prepare-probe")
        )
        # Preparation consumes the admitted policy pin without adopting planning.
        current = preflight_policy(installation, cached=True)
        if current.outcome != LocalOutcome.COMPLETED or current.policy is None:
            return CommandResult(
                operation_id=operation_id,
                local=LocalOutcome.UNAVAILABLE,
                evidence=(*current.evidence, retry),
            )
        workspace = Workspace(installation)
        with workspace.lock():
            binding = workspace.require(
                StoryRef(story=args.story), args.binding, args.generation, args.session
            )
        capture = capture_inputs(installation, binding, current.policy)
        result = provision(
            installation, binding, current.policy, capture, offline=args.offline
        )
        if result.status == "ready" and result.prepared is not None:
            prepared = result.prepared
            return CommandResult(
                operation_id=operation_id,
                local=LocalOutcome.COMPLETED,
                evidence=(
                    dumps(
                        {
                            "environment": str(prepared.directory),
                            "identity": prepared.receipt.identity.digest,
                            "inventory": prepared.receipt.inventory_digest,
                        },
                        sort_keys=True,
                    ),
                ),
            )
        reason = result.reason or "The exact verification environment is unavailable."
        return CommandResult(
            operation_id=operation_id,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(f"preparation-unavailable: {reason}", retry),
        )
    except (argparse.ArgumentError, BindingConflict) as error:
        return CommandResult(
            operation_id=operation_id,
            local=LocalOutcome.REFUSED,
            evidence=(str(error),),
        )
    except (CaptureUnavailable, GitCommandError, OSError, ValueError) as error:
        return CommandResult(
            operation_id=operation_id,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(f"preparation-unavailable: {error}", retry),
        )
    finally:
        if capture is not None:
            _discard(capture.directory)
