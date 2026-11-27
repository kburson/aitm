"""Installed entry point for Core installation."""

import argparse
from dataclasses import replace
from os import fsdecode
from pathlib import Path
from sys import stderr, stdin
from uuid import uuid4

from aitm_core.models.common import CommandResult, LocalOutcome
from aitm_core.setup.adoption import AdoptionProposal, prepare_replacement, reconfigure
from aitm_core.setup.init import (
    InitRequest,
    _active_installation,
    adopt_committed,
    prepare_init,
    resume_init,
)
from aitm_core.setup.journal import read_proposal, state_directory
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import GitCommandError, Repository


def handle(_route: tuple[str, ...], arguments: tuple[str, ...]) -> CommandResult:
    parser = argparse.ArgumentParser(prog="aitm init", exit_on_error=False)
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--reconfigure", action="store_true")
    parser.add_argument("--replacement-branch")
    parser.add_argument("--default-branch")
    parser.add_argument("--code-remote")
    parser.add_argument("--planning-remote")
    parser.add_argument("--planning-branch")
    parser.add_argument("--review-policy", type=Path)
    parser.add_argument("--workflow", type=Path)
    try:
        options = parser.parse_args(arguments)
        repo = Repository(Path.cwd(), "refs/heads/aitm-bootstrap-probe")
        if options.local and (options.code_remote or options.planning_remote):
            raise ValueError("--local cannot select a remote.")
        descriptor = state_directory(repo) / "installation.json"
        saved = None
        if descriptor.exists():
            installation, _ = _active_installation(repo)
            saved = installation
            anchor = installation.store
        else:
            saved = read_proposal(repo)
            anchor = saved.anchor if saved else None
        remote = (
            None
            if options.local
            else options.code_remote
            or (saved.code_remote if saved is not None else "origin")
        )
        branch = options.default_branch or (
            anchor.code_default_ref.removeprefix("refs/heads/") if anchor else None
        )
        if branch is None:
            if remote is None:
                raise ValueError("Select --default-branch for local installation.")
            url = fsdecode(repo._git("remote", "get-url", "--", remote).rstrip(b"\n"))
            refs = (
                repo._git("ls-remote", "--symref", "--", url, "HEAD")
                .decode()
                .splitlines()
            )
            names = [
                line.removeprefix("ref: refs/heads/").removesuffix("\tHEAD")
                for line in refs
                if line.startswith("ref: refs/heads/") and line.endswith("\tHEAD")
            ]
            if len(names) != 1:
                raise ValueError(
                    "Select --default-branch because the remote default is ambiguous."
                )
            branch = names[0]
        name = options.planning_branch
        if name is None and anchor is not None:
            name = anchor.planning_ref.removeprefix("refs/heads/")
        if name is None and stdin.isatty() and options.workflow is not None:
            print("Planning branch [planning]: ", end="", file=stderr, flush=True)
            name = stdin.readline().strip()
        request = InitRequest(
            repository=repo.root,
            default_branch=branch,
            planning_branch=name or "planning",
            code_remote=remote,
            planning_remote=options.planning_remote
            or (
                anchor.planning_remote
                if anchor is not None and not options.reconfigure
                else None
            ),
            review_policy=options.review_policy.read_text()
            if options.review_policy
            else None,
            workflow=options.workflow.read_text() if options.workflow else None,
        )
        if options.replacement_branch is not None:
            if not options.reconfigure:
                raise ValueError("--replacement-branch requires --reconfigure.")
            return prepare_replacement(request, options.replacement_branch).command
        if options.reconfigure:
            return reconfigure(AdoptionProposal(request)).command
        existing = adopt_committed(
            request, check_branch=name is not None and bool(name)
        )
        if existing is not None:
            return existing.command
        if remote is not None and request.planning_remote is None:
            request = replace(request, planning_remote=remote)
        proposal = prepare_init(request)
        return resume_init(request, proposal.operation_id).command
    except (
        argparse.ArgumentError,
        GitCommandError,
        ValidationRejected,
        ValueError,
    ) as error:
        outcome = LocalOutcome.INTEGRITY_ERROR
        reason = str(error)
    except OSError as error:
        outcome = LocalOutcome.UNAVAILABLE
        reason = str(error)
    return CommandResult(operation_id=uuid4().hex, local=outcome, evidence=(reason,))
