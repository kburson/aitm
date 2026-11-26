import json
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pytest
from test_effort_pinned_coverage import WINDOW
from test_effort_session_publication import PROJECT, STORY, git, receipt
from test_effort_session_publication import repo_pair as repo_pair

from aitm_usage.effort import pinned_inputs
from aitm_usage.effort.pinned_coverage import MAX_INPUT_BLOB_BYTES, canonical
from aitm_usage.effort.pinned_inputs import read_inputs
from aitm_usage.effort.receipts import TimeBasis
from aitm_usage.effort.session import PublicReceipt
from aitm_usage.effort.store import EffortError
from aitm_usage.types import _decode, _encode


def pin(repo):
    git(repo, "add", ".aitm")
    git(repo, "commit", "-m", "pin evidence")
    return git(repo, "rev-parse", "HEAD")


def write(repo: Path, relative: str, raw: bytes):
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def at(hour, minute=0):
    return datetime(2026, 11, 25, hour, minute, tzinfo=UTC)


def add_receipt(repo, identity="a" * 64, *, rev=1, prev=None, **fields):
    entry = receipt(identity=identity, revision=rev, previous=prev)
    native = _decode(entry.data, PublicReceipt)
    args = (
        dict(
            started_at=at(0, 5),
            ended_at=at(1),
            observed_at=at(2),
            time_basis=TimeBasis.NATIVE,
        )
        | fields
    )
    raw = _encode(replace(native, **args), PublicReceipt).encode()
    write(repo, entry.path, raw)
    return sha256(raw).hexdigest()


def add_coverage(
    repo,
    *,
    state="observed",
    register=True,
    file=True,
    mismatch=False,
    supersedes=None,
    timing=None,
    invalid_fact=None,
    extra_attempt=None,
):
    record = {
        "schema": "aitm.story-effort-coverage/v1",
        "project": str(PROJECT),
        "story": 457,
        "window": WINDOW,
        "admission": "closed",
        "attempts": [{"attempt": "5" * 64, "state": state}],
        "unattributed": 0,
        "verified_no_work": False,
        "supersedes": supersedes,
        "attestation_sha256": "f" * 64,
    }
    if timing is not None:
        record["timing"] = timing
    if extra_attempt is not None:
        record["attempts"].append({"attempt": extra_attempt, "state": "observed"})
    raw = canonical(record)
    digest = sha256(raw).hexdigest()
    path = f"attachments/effort/coverage/{digest}.json"
    if file:
        write(repo, f"{STORY}/{path}", raw)
    if register:
        log = repo / STORY / "events.jsonl"
        fact = {
            "v": 0,
            "ts": at(2, 1).isoformat(),
            "type": "core.evidence.recorded",
            "story": 457,
            "actor": {"kind": "agent"},
            "provenance": {"route": "manual-bootstrap", "runtime_transition": False},
            "data": {
                "kind": "story-effort-coverage",
                "path": path,
                "sha256": "b" * 64 if mismatch else digest,
                "scope": {"story": 457, "project": str(PROJECT)},
                "window": WINDOW,
            },
        }
        if invalid_fact == "data":
            fact["data"]["extra"] = True
        elif invalid_fact == "premature":
            fact["ts"] = at(1, 59).isoformat()
        elif invalid_fact == "chronology":
            fact["recorded_at_utc"] = at(2).isoformat()
        elif invalid_fact is not None:
            del fact[invalid_fact]
        with log.open("a", encoding="utf-8") as target:
            target.write(json.dumps(fact) + "\n")
    return digest


def test_pinned_inputs_cutoff_and_window_edges(repo_pair):
    repo, _ = repo_pair
    older = add_receipt(repo)
    add_receipt(repo, rev=2, prev=older, observed_at=at(2, 1))
    add_receipt(repo, "b" * 64, attempt="6" * 64, started_at=at(1), ended_at=at(1, 5))
    add_receipt(
        repo, "c" * 64, attempt="7" * 64, started_at=at(0, 50), ended_at=at(1, 5)
    )
    result = read_inputs(repo, PROJECT, 457, pin(repo), WINDOW)
    assert [(r["identity"], r["revision"]) for r in result.receipts] == [("a" * 64, 1)]
    assert {r["reason"] for r in result.manifest["excluded"]} == {
        "after-cutoff",
        "outside-window",
        "crossing-window",
    }
    assert "crossing-window" in result.gaps and result.coverage is None


@pytest.mark.parametrize(
    ("register", "file", "mismatch", "gap"),
    [
        (False, True, False, "coverage-missing"),
        (True, False, False, "coverage-file-missing"),
        (True, True, True, "coverage-digest-mismatch"),
    ],
)
def test_coverage_requires_matching_registration(
    repo_pair, register, file, mismatch, gap
):
    repo, _ = repo_pair
    add_receipt(repo)
    add_coverage(repo, register=register, file=file, mismatch=mismatch)
    result = read_inputs(repo, PROJECT, 457, pin(repo), WINDOW)
    assert result.coverage is None and gap in result.gaps
    assert len(result.receipts) == 1


@pytest.mark.parametrize(
    "invalid", ["v", "ts", "actor", "provenance", "data", "premature", "chronology"]
)
def test_closed_coverage_requires_a_typed_evidence_fact(repo_pair, invalid):
    repo, _ = repo_pair
    add_receipt(repo)
    add_coverage(repo, invalid_fact=invalid)
    result = read_inputs(repo, PROJECT, 457, pin(repo), WINDOW)
    assert result.coverage is None
    assert result.gaps == ("coverage-invalid-registration",)


def test_new_pin_withdrawal_removes_older_visible_attempt(repo_pair):
    repo, _ = repo_pair
    add_receipt(repo)
    digest = add_coverage(repo)
    old_pin = pin(repo)
    add_coverage(repo, state="withdrawn", supersedes=digest)
    new_pin = pin(repo)
    assert len(read_inputs(repo, PROJECT, 457, old_pin, WINDOW).receipts) == 1
    result = read_inputs(repo, PROJECT, 457, new_pin, WINDOW)
    assert result.receipts == ()
    assert result.manifest["excluded"][0]["reason"] == "withdrawn"


def test_refuses_broken_lineage_and_inexact_commit(repo_pair):
    repo, _ = repo_pair
    add_receipt(repo, rev=2, prev="f" * 64)
    commit = pin(repo)
    with pytest.raises(EffortError, match="lineage"):
        read_inputs(repo, PROJECT, 457, commit, WINDOW)
    with pytest.raises(EffortError, match="commit"):
        read_inputs(repo, PROJECT, 457, "HEAD", WINDOW)


@pytest.mark.parametrize("problem", ["path", "mode", "size", "project", "placement"])
def test_pin_refuses_invalid_target_receipt_evidence(repo_pair, problem):
    repo, _ = repo_pair
    entry = receipt()
    if problem == "path":
        write(repo, entry.path + "~", b"disallowed")
    elif problem == "mode":
        link_value = write(repo, "link-fixture", b"private-target")
        oid = git(repo, "hash-object", "-w", str(link_value))
        git(repo, "update-index", "--add", "--cacheinfo", f"120000,{oid},{entry.path}")
        git(repo, "commit", "-m", "pin special mode")
        with pytest.raises(EffortError, match="normal pinned evidence file"):
            read_inputs(repo, PROJECT, 457, git(repo, "rev-parse", "HEAD"), WINDOW)
        return
    elif problem == "size":
        write(repo, entry.path, b"0" * (MAX_INPUT_BLOB_BYTES + 1))
    elif problem == "project":
        add_receipt(repo, project=type(PROJECT)(int=1))
    else:
        add_receipt(repo)
        write(repo, entry.path.replace("/457/", "/458/"), b"unread foreign blob")
    with pytest.raises(EffortError, match="path|normal|limits|scope|another story"):
        read_inputs(repo, PROJECT, 457, pin(repo), WINDOW)


def test_coverage_fork_and_cutoff_crossing_lineage_remain_explicit(repo_pair):
    repo, _ = repo_pair
    older = add_receipt(repo, observed_at=at(2, 1))
    add_receipt(repo, rev=2, prev=older, observed_at=at(2))
    add_coverage(repo)
    add_coverage(repo, state="withdrawn")
    result = read_inputs(repo, PROJECT, 457, pin(repo), WINDOW)
    assert result.coverage is None and result.receipts == ()
    assert set(result.gaps) == {"coverage-conflict", "cutoff-lineage"}


def test_pin_bounds_recursive_path_stream(repo_pair, monkeypatch):
    repo, _ = repo_pair
    add_receipt(repo)
    commit = pin(repo)
    monkeypatch.setattr(pinned_inputs, "_MAX_INPUT_TOTAL", 1)
    with pytest.raises(EffortError, match="listing exceeds"):
        pinned_inputs.PinnedTree(repo, commit).paths(STORY)


@pytest.mark.parametrize(
    "issue", [None, "late-admission", "missing-source", "late-observation", "duplicate"]
)
def test_timing_joins_require_registered_actor_and_wait_evidence(repo_pair, issue):
    repo, _ = repo_pair
    add_receipt(repo)
    path = "attachments/timing/fixture-457.json"
    shared = {
        "actor": "agent-1",
        "turn": "fixture-turn-1",
        "phase": "implement",
        "role": "implementer",
        "attempt": "fixture-attempt",
        "coverage": "complete",
    }
    source_record = {
        "schema": "aitm.story-timing-receipt/v1",
        "project": "aitm",
        "subject": 457,
        "batch": "fixture",
        "recorded_at_utc": at(1, 5).isoformat(),
        "source": {"ref": "manual:fixture"},
        "observations": [
            shared
            | {
                "observation_id": "fixture.turn",
                "kind": "agent-turn",
                "basis": "verified-turn-boundaries",
                "start_utc": at(0, 5).isoformat(),
                "end_utc": at(1).isoformat(),
            },
            shared
            | {
                "observation_id": "fixture.wait",
                "kind": "owner-wait",
                "basis": "verified-owner-request-response",
                "start_utc": at(0, 20).isoformat(),
                "end_utc": at(0, 40).isoformat(),
            },
        ],
    }
    if issue == "missing-source":
        del source_record["source"]
    elif issue == "late-observation":
        source_record["observations"][0]["recorded_at_utc"] = at(2, 1).isoformat()
    source = canonical(source_record)
    write(repo, f"{STORY}/{path}", source)
    sha = sha256(source).hexdigest()
    event = {
        "v": 0,
        "ts": (at(2, 1) if issue == "late-admission" else at(1, 5)).isoformat(),
        "story": 457,
        "type": "core.evidence.recorded",
        "actor": {"kind": "agent", "harness": "codex"},
        "provenance": {"route": "manual-bootstrap", "runtime_transition": False},
        "data": {
            "kind": "story-timing-receipt",
            "path": path,
            "sha256": sha,
            "scope": {"project": "aitm", "story": 457},
        },
    }
    log = repo / STORY / "events.jsonl"
    with log.open("a") as output:
        output.write(json.dumps(event) + "\n")
    join = {
        "attempt": "5" * 64,
        "path": path,
        "sha256": sha,
        "project": "aitm",
        "observation": "fixture.turn",
        "clock": "f" * 64,
        "waits": ["fixture.wait"],
    }
    joins = [join]
    extra = "6" * 64 if issue == "duplicate" else None
    if extra is not None:
        add_receipt(repo, "b" * 64, attempt=extra)
        joins.append(join | {"attempt": extra})
    add_coverage(repo, timing=joins, extra_attempt=extra)
    result = read_inputs(repo, PROJECT, 457, pin(repo), WINDOW)
    assert result.coverage is not None and len(result.receipts) == len(joins)
    if issue is not None:
        assert result.timing == () and result.gaps == ("timing-evidence-invalid",)
    else:
        assert result.timing == (
            {
                "attempt": "5" * 64,
                "actor": "agent-1",
                "clock": "f" * 64,
                "start": at(0, 5).isoformat(),
                "end": at(1).isoformat(),
                "owner_waits": [
                    {"start": at(0, 20).isoformat(), "end": at(0, 40).isoformat()}
                ],
            },
        )
        assert result.manifest["timing"] == [{"path": f"{STORY}/{path}", "sha256": sha}]
