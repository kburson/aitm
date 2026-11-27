"""Exercise the real planning-history validator and clone-wide ref gate."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from threading import Event

import pytest

from aitm_core.models.common import LocalOutcome, StoreAnchor
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
)
from aitm_core.services import ServicePorts, backend
from aitm_core.store.gate import (
    COOPERATIVE_LIMIT,
    RefIdentity,
    RefMutationKind,
    ref_gate,
)
from aitm_core.store.git_backend import ValidationRejected
from aitm_core.store.objects import Repository
from aitm_core.store.validation import (
    validate_history,
)

REF = "refs/heads/planning"
DEFAULT = "refs/heads/trunk"
README = ".aitm/README.md"
OUTSIDE = "outside.txt"
OWNER = OperationOwner(actor=EventActor(kind="agent", harness="fixture"))


def git(root, *args, data=None):
    return subprocess.run(
        ("git", "-C", str(root), *args),
        input=data,
        check=True,
        capture_output=True,
    ).stdout.strip()


@pytest.fixture
def store(tmp_path):
    root = tmp_path / "clone"
    root.mkdir()
    git(root, "init", "-q", "-b", "trunk")
    git(root, "config", "user.name", "AITM history fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    (root / "code.txt").write_text("code default\n")
    git(root, "add", "code.txt")
    git(root, "commit", "-qm", "Code root")
    tree = git(root, "mktree", data=b"").decode()
    genesis = git(root, "commit-tree", tree, "-m", "aitm-planning-root: v1").decode()
    git(root, "update-ref", REF, genesis)
    repo = Repository(root, REF)
    anchor = StoreAnchor(
        store_uuid="c06-fixture",
        code_default_ref=DEFAULT,
        planning_ref=REF,
        planning_remote=None,
        root_commit=genesis,
    )
    return repo, anchor


def allow_fixture(owner, change):
    assert owner == OWNER
    assert isinstance(change, RelatedWriteSet)
    return WriteAuthorization(allowed=True, origin=AuthorityOrigin.FIXTURE)


PORTS = ServicePorts(write_authorization=allow_fixture)


def operation(store_backend, snapshot, path, value=b"new"):
    current = store_backend.read(snapshot, (path,))[path]
    digest = sha256(current).hexdigest() if current is not None else None
    return Operation(
        operation_id=f"c06-{sha256(path.encode() + value).hexdigest()[:16]}",
        owner=OWNER,
        category=OperationCategory.NORMAL,
        policy_digest="a" * 64,
        intent=FinalizationIntent(
            kind="store.fixture", version=1, related_preconditions=(), payload=b"{}"
        ),
        change=RelatedWriteSet(
            read_set=(ReadExpectation(path=path, digest=digest),),
            writes=(BlobWrite(path=path, content=value),),
        ),
    )


def candidate_with_mode(repo, before, mode, path):
    content = (
        git(repo.root, "rev-parse", DEFAULT).decode()
        if mode == "160000"
        else git(
            repo.root, "hash-object", "-w", "--stdin", data=b"text fixture"
        ).decode()
    )
    index = repo.root / ".git" / "fixture-index"
    repo._git("read-tree", before.tree, index=index)
    repo._git("update-index", "--add", "--cacheinfo", mode, content, path, index=index)
    tree = repo._git("write-tree", index=index).strip().decode()
    return git(
        repo.root, "commit-tree", tree, "-p", before.revision, "-m", "Fixture"
    ).decode()


def test_store_gate(store, tmp_path):
    repo, anchor = store
    start = repo.tip()
    safe = backend(repo, anchor, ports=PORTS)
    good = safe.transact(operation(safe, start, README, b"# Planning data\n"), start)
    assert good.command.local == LocalOutcome.COMPLETED
    assert (
        validate_history(anchor, good.snapshot.revision, repository=repo).outcome
        == LocalOutcome.COMPLETED
    )

    bad = safe.transact(operation(safe, good.snapshot, OUTSIDE), good.snapshot)
    assert bad.command.local == LocalOutcome.INTEGRITY_ERROR
    assert OUTSIDE in bad.reason
    assert repo.tip() == good.snapshot

    proposed = repo.create_commit(good.snapshot, {OUTSIDE: b"invalid"}, "outside")
    config = tmp_path / "trusted-anchor.json"
    config.write_text(anchor.model_dump_json())
    tool = Path(sys.executable).parent / "aitm"
    run = subprocess.run(
        (
            str(tool),
            "--json",
            "planning",
            "validate",
            "--anchor",
            str(config),
            "--tip",
            proposed.revision,
        ),
        cwd=repo.root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 3
    result = json.loads(run.stdout)
    assert result["local"] == "integrity-error"
    assert any(OUTSIDE in evidence for evidence in result["evidence"])
    assert repo.tip() == good.snapshot


@pytest.mark.parametrize(
    ("mode", "path"),
    [
        ("120000", README),
        ("160000", ".aitm/attachments/submodule"),
        ("100755", README),
    ],
)
def test_tree_rejects_non_data_objects(store, mode, path):
    repo, anchor = store
    candidate = candidate_with_mode(repo, repo.tip(), mode, path)
    result = validate_history(anchor, candidate, repository=repo)
    assert result.outcome == LocalOutcome.INTEGRITY_ERROR
    assert path in result.reason


def test_root_lineage_and_code_ancestry_guards(store):
    repo, anchor = store
    start = repo.tip()
    current_code = git(repo.root, "rev-parse", DEFAULT).decode()
    assert (
        validate_history(anchor, current_code, repository=repo).reason
        == "code-ancestry"
    )

    valid = repo.create_commit(start, {README: b"ordinary"}, "valid")
    sibling = repo.create_commit(start, {README: b"other"}, "sibling")
    merged = git(
        repo.root,
        "commit-tree",
        valid.tree,
        "-p",
        valid.revision,
        "-p",
        sibling.revision,
        "-m",
        "Merge",
    ).decode()
    assert (
        validate_history(anchor, merged, repository=repo).outcome
        == LocalOutcome.INTEGRITY_ERROR
    )

    nonempty = git(
        repo.root, "commit-tree", valid.tree, "-m", "aitm-planning-root: v1"
    ).decode()
    anchored_nonempty = anchor.model_copy(update={"root_commit": nonempty})
    assert (
        validate_history(anchored_nonempty, nonempty, repository=repo).reason
        == "nonempty-planning-root"
    )

    alien = git(repo.root, "commit-tree", start.tree, "-m", "other root").decode()
    anchored_alien = anchor.model_copy(update={"root_commit": alien})
    assert (
        validate_history(anchored_alien, alien, repository=repo).reason
        == "planning-root-marker-missing"
    )
    assert (
        validate_history(anchor, alien, repository=repo).reason
        == "planning-root-mismatch"
    )


def test_repair_requires_the_explicit_verifier_slot(store):
    repo, anchor = store
    start = repo.tip()
    bad = repo.create_commit(start, {OUTSIDE: b"invalid"}, "invalid")
    repaired = repo.create_commit(
        bad,
        {
            OUTSIDE: None,
            ".aitm/repairs/fixture.json": b'{"schema":"aitm.forward-repair/v1"}',
        },
        "repair",
    )

    def unneeded_verifier(_anchor, _diagnosis, _candidate):
        pytest.fail("absent repair slot must remain absent")

    explicit = replace(
        ServicePorts(forward_repair_verifier=unneeded_verifier),
        forward_repair_verifier=None,
    )
    view = backend(repo, anchor, ports=explicit)
    result = validate_history(
        anchor,
        repaired.revision,
        repository=repo,
        forward_repair_verifier=explicit.forward_repair_verifier,
    )
    assert view.snapshot() == start
    assert result.outcome == LocalOutcome.UNAVAILABLE
    assert result.reason == "forward-repair-verifier-unavailable"
    assert result.first_invalid == bad.revision
    assert result.valid_prefix == start.revision


def test_checked_out_target_refuses_writes_but_review_ref_is_distinct(store, tmp_path):
    repo, anchor = store
    review = tmp_path / "review"
    git(repo.root, "worktree", "add", "-qb", "review", str(review), repo.tip().revision)
    safe = backend(repo, anchor, ports=PORTS)
    start = safe.snapshot()
    result = safe.transact(operation(safe, start, README), start)
    assert result.command.local == LocalOutcome.COMPLETED

    planning = tmp_path / "planning"
    git(repo.root, "worktree", "add", "-q", str(planning), "planning")
    locked = safe.snapshot()
    refused = safe.transact(operation(safe, locked, README, b"retry"), locked)
    assert refused.command.local == LocalOutcome.INTEGRITY_ERROR
    assert "checked out" in refused.reason
    assert COOPERATIVE_LIMIT in refused.reason
    assert safe.snapshot() == locked


def test_clone_lock_serializes_distinct_ref_purposes(store):
    repo, _ = store
    entered = Event()
    alternate = "refs/heads/candidate"
    git(repo.root, "branch", "candidate", repo.tip().revision)

    def other_target():
        with ref_gate(repo, RefIdentity(alternate), RefMutationKind.DELIVERY):
            entered.set()

    with ThreadPoolExecutor(max_workers=1) as worker:
        with ref_gate(repo, RefIdentity(REF), RefMutationKind.PLANNING):
            result = worker.submit(other_target)
            assert not entered.wait(0.1)
        assert entered.wait(5)
        result.result(timeout=5)


def test_external_checkout_fences_publication_and_preserves_bytes(
    store, tmp_path, monkeypatch
):
    repo, anchor = store
    safe = backend(repo, anchor, ports=PORTS)
    start = safe.snapshot()
    request = operation(safe, start, README)
    update = Repository.compare_and_swap
    checkout = tmp_path / "external"
    retained = {}

    def checkout_during_cas(repository, new, expected):
        git(repo.root, "worktree", "add", "-q", str(checkout), "planning")
        (checkout / "user.txt").write_bytes(b"staged user bytes")
        git(checkout, "add", "user.txt")
        index = Path(
            git(
                checkout, "rev-parse", "--path-format=absolute", "--git-path", "index"
            ).decode()
        )
        retained["index"] = index
        retained["before"] = index.read_bytes()
        (checkout / "user.txt").write_bytes(b"unsynced user bytes")
        return update(repository, new, expected)

    with monkeypatch.context() as race:
        race.setattr(Repository, "compare_and_swap", checkout_during_cas)
        result = safe.transact(request, start)

    observed = safe.snapshot()
    assert result.command.local == LocalOutcome.INTEGRITY_ERROR
    assert result.command.pending == ()
    assert result.snapshot == observed
    assert COOPERATIVE_LIMIT in result.reason
    assert observed != start
    assert retained["index"].read_bytes() == retained["before"]
    assert (checkout / "user.txt").read_bytes() == b"unsynced user bytes"
    refs = git(
        repo.root, "for-each-ref", "--format=%(objectname)", "refs/aitm/recovery"
    )
    assert set(refs.decode().splitlines()) == {start.revision, observed.revision}
    with pytest.raises(ValidationRejected, match="fenced"):
        with ref_gate(repo, RefIdentity(REF), RefMutationKind.PLANNING):
            pytest.fail("fenced target cannot be admitted")


def test_delivery_validation_uses_its_own_content_check(store):
    repo, _ = store
    start = repo.tip()
    ref = "refs/heads/candidate"
    git(repo.root, "branch", "candidate", start.revision)
    candidate = repo.create_commit(
        start, {OUTSIDE: b"ordinary delivery content"}, "source"
    )
    checks = []

    def planning_only(_tip):
        pytest.fail("delivery target must use the content check for its own lane")

    def delivery(before, after):
        checks.append((before, after))

    with ref_gate(
        repo,
        RefIdentity(ref),
        RefMutationKind.DELIVERY,
        planning_validation=planning_only,
        delivery_validation=delivery,
    ) as guard:
        guard(start, candidate)

    assert checks == [(start, candidate)]
    assert repo.tip() == start
