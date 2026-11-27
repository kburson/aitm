import hashlib
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from uuid import UUID

import pytest
from pinned_evidence_fixture import pinned_evidence as pinned_evidence

from aitm_usage.effort import session_publication as publication
from aitm_usage.effort.receipts import Outcome, Role, TimeBasis, UsageScope
from aitm_usage.effort.session import PublicReceipt
from aitm_usage.effort.session_publication import PublicationEntry, publish_receipts
from aitm_usage.types import Availability, TokenCounts, _encode

PROJECT = UUID("526d9fbd-6e2d-4535-8dd1-2a5daa6d60e7")
STORY = ".aitm/stories/004/457"
PLANNING = "refs/heads/planning"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


@pytest.fixture
def repo_pair(tmp_path):
    remote = tmp_path / "remote.git"
    checkout = tmp_path / "checkout"
    remote.mkdir()
    checkout.mkdir()
    git(remote, "init", "--bare")
    git(checkout, "init", "-b", "planning")
    git(checkout, "config", "user.email", "test@example.invalid")
    git(checkout, "config", "user.name", "AITM test")
    git(checkout, "remote", "add", "origin", str(remote))
    for story in (457, 458):
        path = checkout / f".aitm/stories/004/{story}"
        path.mkdir(parents=True)
        (path / "story.md").write_text(f'---\nid: {story}\ntitle: "test"\n---\n')
    git(checkout, "add", ".aitm")
    git(checkout, "commit", "-m", "planning fixture")
    git(checkout, "push", "origin", f"{PLANNING}:{PLANNING}")
    git(checkout, "switch", "-c", "work")
    return checkout, remote


def receipt(identity="a" * 64, *, revision=1, story=457, marker="one", previous=None):
    payload = PublicReceipt(
        schema="aitm.session-turn/v1",
        project=PROJECT,
        story=story,
        identity=identity,
        revision=revision,
        attempt="5" * 64,
        role=Role.WORKER,
        provider="codex",
        version="0.171.0-alpha.13.2",
        surface="desktop",
        observed_at=datetime(2026, 11, 25, tzinfo=UTC),
        started_at=None,
        ended_at=None,
        time_basis=TimeBasis.UNKNOWN,
        coverage=Availability.UNKNOWN,
        outcome=Outcome.UNKNOWN,
        usage_scope=UsageScope.BOUNDED,
        tokens=TokenCounts(),
        evidence_sha256=hashlib.sha256(marker.encode()).hexdigest(),
        previous_receipt_sha256=previous,
        model=None,
        rate_inputs=None,
        reported_grok_usd_ticks=None,
        grok_cache_creation_tokens=None,
    )
    return PublicationEntry(
        story, identity, revision, _encode(payload, PublicReceipt).encode()
    )


def test_publishes_once_without_touching_worktree(repo_pair):
    checkout, remote = repo_pair
    (checkout / STORY / "story.md").write_text("uncommitted local edit\n")
    before = git(checkout, "status", "--porcelain=v1")
    item = receipt()
    tip = publish_receipts(checkout, str(remote), PROJECT, [item])
    assert git(remote, "rev-parse", PLANNING) == tip
    content = git(remote, "show", f"{PLANNING}:{item.path}")
    assert content.encode() == item.data
    assert publish_receipts(checkout, str(remote), PROJECT, [item]) == tip
    assert git(checkout, "status", "--porcelain=v1") == before
    assert git(checkout, "branch", "--show-current") == "work"
    assert git(checkout, "for-each-ref", "refs/aitm/session-publication") == ""

    second = receipt(revision=2, previous=hashlib.sha256(item.data).hexdigest())
    tip = publish_receipts(checkout, str(remote), PROJECT, [second])
    for landed in (item, second):
        assert git(remote, "show", f"{tip}:{landed.path}").encode() == landed.data

    with pytest.raises(ValueError, match="conflicting immutable"):
        publish_receipts(
            checkout,
            str(remote),
            PROJECT,
            [receipt("b" * 64), receipt(marker="conflict")],
        )
    assert git(remote, "rev-parse", PLANNING) == tip


def test_conflict_refuses_the_entire_batch_before_publication(planning_tree):
    first = receipt()
    planning_tree.write(first.path, first.data)
    tip = planning_tree.pin()
    tree = publication._PlanningTree(planning_tree, tip)
    with pytest.raises(ValueError, match="conflicting immutable"):
        tree.missing(
            publication._validated_batch(
                PROJECT, [receipt("b" * 64), receipt(marker="conflict")]
            )
        )


def test_refuses_mismatched_identity_project_and_remote(repo_pair, tmp_path):
    checkout, remote = repo_pair
    tip = git(remote, "rev-parse", PLANNING)
    item = receipt()
    wrong_fields = PublicationEntry(457, "b" * 64, 1, item.data)
    with pytest.raises(ValueError, match="scope"):
        publish_receipts(checkout, str(remote), PROJECT, [wrong_fields])
    with pytest.raises(ValueError, match="scope"):
        publish_receipts(checkout, str(remote), UUID(int=1), [item])
    git(checkout, "remote", "set-url", "--push", "origin", str(tmp_path / "other.git"))
    with pytest.raises(ValueError, match="remote"):
        publish_receipts(checkout, str(remote), PROJECT, [item])
    assert git(remote, "rev-parse", PLANNING) == tip


def test_refuses_missing_story_and_symlinked_tree(repo_pair):
    checkout, remote = repo_pair
    with pytest.raises(ValueError, match="story"):
        publish_receipts(checkout, str(remote), PROJECT, [receipt(story=459)])
    git(checkout, "switch", "planning")
    (checkout / STORY / "attachments").symlink_to("elsewhere")
    git(checkout, "add", ".aitm")
    git(checkout, "commit", "-m", "conflicting entry type")
    git(checkout, "push", "origin", f"{PLANNING}:{PLANNING}")
    tip = git(remote, "rev-parse", PLANNING)
    with pytest.raises(ValueError, match="tree"):
        publish_receipts(checkout, str(remote), PROJECT, [receipt()])
    assert git(remote, "rev-parse", PLANNING) == tip


def test_recovers_remote_acceptance_after_lost_push_ack(repo_pair, monkeypatch):
    checkout, remote = repo_pair
    real_run = publication._git

    def lose_ack(repo, *args, **kwargs):
        result = real_run(repo, *args, **kwargs)
        if args[0] == "push" and result.returncode == 0:
            return subprocess.CompletedProcess(result.args, 1, b"", b"lost ack")
        return result

    monkeypatch.setattr(publication, "_git", lose_ack)
    item = receipt()
    tip = publish_receipts(checkout, str(remote), PROJECT, [item])
    assert git(remote, "rev-parse", PLANNING) == tip
    assert git(remote, "show", f"{tip}:{item.path}").encode() == item.data


def test_concurrent_writers_keep_both_disjoint_receipts(repo_pair, monkeypatch):
    checkout, remote = repo_pair
    first_push = Barrier(2, timeout=15)
    real_run = publication._git
    tries = set()

    def overlap_pushes(repo, *args, **kwargs):
        if args[0] == "push" and args[-1] not in tries and len(tries) < 2:
            tries.add(args[-1])
            first_push.wait()
        return real_run(repo, *args, **kwargs)

    monkeypatch.setattr(publication, "_git", overlap_pushes)
    items = [receipt(), receipt("b" * 64)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        sends = [
            pool.submit(publish_receipts, checkout, str(remote), PROJECT, [item])
            for item in items
        ]
        for future in sends:
            future.result()
    tip = git(remote, "rev-parse", PLANNING)
    for item in items:
        assert git(remote, "show", f"{tip}:{item.path}").encode() == item.data


@pytest.fixture
def planning_tree(pinned_evidence, monkeypatch):
    from types import SimpleNamespace

    evidence = pinned_evidence(STORY, 457)

    def read(repo, *args):
        return evidence.response(
            SimpleNamespace(repository=repo, commit=next(reversed(evidence.commits))),
            *args,
            limit=2 * 1024 * 1024,
        )

    monkeypatch.setattr(publication, "_read", read)
    return evidence


def test_observation_cannot_move_to_another_story_in_later_revision(planning_tree):
    first = receipt()
    planning_tree.write(first.path, first.data)
    tip = planning_tree.pin()
    tree = publication._PlanningTree(planning_tree, tip)
    predecessor = hashlib.sha256(first.data).hexdigest()
    moved = receipt(story=458, revision=2, previous=predecessor)
    with pytest.raises(ValueError, match="another story"):
        tree.missing(publication._validated_batch(PROJECT, [moved]))


def test_revision_requires_its_exact_public_predecessor(planning_tree):
    first = receipt()
    second = receipt(revision=2, previous=hashlib.sha256(first.data).hexdigest())
    wrong_root = receipt(marker="wrong")
    tip = planning_tree.pin()
    tree = publication._PlanningTree(planning_tree, tip)
    with pytest.raises(ValueError, match="predecessor"):
        tree.missing(publication._validated_batch(PROJECT, [second]))
    with pytest.raises(ValueError, match="predecessor"):
        tree.missing(publication._validated_batch(PROJECT, [wrong_root, second]))
    assert tree.missing(publication._validated_batch(PROJECT, [second, first])) == [
        second,
        first,
    ]


def test_policy_refusal_retains_remote_and_bounds_pushes(repo_pair, monkeypatch):
    checkout, remote = repo_pair
    real_run = publication._git
    pushes = []

    def refuse(repo, *args, **kwargs):
        if args[0] == "push":
            pushes.append(args)
            return subprocess.CompletedProcess(args, 1, b"", b"policy refused")
        return real_run(repo, *args, **kwargs)

    monkeypatch.setattr(publication, "_git", refuse)
    tip = git(remote, "rev-parse", PLANNING)
    with pytest.raises(publication.PublicationHold, match="unverified"):
        publish_receipts(checkout, str(remote), PROJECT, [receipt()])
    assert len(pushes) == 3
    assert git(remote, "rev-parse", PLANNING) == tip
