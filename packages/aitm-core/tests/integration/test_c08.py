"""Exercise the refresh adapter through real independent Git repositories."""

import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from json import dumps, loads
from pathlib import Path
from threading import Event
from uuid import uuid4

import pytest

from aitm_core.config import resolve_policy
from aitm_core.models.common import LocalOutcome
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness, RefreshPolicy, cached_refs, refresh_refs
from aitm_core.store.objects import Repository
from aitm_core.store.validation import ValidationReport
from tests.support.c07 import (
    DEFAULT,
    PLANNING,
    WORKFLOW,
    WORKFLOW_BYTES,
    installation,
    settings_at,
)

CODE_REMOTE = "code-source"
PLANNING_REMOTE = "planning-source"


def git(root, *args, data=None):
    result = subprocess.run(
        ("git", "-C", str(root), *args), input=data, capture_output=True, check=True
    )
    return result.stdout.decode().strip()


def identify(root):
    git(root, "config", "user.name", "C08 fixture")
    git(root, "config", "user.email", "fixture@example.invalid")


def empty_planning_root(root, message="aitm-planning-root: v1"):
    tree = git(root, "mktree", data=b"")
    return git(root, "commit-tree", tree, "-m", message)


def commit_file(root, path, content):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    git(root, "add", path)
    git(root, "commit", "-qm", f"Update {path}")
    return git(root, "rev-parse", "HEAD")


def configured_settings(genesis):
    return (
        settings_at(genesis)
        .replace("[store]", f'[store]\nremote = "{PLANNING_REMOTE}"')
        .replace('trunk = "trunk"', f'trunk = "{CODE_REMOTE}/trunk"')
    )


@dataclass
class Topology:
    local: Path
    code: Path
    planning: Path
    policy: RefreshPolicy
    genesis: str
    old_code: str

    @property
    def common(self):
        return Path(
            git(self.local, "rev-parse", "--path-format=absolute", "--git-common-dir")
        )

    def writer(self):
        return git(self.local, "rev-parse", PLANNING)

    def advance_planning(self, path=".aitm/README.md", content=b"planning-data"):
        revision = commit_file(self.planning, path, content)
        git(self.planning, "push", "-q", "origin", f"HEAD:{PLANNING}")
        return revision


@pytest.fixture
def topology(tmp_path):
    local = tmp_path / "local"
    local.mkdir()
    git(local, "init", "-q", "-b", "trunk")
    identify(local)
    genesis = empty_planning_root(local)
    git(local, "update-ref", PLANNING, genesis)
    (local / ".aitm.toml").write_text(configured_settings(genesis))
    workflow = local / WORKFLOW
    workflow.parent.mkdir(parents=True)
    workflow.write_bytes(WORKFLOW_BYTES)
    git(local, "add", ".aitm.toml", WORKFLOW)
    git(local, "commit", "-qm", "Configure trusted code policy")
    old_code = git(local, "rev-parse", DEFAULT)

    clones = {}
    for remote, ref in ((CODE_REMOTE, DEFAULT), (PLANNING_REMOTE, PLANNING)):
        bare = tmp_path / f"{remote}.git"
        bare.mkdir()
        git(bare, "init", "-q", "--bare")
        git(local, "remote", "add", remote, str(bare))
        git(local, "push", "-q", remote, f"{ref}:{ref}")
        clone = tmp_path / remote
        git(
            tmp_path,
            "clone",
            "-q",
            "-b",
            ref.removeprefix("refs/heads/"),
            str(bare),
            str(clone),
        )
        identify(clone)
        clones[remote] = clone

    anchor = installation(Repository(local, PLANNING), genesis)
    landed = replace(
        anchor,
        store=anchor.store.model_copy(update={"planning_remote": PLANNING_REMOTE}),
        code_remote=CODE_REMOTE,
        code_remote_ref=DEFAULT,
    )
    return Topology(
        local,
        clones[CODE_REMOTE],
        clones[PLANNING_REMOTE],
        RefreshPolicy(landed),
        genesis,
        old_code,
    )


def test_refreshes_anchored_code_and_planning_from_separate_exact_refs(topology):
    updated_code = commit_file(
        topology.code,
        ".aitm.toml",
        configured_settings(topology.genesis)
        .replace("uv run pytest", "uv run ruff")
        .encode(),
    )
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    valid_planning = topology.advance_planning()
    git(topology.local, "switch", "-qc", "story")
    (topology.local / ".aitm.toml").write_text("story override")
    originals = git(
        topology.local,
        "for-each-ref",
        "--format=%(refname) %(objectname)",
        "refs/remotes",
    )
    fetch_head = topology.common / "FETCH_HEAD"
    fetch_head.write_bytes(b"unrelated caller fetch\n")

    result = refresh_refs(topology.policy)

    assert result.code_freshness is Freshness.FRESH
    assert (result.local.ref, result.local.remote, result.local.observed_commit) == (
        DEFAULT,
        CODE_REMOTE,
        updated_code,
    )
    assert result.shared.status is ContinuityStatus.VERIFIED
    assert result.shared.checkpoint == result.shared.valid_tip == valid_planning
    assert result.planning.observed_commit == topology.writer() == valid_planning
    assert (
        resolve_policy(topology.policy.installation, result).config.test.command
        == "uv run ruff"
    )
    assert git(topology.local, "rev-parse", DEFAULT) == topology.old_code
    assert (
        git(
            topology.local,
            "for-each-ref",
            "--format=%(refname) %(objectname)",
            "refs/remotes",
        )
        == originals
    )
    assert fetch_head.read_bytes() == b"unrelated caller fetch\n"
    assert (topology.local / ".aitm.toml").read_text() == "story override"

    # The next shared advance cannot reset unpublished work on the local
    # planning writer, even when both branches share the admitted frontier.
    tree = git(topology.local, "rev-parse", f"{valid_planning}^{{tree}}")
    unpublished = git(
        topology.local,
        "commit-tree",
        tree,
        "-p",
        valid_planning,
        "-m",
        "Unpublished local planning",
    )
    git(topology.local, "update-ref", PLANNING, unpublished, valid_planning)
    latest = topology.advance_planning(content=b"published data on the shared branch")
    divergent = refresh_refs(topology.policy)
    assert divergent.shared.status is ContinuityStatus.VERIFIED
    assert divergent.shared.local_diverged
    assert divergent.shared.checkpoint == divergent.shared.valid_tip == latest
    assert divergent.planning.observed_commit == topology.writer() == unpublished

    rejected_code = commit_file(topology.code, ".aitm.toml", b"not a committed policy")
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
    assert rejected_code != updated_code
    refused = refresh_refs(topology.policy)
    assert refused.code_freshness is Freshness.FENCED
    assert refused.local.observed_commit == updated_code
    assert refused.planning.observed_commit == topology.writer() == unpublished
    assert refused.shared.fences_shared

    target = topology.policy.installation.validated_code_ref
    git(topology.local, "symbolic-ref", target, DEFAULT)
    invalid_cache = cached_refs(topology.policy)
    assert invalid_cache.code_freshness is Freshness.FENCED
    assert invalid_cache.local.observed_commit is None
    assert "must be direct" in invalid_cache.code_reason


def test_published_invalid_descendant_is_retained_as_checkpoint_without_moving_writer(
    topology,
):
    previous = topology.advance_planning()
    assert refresh_refs(topology.policy).shared.valid_tip == previous
    bad = topology.advance_planning("not-planning.py", b"not data")
    result = refresh_refs(topology.policy)
    assert result.shared.status is ContinuityStatus.QUARANTINED
    assert result.shared.checkpoint == bad
    assert result.shared.valid_tip == topology.writer() == previous
    assert result.recovery_ref is not None
    assert git(topology.local, "rev-parse", result.recovery_ref) == bad
    cached = cached_refs(topology.policy)
    assert cached.shared.status is ContinuityStatus.QUARANTINED
    assert cached.shared.checkpoint == bad

    # C08 consumes C06's forward verifier without granting a repair
    # producer. The same exact candidate is held before the slot is supplied.
    git(topology.planning, "rm", "-q", "not-planning.py")
    repair_path = ".aitm/repairs/fixture.json"
    repair_bytes = b'{"schema":"aitm.repair/v1"}'
    repaired = topology.advance_planning(repair_path, repair_bytes)
    lacking_verifier = refresh_refs(topology.policy)
    assert lacking_verifier.shared.status is ContinuityStatus.QUARANTINED
    assert lacking_verifier.shared.checkpoint == repaired
    assert lacking_verifier.shared.valid_tip == topology.writer() == previous

    def verify_repair(anchor, diagnosed, candidate):
        assert anchor == topology.policy.installation.store
        assert diagnosed.bad_tip.revision == bad
        assert diagnosed.valid_prefix.revision == previous
        assert candidate.revision == repaired
        assert topology.policy.installation.repository.read_blobs(
            candidate.tree,
            (repair_path, "not-planning.py"),
        ) == {repair_path: repair_bytes, "not-planning.py": None}
        return ValidationReport(LocalOutcome.COMPLETED, candidate.revision)

    verified = refresh_refs(
        replace(topology.policy, forward_repair_verifier=verify_repair)
    )
    assert verified.shared.status is ContinuityStatus.VERIFIED
    assert (
        verified.shared.valid_tip
        == verified.shared.checkpoint
        == topology.writer()
        == repaired
    )

    # A forced unrelated root with a familiar trailer cannot reset the checkpoint.
    other = empty_planning_root(
        topology.planning, "Unrelated root\n\naitm-planning-root: v1"
    )
    git(topology.planning, "push", "-q", "--force", "origin", f"{other}:{PLANNING}")
    unrelated = refresh_refs(topology.policy)
    assert unrelated.shared.status is ContinuityStatus.SIBLING
    assert unrelated.shared.checkpoint == repaired
    assert unrelated.shared.valid_tip == topology.writer() == repaired
    assert git(topology.local, "rev-parse", unrelated.recovery_ref) == other

    # Even a descendant of the retained checkpoint remains unusable if it
    # introduces the admitted code-default ancestry.
    tree = git(topology.local, "mktree", data=b"")
    connected = git(
        topology.local,
        "commit-tree",
        tree,
        "-p",
        repaired,
        "-p",
        topology.old_code,
        "-m",
        "Contains code ancestry",
    )
    git(
        topology.local,
        "push",
        "-q",
        "--force",
        PLANNING_REMOTE,
        f"{connected}:{PLANNING}",
    )
    unsafe = refresh_refs(topology.policy)
    assert (unsafe.shared.status, unsafe.shared.reason) == (
        ContinuityStatus.QUARANTINED,
        "code-ancestry",
    )
    assert unsafe.shared.checkpoint == connected
    assert unsafe.shared.valid_tip == topology.writer() == repaired
    assert git(topology.local, "rev-parse", unsafe.recovery_ref) == connected

    git(topology.planning, "push", "-q", "origin", f":{PLANNING}")
    deleted = refresh_refs(topology.policy)
    assert deleted.shared.status is ContinuityStatus.DELETED
    assert deleted.candidate.observed_commit is None
    assert deleted.shared.checkpoint == connected
    assert deleted.shared.valid_tip == topology.writer() == repaired


class Interrupted(RuntimeError):
    pass


@pytest.mark.parametrize("after_cas", [False, True])
def test_refresh_recovers_durable_journal_and_real_ref_transition(
    topology, monkeypatch, after_cas
):
    previous = topology.advance_planning()
    assert refresh_refs(topology.policy).planning.observed_commit == previous
    advanced = topology.advance_planning(content=b"new planning-data")
    old_git = Repository._git

    def intercept(repository, *args, data=None, index=None):
        if (
            args == ("update-ref", "--stdin")
            and data is not None
            and f"update {PLANNING} {advanced} {previous}\n".encode() in data
        ):
            if after_cas:
                old_git(repository, *args, data=data, index=index)
            raise Interrupted("leave the journal at the publication boundary")
        return old_git(repository, *args, data=data, index=index)

    with monkeypatch.context() as patch:
        patch.setattr(Repository, "_git", intercept)
        with pytest.raises(Interrupted, match="publication boundary"):
            refresh_refs(topology.policy)
    assert topology.writer() == (advanced if after_cas else previous)

    if not after_cas:
        # The unpublished journal tail can request replay, but its fields
        # cannot replace the retained established frontier.
        (journal,) = (topology.common / "aitm/continuity").glob("*.jsonl")
        original = journal.read_bytes()
        lines = original.splitlines(keepends=True)
        forged = loads(lines[-1])
        tree = git(topology.local, "rev-parse", f"{previous}^{{tree}}")
        sibling = git(
            topology.local,
            "commit-tree",
            tree,
            "-p",
            topology.genesis,
            "-m",
            "Content-valid sibling",
        )
        forged["frontier"]["checkpoint"] = sibling
        forged["frontier"]["valid_tip"] = sibling
        forged["frontier"]["observation"]["observed_commit"] = sibling
        forged["writer_after"] = sibling
        forged["transport_ref"] = f"refs/aitm/candidates/planning-{uuid4().hex}"
        git(topology.local, "update-ref", forged["transport_ref"], sibling)
        journal.write_bytes(b"".join(lines[:-1]) + dumps(forged).encode() + b"\n")
        held = refresh_refs(topology.policy)
        assert held.shared.fences_shared
        assert "independent retained evidence" in held.shared.reason
        assert topology.writer() == previous
        journal.write_bytes(original)

    recovered = refresh_refs(topology.policy)
    assert recovered.shared.status is ContinuityStatus.VERIFIED
    assert recovered.shared.checkpoint == recovered.shared.valid_tip == advanced
    assert recovered.planning.observed_commit == topology.writer() == advanced

    (journal,) = (topology.common / "aitm/continuity").glob("*.jsonl")
    if after_cas:
        journal.unlink()
        diagnostic = "missing while retained refs exist"
    else:
        with journal.open("ab") as writer:
            writer.write(b'{"partially-written":')
        diagnostic = "partial record"

    later = topology.advance_planning(content=b"must remain unadmitted")
    assert later != advanced
    assert diagnostic in cached_refs(topology.policy).shared.reason
    fenced = refresh_refs(topology.policy)
    assert fenced.shared.fences_shared and diagnostic in fenced.shared.reason
    assert fenced.planning.observed_commit == topology.writer() == advanced


def test_out_of_band_checkout_after_precheck_fences_and_preserves_worktree(
    topology, monkeypatch, tmp_path
):
    previous = topology.advance_planning()
    assert refresh_refs(topology.policy).planning.observed_commit == previous
    advanced = topology.advance_planning(content=b"advanced planning-data")
    checkout = tmp_path / "interference"
    old_git = Repository._git
    witnessed = {}

    def check_out_during_cas(repository, *args, data=None, index=None):
        if (
            args == ("update-ref", "--stdin")
            and data is not None
            and f"update {PLANNING} {advanced} {previous}\n".encode() in data
        ):
            git(topology.local, "worktree", "add", "-q", str(checkout), "records")
            path = checkout / ".aitm/README.md"
            path.write_bytes(b"unsynced author edit")
            worktree_index = Path(
                git(
                    checkout,
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-path",
                    "index",
                )
            )
            witnessed.update(index=worktree_index, contents=worktree_index.read_bytes())
        return old_git(repository, *args, data=data, index=index)

    monkeypatch.setattr(Repository, "_git", check_out_during_cas)
    result = refresh_refs(topology.policy)
    assert result.shared.fences_shared
    assert "checkout" in result.shared.reason.lower()
    assert topology.writer() == advanced
    assert (checkout / ".aitm/README.md").read_bytes() == b"unsynced author edit"
    assert witnessed["index"].read_bytes() == witnessed["contents"]
    recovery = git(
        topology.local, "for-each-ref", "--format=%(objectname)", "refs/aitm/recovery"
    )
    assert {previous, advanced}.issubset(recovery.splitlines())
    assert cached_refs(topology.policy).shared.fences_shared


def test_refresh_discards_in_flight_candidate_after_other_refresh_admits_new_frontier(
    topology, monkeypatch
):
    first = topology.advance_planning()
    assert refresh_refs(topology.policy).planning.observed_commit == first
    stale = topology.advance_planning(content=b"will be superseded while fetching")
    captured = Event()
    resume = Event()
    old_run = Repository._run

    def delay_first_planning_fetch(repository, *args, data=None, index=None):
        result = old_run(repository, *args, data=data, index=index)
        if (
            "fetch" in args
            and args[-1].startswith(f"+{PLANNING}:")
            and not captured.is_set()
        ):
            captured.set()
            assert resume.wait(25), (
                "refresh was unable to run while the other fetch was in flight"
            )
        return result

    monkeypatch.setattr(Repository, "_run", delay_first_planning_fetch)
    with ThreadPoolExecutor(max_workers=2) as workers:
        delayed = workers.submit(refresh_refs, topology.policy)
        try:
            assert captured.wait(20)
            latest = topology.advance_planning(content=b"more recent shared data")
            admitted = workers.submit(refresh_refs, topology.policy).result(timeout=20)
            assert admitted.shared.status is ContinuityStatus.VERIFIED
            assert admitted.planning.observed_commit == latest
        finally:
            resume.set()
        replayed = delayed.result(timeout=20)

    assert replayed.shared.status is ContinuityStatus.VERIFIED
    assert replayed.planning.observed_commit == topology.writer() == latest
    (journal,) = (topology.common / "aitm/continuity").glob("*.jsonl")
    assert len(journal.read_bytes().splitlines()) == 2
    assert stale.encode() not in journal.read_bytes()
