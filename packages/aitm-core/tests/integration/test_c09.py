"""Exercise C09 default publication through the installed CLI and real Git."""

from dataclasses import replace
from hashlib import sha256
from json import dumps, loads
from os import environ
from pathlib import Path
from shlex import quote
from shutil import which
from subprocess import run

import pytest

from aitm_core.cli.describe import handle
from aitm_core.cli.dispatch import publish as retry_publication
from aitm_core.description import DescriptionInput, DescriptionTarget, describe
from aitm_core.events import core_reducers, fold
from aitm_core.models.common import PublicationOutcome
from aitm_core.models.operations import (
    AuthorityOrigin,
    ReadExpectation,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.services import ServicePorts, preflight_policy
from aitm_core.store.objects import Repository
from aitm_core.store.publication import Publisher
from aitm_core.store.reconcile import Resolution, reconcile
from tests.integration.test_c08 import (
    CODE_REMOTE,
    DEFAULT,
    PLANNING,
    PLANNING_REMOTE,
    commit_file,
    git,
    identify,
)
from tests.integration.test_c08 import (
    topology as topology,
)
from tests.unit.test_c15 import DESCRIPTION, EVENTS, graduated


def describe_args(topology, scratch, story=16):
    scratch.mkdir(exist_ok=True)
    installation = topology.policy.installation
    anchor_file = scratch / "anchor.json"
    anchor_file.write_text(installation.store.model_dump_json())
    descriptor = scratch / "installation.json"
    descriptor.write_text(
        dumps(
            {
                "code_repository": installation.code_repository,
                "planning_repository": installation.planning_repository,
                "bootstrap_source": installation.bootstrap_source,
                "issuer": installation.issuer.model_dump(),
                "code_remote": installation.code_remote,
                "code_remote_ref": installation.code_remote_ref,
            }
        )
    )
    scope = scratch / "scope.md"
    scope.write_text("Describe the pinned planning store.\n")
    return (
        str(story),
        "--title",
        "Read the store",
        "--as",
        "operator",
        "--want",
        "immutable evidence",
        "--so-that",
        "I can verify it",
        "--scope-file",
        str(scope),
        "--anchor",
        str(anchor_file),
        "--installation",
        str(descriptor),
    )


def invoke_describe(topology, scratch, *, environment=None, story=16):
    cli = which("aitm")
    assert cli is not None
    return run(
        [cli, "--json", "describe", *describe_args(topology, scratch, story)],
        cwd=topology.local,
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )


def test_describe_attempts_default_publication(topology, tmp_path):
    topology.advance_planning(EVENTS, graduated())
    executed = invoke_describe(topology, tmp_path)
    outcome = loads(executed.stdout)
    assert outcome["local"] == "completed"
    assert outcome["publication"] == "verified", executed.stdout
    assert executed.returncode == 0
    remote = Path(git(topology.local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == topology.writer()
    repo = Repository(topology.local, PLANNING)
    saved = repo.read_blobs(repo.tip().tree, (EVENTS, DESCRIPTION))
    assert b"Describe the pinned planning store." in saved[DESCRIPTION]
    story = fold(saved[EVENTS].splitlines(keepends=True), core_reducers())
    assert story.domains["lifecycle"].description.title == "Read the store"


def cloned(topology, scratch):
    local = scratch / "second"
    git(
        scratch,
        "clone",
        "-q",
        "-b",
        "trunk",
        git(topology.local, "remote", "get-url", CODE_REMOTE),
        str(local),
    )
    identify(local)
    git(local, "remote", "rename", "origin", CODE_REMOTE)
    route = git(topology.local, "remote", "get-url", PLANNING_REMOTE)
    git(local, "remote", "add", PLANNING_REMOTE, route)
    git(local, "fetch", "-q", PLANNING_REMOTE, PLANNING)
    git(local, "update-ref", PLANNING, git(local, "rev-parse", "FETCH_HEAD"))
    installation = replace(
        topology.policy.installation, repository=Repository(local, PLANNING)
    )
    return replace(
        topology,
        local=local,
        policy=replace(topology.policy, installation=installation),
    )


@pytest.mark.parametrize("race_kind", ["authored", "disjoint", "related", "policy"])
def test_racing_clones_replay_only_whole_disjoint_operations(
    topology, tmp_path, monkeypatch, race_kind
):
    other_story = 16 if race_kind == "authored" else 17
    topology.advance_planning(EVENTS, graduated())
    if other_story != 16:
        second_seed = loads(graduated())
        second_seed["story"] = other_story
        topology.advance_planning(
            story_event_path(other_story), dumps(second_seed).encode() + b"\n"
        )
    other = cloned(topology, tmp_path)
    remote = Path(git(topology.local, "remote", "get-url", PLANNING_REMOTE))
    original_push = Publisher._push
    candidates = []

    def race(publisher, tip, shared):
        candidates.append(tip)
        if len(candidates) == 1:
            if race_kind == "policy":
                settings = (topology.code / ".aitm.toml").read_bytes()
                commit_file(
                    topology.code,
                    ".aitm.toml",
                    settings.replace(b"uv run pytest", b"uv run ruff"),
                )
                git(topology.code, "push", "-q", "origin", DEFAULT)
            result = invoke_describe(other, tmp_path / "other", story=other_story)
            assert loads(result.stdout)["publication"] == "verified", result.stdout
        original_push(publisher, tip, shared)
        if len(candidates) == 1:
            assert git(remote, "rev-parse", PLANNING) != tip

    monkeypatch.setattr(Publisher, "_push", race)
    monkeypatch.chdir(topology.local)
    if race_kind in {"related", "disjoint"}:
        from aitm_core.cli import describe as adapter

        build = adapter.describe
        related = ReadExpectation(
            path=story_event_path(other_story),
            digest=sha256(dumps(second_seed).encode() + b"\n").hexdigest(),
        )

        def read_related(target, fields):
            request = build(target, fields)
            if race_kind == "disjoint":
                return request.model_copy(
                    update={"pending_actions": ("deferred-provider-action",)}
                )
            return request.model_copy(
                update={
                    "change": request.change.model_copy(
                        update={"read_set": (*request.change.read_set, related)}
                    ),
                    "intent": request.intent.model_copy(
                        update={
                            "related_preconditions": (
                                *request.intent.related_preconditions,
                                related,
                            )
                        }
                    ),
                }
            )

        monkeypatch.setattr(adapter, "describe", read_related)
    result = handle(("describe",), describe_args(topology, tmp_path / "primary"))
    assert result.local == "completed", result.evidence
    ran = len(candidates)
    if race_kind != "disjoint":
        assert ran == 1
        assert result.publication == PublicationOutcome.PENDING
        assert result.recovery
        assert any("Publication conflict" in line for line in result.evidence)
        if race_kind == "policy":
            assert any("policy changed" in line for line in result.evidence)
        else:
            assert any("read-set-changed" in line for line in result.evidence)
        assert git(topology.local, "rev-parse", result.recovery) == candidates[0]
        assert git(remote, "rev-parse", PLANNING) == other.writer()
        retry = retry_publication(topology.policy.installation, result.operation_id)
        assert retry.local == "completed", retry.evidence
        assert retry.publication == "pending"
        resolved = reconcile(
            topology.policy.installation,
            result.operation_id,
            Resolution(candidates[0], other.writer()),
        )
        assert resolved.command.local == "completed", resolved.reason
        assert resolved.command.publication == "not-applicable"
        assert topology.writer() == other.writer()
        assert git(topology.local, "rev-parse", result.recovery) == candidates[0]
        if race_kind == "authored":
            installation = topology.policy.installation
            publisher = Publisher(installation)
            original = publisher.request(result.operation_id)
            repo = installation.repository
            authority = preflight_policy(installation).policy
            blobs = repo.read_blobs(repo.tip().tree, (EVENTS, DESCRIPTION))
            replacement = describe(
                DescriptionTarget(
                    16,
                    blobs,
                    original.owner,
                    authority.source.digest,
                    "explicit-replacement",
                    "2026-11-27T19:00:00Z",
                ),
                DescriptionInput(
                    title="Resolved content",
                    actor="operator",
                    want="the retained choice",
                    so_that="it is audited",
                    scope="Use the explicit replacement.",
                ),
            )
            ports = ServicePorts(
                write_authorization=lambda *_: WriteAuthorization(
                    allowed=True, origin=AuthorityOrigin.FIXTURE
                )
            )
            applied = reconcile(
                installation,
                result.operation_id,
                Resolution(candidates[0], other.writer(), replacement),
                ports=ports,
            )
            assert applied.command.local == "completed", applied.reason
            assert applied.command.publication == "verified"
            assert publisher.request(replacement.operation_id) == replacement
            lineage = loads(
                repo._git(
                    "cat-file", "blob", publisher._lineage_ref(replacement.operation_id)
                )
            )
            assert lineage["original_request"] == original.request_digest
            assert lineage["replacement_request"] == replacement.request_digest
            assert lineage["retained_revision"] == candidates[0]
        return

    assert ran == 2
    assert result.pending == ("deferred-provider-action",)
    assert result.publication == PublicationOutcome.VERIFIED
    assert (
        candidates[0]
        in git(
            topology.local,
            "for-each-ref",
            "--format=%(objectname)",
            "refs/aitm/recovery",
        ).splitlines()
    )
    assert git(remote, "rev-parse", PLANNING) == candidates[1]
    repo = Repository(topology.local, PLANNING)
    pub = Publisher(topology.policy.installation)
    request = pub.request(result.operation_id)
    assert pub.record(repo.tip(), request).command.pending == (
        "deferred-provider-action",
    )
    events = repo.read_blobs(repo.tip().tree, (EVENTS, story_event_path(other_story)))
    for event_stream in events.values():
        assert (
            fold(event_stream.splitlines(keepends=True), core_reducers())
            .domains["lifecycle"]
            .description.title
            == "Read the store"
        )


@pytest.mark.parametrize("pushed", [True, False])
def test_installed_describe_observes_a_lost_ack(topology, tmp_path, pushed):
    topology.advance_planning(EVENTS, graduated())
    shim = tmp_path / "shim"
    shim.mkdir()
    git_path = which("git")
    assert git_path is not None
    log = tmp_path / "commands"
    wrapper = shim / "git"
    injection = f'{quote(git_path)} "$@"\n    exit 69' if pushed else "exit 69"
    wrapper.write_text(
        f"""#!/bin/sh
if [ "$3" = push ]; then
    printf 'push\\n' >> {quote(str(log))}
    {injection}
fi
if [ "$3" = ls-remote ]; then printf 'observe\\n' >> {quote(str(log))}; fi
exec {quote(git_path)} "$@"
"""
    )
    wrapper.chmod(0o755)
    environment = dict(environ, PATH=f"{shim}:{environ['PATH']}")
    executed = invoke_describe(topology, tmp_path, environment=environment)
    result = loads(executed.stdout)
    assert result["local"] == "completed", executed.stdout
    assert result["publication"] == ("verified" if pushed else "pending")
    commands = log.read_text().splitlines()
    assert commands.count("push") == 1
    assert "observe" in commands[commands.index("push") + 1 :]
    if not pushed:
        publisher = Publisher(topology.policy.installation)
        request_ref = publisher._request_ref(result["operation_id"])
        original = git(topology.local, "rev-parse", request_ref)
        raw = loads(git(topology.local, "cat-file", "blob", request_ref))
        raw["change"]["read_set"] = []
        corrupt = git(
            topology.local, "hash-object", "-w", "--stdin", data=dumps(raw).encode()
        )
        git(topology.local, "update-ref", request_ref, corrupt, original)
        refused = publisher.publish(result["operation_id"])
        assert refused.status == "conflict", refused
        assert refused.local_completed and refused.recovery_ref
        git(topology.local, "update-ref", request_ref, original, corrupt)
        retried = publisher.publish(result["operation_id"])
        assert retried.status == "published", retried
