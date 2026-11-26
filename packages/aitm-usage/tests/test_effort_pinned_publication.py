"""End-to-end boundaries for frozen report publication and the #181 Cost intake."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = "526d9fbd-6e2d-4535-8dd1-2a5daa6d60e7"
STORY = 458
STORY_ROOT = ".aitm/stories/004/458"
PLANNING = "refs/heads/planning"
START = "2026-11-25T16:00:00Z"
END = "2026-11-25T17:00:00Z"
CUTOFF = "2026-11-25T18:00:00Z"
RECORDED = "2026-11-25T19:00:00Z"
BASIS = "standard-api-equivalent"
REPO_ROOT = Path(__file__).resolve().parents[3]


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def oid(repo, ref="HEAD"):
    return git(repo, "rev-parse", ref).decode().strip()


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def commit(repo, message):
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return oid(repo)


def timing_registration(story):
    batch = "independent-timing"
    value = {
        "schema": "aitm.story-timing-receipt/v1",
        "project": "aitm",
        "subject": STORY,
        "batch": batch,
        "recorded_at_utc": RECORDED,
        "source": {"ref": "manual:independent-fixture"},
        "observations": [
            {
                "observation_id": "independent.turn-1",
                "actor": "agent-1",
                "turn": "turn-1",
                "phase": "implement",
                "role": "implementer",
                "attempt": "attempt-1",
                "kind": "agent-turn",
                "coverage": "complete",
                "basis": "verified-turn-boundaries",
                "start_utc": START,
                "end_utc": "2026-11-25T16:01:00Z",
            }
        ],
    }
    path = f"attachments/timing/{batch}-{STORY}.json"
    payload = raw(value)
    destination = story / path
    destination.parent.mkdir(parents=True)
    destination.write_bytes(payload)
    return registration_event(path, payload, "story-timing-receipt")


def registration_event(path, payload, kind):
    return {
        "v": 0,
        "type": "core.evidence.recorded",
        "ts": RECORDED,
        "story": STORY,
        "actor": {"kind": "agent", "on-behalf-of": "operator-1"},
        "provenance": {"route": "manual-bootstrap", "runtime_transition": False},
        "data": {
            "kind": kind,
            "path": path,
            "scope": {"project": "aitm", "story": STORY},
            "sha256": hashlib.sha256(payload).hexdigest(),
        },
    }


@pytest.fixture
def repo_pair(tmp_path):
    remote = tmp_path / "remote.git"
    checkout = tmp_path / "checkout"
    remote.mkdir()
    checkout.mkdir()
    git(remote, "init", "--bare")
    git(remote, "config", "receive.denyNonFastForwards", "true")
    git(remote, "config", "receive.denyDeletes", "true")
    git(checkout, "init", "-b", "planning")
    git(checkout, "config", "user.email", "test@example.invalid")
    git(checkout, "config", "user.name", "AITM fixture")
    git(checkout, "remote", "add", "origin", str(remote))
    story = checkout / STORY_ROOT
    story.mkdir(parents=True)
    (story / "story.md").write_text(
        '---\nschema: "aitm.story/v0"\nid: 458\ntitle: "Pinned fixture"\n'
        'state: "develop"\nparent: null\nchildren: []\n'
        f'updated: "{START}"\nestimate: {{}}\n---\n\nBody\n',
        encoding="utf-8",
    )
    (story / "events.jsonl").write_bytes(raw(timing_registration(story)) + b"\n")
    pin = commit(checkout, "planning fixture")
    git(checkout, "push", "origin", f"{PLANNING}:{PLANNING}")
    git(checkout, "switch", "-c", "work")
    return checkout, remote, pin


def envelope(pin, *, complete=True, coverage_override=None):
    from aitm_usage.effort.pinned_report import freeze_report

    identity = "1" * 64
    window = {
        "window_start_utc": START,
        "window_end_utc": END,
        "cutoff_utc": CUTOFF,
    }
    manifest = {
        "project": PROJECT,
        "story": STORY,
        "planning_commit": pin,
        "rate_sha256": "b" * 64,
        "window": window,
        "inputs": {
            "receipts": [
                {
                    "path": f"{STORY_ROOT}/attachments/effort/session/{identity}-r1.json",
                    "sha256": "2" * 64,
                    "identity": identity,
                    "revision": 1,
                }
            ],
            "excluded": [],
            "coverage": [],
            "timing": [],
            "registration": None,
        },
    }
    summary = {
        "tokens": {"cached_input": 25, "new_input": 100, "output": 30},
        "api_estimate_usd": "0.0095",
        "cost_eligible": complete,
        "cost_hold_reasons": [] if complete else ["coverage-open"],
        "api_price_basis": BASIS,
        "api_estimate_coverage": {"known_turns": 1, "status": "complete"},
        "turns": [
            {
                "attempt": "3" * 64,
                "identity": identity,
                "revision": 1,
                "provider": "codex",
                "role": "worker",
                "model": "gpt-5.6-sol",
                "time_basis": "native",
                "started_at": START,
                "ended_at": "2026-11-25T16:01:00Z",
                "usage_scope": "bounded",
                "coverage": "complete",
                "outcome": "completed",
                "native_duration_us": 60_000_000,
                "tokens": {"cached_input": 25, "new_input": 100, "output": 30},
                "api_estimate_usd": "0.0095",
                "api_estimate_gap": None,
                "exclusion": None,
            }
        ],
        "token_coverage": {
            key: {"known_turns": 1, "status": "complete"}
            for key in ("cached_input", "new_input", "output")
        },
        "coverage": {
            "admission": "closed" if complete else "open",
            "expected_turns": 1 if complete else None,
            "measured_turns": 1,
            "sampled_attempts": 1,
            "pending": 0,
            "unattributed": 0,
            "missing": 0,
            "unavailable": 0,
            "withdrawn": 0,
            "disputed": 0,
            **(coverage_override or {}),
        },
    }
    return freeze_report(manifest, summary)


def selector_and_proof(data, artifact_commit):
    report = json.loads(data)
    selector = {
        "project": "aitm",
        "report_id": report["report_id"],
        "rate_card": "b" * 64,
        "pricing_basis": BASIS,
        "window_start_utc": START,
        "window_end_utc": END,
        "cutoff_utc": CUTOFF,
    }
    proof = {
        "operator_ref": "operator-1",
        "verified_at_utc": RECORDED,
        "source_report_id": report["report_id"],
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "verified_story": STORY,
        "project_uuid": PROJECT,
        "artifact_commit": artifact_commit,
        "selector": selector.copy(),
    }
    return selector, proof


def test_publication_replay_keeps_original_artifact_and_local_worktree(repo_pair):
    from aitm_usage.effort.pinned_publication import publish_pinned_report
    from aitm_usage.effort.pinned_report import report_path

    checkout, remote, pin = repo_pair
    data = envelope(pin)
    (checkout / "private-local.txt").write_bytes(b"PRIVATE-PROMPT-SENTINEL")
    before = git(checkout, "status", "--porcelain=v1")
    report_id, artifact = publish_pinned_report(checkout, str(remote), data)
    path = report_path(STORY, report_id)
    assert git(remote, "show", f"{artifact}:{path}") == data
    assert oid(remote, PLANNING) == artifact
    assert git(
        remote, "diff-tree", "--no-commit-id", "--name-only", "-r", artifact
    ) == (path.encode() + b"\n")
    assert git(checkout, "status", "--porcelain=v1") == before
    assert git(checkout, "branch", "--show-current").strip() == b"work"
    assert oid(checkout) == pin
    assert not git(checkout, "for-each-ref", "refs/aitm/pinned-report-publication")


def test_publication_conflict_holds_without_overwriting(repo_pair):
    from aitm_usage.effort.pinned_publication import publish_pinned_report
    from aitm_usage.effort.pinned_report import report_path
    from aitm_usage.effort.session_publication import PublicationHold

    checkout, remote, pin = repo_pair
    data = envelope(pin)
    target = checkout / report_path(STORY, json.loads(data)["report_id"])
    target.parent.mkdir(parents=True)
    target.write_bytes(b"conflict")
    conflicting = commit(checkout, "conflicting report")
    git(checkout, "push", "origin", f"HEAD:{PLANNING}")
    with pytest.raises(PublicationHold, match="conflicting immutable"):
        publish_pinned_report(checkout, str(remote), data)
    assert oid(remote, PLANNING) == conflicting
    assert (
        git(remote, "show", f"{conflicting}:{target.relative_to(checkout).as_posix()}")
        == b"conflict"
    )


def test_publication_holds_if_an_immutable_report_was_removed(repo_pair):
    from aitm_usage.effort.pinned_publication import publish_pinned_report
    from aitm_usage.effort.pinned_report import report_path
    from aitm_usage.effort.session_publication import PublicationHold

    checkout, remote, pin = repo_pair
    data = envelope(pin)
    report_id, artifact = publish_pinned_report(checkout, str(remote), data)
    git(checkout, "reset", "--hard", artifact)
    target = checkout / report_path(STORY, report_id)
    target.unlink()
    removed = commit(checkout, "outside writer removes the report")
    git(checkout, "push", "origin", f"HEAD:{PLANNING}")
    with pytest.raises(PublicationHold, match="conflicting immutable report history"):
        publish_pinned_report(checkout, str(remote), data)
    assert oid(remote, PLANNING) == removed


def test_publication_refreshes_stale_remote_and_keeps_lost_ack_replay_stable(
    repo_pair, tmp_path, monkeypatch
):
    from aitm_usage.effort import pinned_publication as publication

    checkout, remote, pin = repo_pair
    newer = tmp_path / "newer"
    git(remote, "clone", "--branch", "planning", str(remote), str(newer))
    git(newer, "config", "user.email", "test@example.invalid")
    git(newer, "config", "user.name", "AITM fixture")
    (newer / "unrelated.md").write_text("later\n", encoding="utf-8")
    newer_tip = commit(newer, "independent planning change")
    native = publication._git
    attempts = []

    def intervening_push(repo, *args, **kwargs):
        if args[0] != "push":
            return native(repo, *args, **kwargs)
        if not attempts:
            git(newer, "push", "origin", f"HEAD:{PLANNING}")
        attempts.append(args[-1])
        result = native(repo, *args, **kwargs)
        if result.returncode == 0:
            return subprocess.CompletedProcess(result.args, 124, b"", b"lost ack")
        return result

    monkeypatch.setattr(publication, "_git", intervening_push)
    data = envelope(pin)
    first = publication.publish_pinned_report(checkout, str(remote), data)
    assert len(attempts) == 2
    assert oid(remote, f"{first[1]}^") == newer_tip
    assert oid(remote, PLANNING) == first[1]
    git(newer, "pull", "--ff-only", "origin", "planning")
    (newer / "unrelated.md").write_text("still later\n", encoding="utf-8")
    later = commit(newer, "another unrelated change")
    git(newer, "push", "origin", f"HEAD:{PLANNING}")
    assert publication.publish_pinned_report(checkout, str(remote), data) == first
    assert oid(remote, PLANNING) == later


def test_registration_replays_exact_fact_and_holds_conflicting_readback(repo_pair):
    from aitm_usage.effort.pinned_publication import (
        prepare_report_registration,
        publish_pinned_report,
    )
    from aitm_usage.effort.session_publication import PublicationHold

    checkout, remote, pin = repo_pair
    data = envelope(pin)
    report_id, artifact = publish_pinned_report(checkout, str(remote), data)

    def prepare(published_commit=artifact):
        return prepare_report_registration(
            checkout,
            str(remote),
            data,
            published_commit,
            operator_ref="operator-1",
            recorded_at_utc=RECORDED,
        )

    with pytest.raises(PublicationHold, match="readback"):
        prepare(pin)
    event = prepare()
    assert event["data"]["report_id"] == report_id
    assert event["data"]["artifact_commit"] == artifact
    assert event["data"]["scope"] == {"story": STORY, "project": PROJECT}
    assert event["data"]["sha256"] == hashlib.sha256(data).hexdigest()
    git(checkout, "reset", "--hard", artifact)
    events = checkout / STORY_ROOT / "events.jsonl"
    events.write_bytes(raw(event) + b"\n")
    registered = commit(checkout, "record report pair")
    git(checkout, "push", "origin", f"HEAD:{PLANNING}")
    assert prepare() is None
    assert oid(remote, PLANNING) == registered
    event["data"]["sha256"] = "0" * 64
    events.write_bytes(raw(event) + b"\n")
    conflict = commit(checkout, "conflicting registration")
    git(checkout, "push", "origin", f"HEAD:{PLANNING}")
    with pytest.raises(PublicationHold, match="conflicting.*registration"):
        prepare()
    assert oid(remote, PLANNING) == conflict


def dashboard_view(checkout, pin, selector):
    source = """
from datetime import UTC, datetime
from pathlib import Path
import json
import subprocess
import sys
from tools.story_dashboard import evidence, usage
from tools.story_dashboard.snapshot import build_snapshot

repo, pin, selector = sys.argv[1:]
commit_date = subprocess.check_output(
    ["git", "-C", repo, "show", "-s", "--format=%cI", pin], text=True
).strip()
as_of = max(
    datetime.fromisoformat("2026-11-25T20:00:00Z"),
    datetime.fromisoformat(commit_date).astimezone(UTC),
)
tree = evidence.read_tree(Path(repo), pin, as_of)
selector = usage.ReportSelector.from_dict(json.loads(selector))
report = usage.select_usage(tree, selector)
measure = report.stories[458].direct
actual = build_snapshot(tree, selector)["stories"][0]["timing"]["actual"]["milliseconds"]
print(json.dumps({"cost": str(measure.priced_usd) if measure.priced_usd is not None else None,
                  "coverage": measure.coverage, "digests": report.resolved_receipt_digests,
                  "actual_ms": actual}))
"""
    return json.loads(
        subprocess.check_output(
            [sys.executable, "-c", source, str(checkout), pin, json.dumps(selector)],
            cwd=REPO_ROOT,
        )
    )


def test_complete_cost_projection_is_accepted_by_existing_dashboard(repo_pair):
    from aitm_usage.effort.pinned_cost import cost_candidate
    from aitm_usage.effort.pinned_publication import publish_pinned_report

    checkout, remote, pin = repo_pair
    data = envelope(pin)
    _, artifact = publish_pinned_report(checkout, str(remote), data)
    selector, proof = selector_and_proof(data, artifact)
    outcome = cost_candidate(data, selector, proof)
    assert outcome["status"] == "eligible"
    receipt = raw(outcome["receipt"])
    git(checkout, "reset", "--hard", artifact)
    target = checkout / STORY_ROOT / outcome["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(receipt)
    digest = hashlib.sha256(receipt).hexdigest()
    event = registration_event(outcome["path"], receipt, "story-usage-receipt")
    events = checkout / STORY_ROOT / "events.jsonl"
    time_evidence = events.read_bytes()
    events.write_bytes(time_evidence + raw(event) + b"\n")
    latest = commit(checkout, "register the authorized fixture")
    assert dashboard_view(checkout, latest, selector) == {
        "cost": "0.0095",
        "coverage": "complete",
        "digests": [digest],
        "actual_ms": 60_000,
    }
    event["actor"]["on-behalf-of"] = "other-operator"
    events.write_bytes(time_evidence + raw(event) + b"\n")
    other = commit(checkout, "alter operator binding")
    post = dashboard_view(checkout, other, selector)
    assert post["cost"] is None
    assert post["actual_ms"] == 60_000


def test_partial_cost_hold_leaves_existing_dashboard_cost_unknown(repo_pair):
    from aitm_usage.effort.pinned_cost import cost_candidate
    from aitm_usage.effort.pinned_publication import publish_pinned_report

    checkout, remote, pin = repo_pair
    data = envelope(pin, complete=False)
    _, artifact = publish_pinned_report(checkout, str(remote), data)
    selector, proof = selector_and_proof(data, artifact)
    assert cost_candidate(data, selector, proof) == {
        "status": "held",
        "reasons": ["coverage-open"],
    }
    assert dashboard_view(checkout, artifact, selector) == {
        "cost": None,
        "coverage": "unknown",
        "digests": [],
        "actual_ms": 60_000,
    }


@pytest.mark.parametrize(
    "field", ["source_sha256", "project_uuid", "verified_story", "selector"]
)
def test_cost_projection_requires_exact_operator_binding(repo_pair, field):
    from aitm_usage.effort.pinned_cost import cost_candidate

    _, _, pin = repo_pair
    data = envelope(pin)
    selector, proof = selector_and_proof(data, "a" * 40)
    proof[field] = "different"
    assert cost_candidate(data, selector, proof)["status"] == "held"


def test_cost_projection_does_not_trust_eligibility_without_reconciled_coverage(
    repo_pair,
):
    from aitm_usage.effort.pinned_cost import cost_candidate

    _, _, pin = repo_pair
    data = envelope(pin, coverage_override={"expected_turns": 2, "pending": 1})
    selector, proof = selector_and_proof(data, "a" * 40)
    result = cost_candidate(data, selector, proof)
    assert result == {"status": "held", "reasons": ["invalid-complete-cost"]}
