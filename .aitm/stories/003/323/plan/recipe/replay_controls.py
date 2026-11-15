"""Off-host controls isolate one failing fact at a time using saved native evidence."""

from copy import deepcopy
from pathlib import Path
import subprocess

import evidence_io as io
from capture import RECORDS
from profiles import digest
from source.operator_recovery import instant, need
from verify_recovery import DENIALS, load_docs, verify
from ci_scheduled_shadow import incident_observation, inspect


def add_candidate(docs, same_authorization):
    added = deepcopy(docs["run-before"])
    added["id"] += 1
    added["run_number"] += 1
    if not same_authorization:
        added["display_title"] = "recovery/00000000000000000000000000000000"
    doc = docs["workflow-runs-after"][0]
    doc["workflow_runs"].append(added)
    doc["total_count"] += 1


def replace_run(docs, **fields):
    for phase in ("before", "after"):
        docs[f"run-{phase}"].update(fields)
        docs[f"workflow-runs-{phase}"][0]["workflow_runs"][0].update(fields)


class NativeScheduleReplay:
    def __init__(self, snapshot, runs):
        self.snapshot = snapshot
        self.runs = runs

    def document(self, path):
        mapping = {"": "repository", "branches/trunk": "branch",
                   "actions/workflows/scheduled-full-shadow.yml": "scheduled-full-shadow"}
        return io.read(self.snapshot / (mapping[path] + ".json"))

    def pages(self, path, key):
        need(key == "workflow_runs" and "event=schedule" in path, "unexpected schedule replay endpoint")
        return deepcopy(self.runs)


def production_controls():
    source = RECORDS / "production-pinned"
    observed = io.read(source / "native-scheduled-reader.json")
    diagnostic = io.read(source / "native-diagnostic-reader.json")
    late = io.read(source / "run-43709222718-attempt-1.json")
    now = instant(io.read(source / "gate-summary.json")["captured_at"])
    slot = instant(observed["slot"])
    actual = inspect(NativeScheduleReplay(source, [late]), now=now)
    missing = inspect(NativeScheduleReplay(source, []), now=now)
    need(actual == observed and actual["status"] == "incomplete"
         and not actual["artifact"] and not actual["current_verified"]
         and not missing["artifact"] and not missing["current_verified"]
         and missing["status"] == "incomplete" and "observed_run" not in missing,
         "native schedule did not fail closed")
    refused = None
    try:
        incident_observation({**diagnostic, "status": "green", "current_verified": True})
    except DENIALS as exc:
        refused = str(exc)
    need(refused == "scheduled result unavailable for shadow incident replay",
         "production diagnostic event admitted")
    archived = io.read(source / "legacy-reviewed-gap.json")
    need(archived["slot"] == actual["slot"] and archived["status"] == "incomplete"
         and archived["artifact"] is None and "observed_run" not in archived,
         "retained production no-registration observation disagrees")
    return {
        "live_production": {"scheduled": observed, "diagnostic": diagnostic},
        "historical_live_production_at_miss": archived,
        "explicit_replays": {
            "late_real_record": actual, "absent_schedule_record": missing,
            "hypothetically_current_green_production_diagnostic": {"denial": refused},
        },
        "late_registration_seconds": (instant(late["created_at"]) - slot).total_seconds(),
    }


def main():
    evidence = RECORDS / "green"
    verified = io.read(evidence / "result.json")
    now = instant(verified["verified_at"])
    original = load_docs(evidence)
    raw = (evidence / "artifact.zip").read_bytes()
    need(verify(evidence, now=now) == verified, "positive retained evidence failed replay")
    rows = []

    def deny(label, expected, change=None, archive=raw):
        docs = deepcopy(original)
        if change is not None:
            change(docs)
        denial = None
        try:
            verify(evidence, docs=docs, archive_raw=archive, now=now)
        except DENIALS as exc:
            denial = str(exc)
        need(denial == expected, f"{label} unexpectedly returned {denial}")
        rows.append({"control": label, "scope": "off-host mutation of retained authenticated facts",
                     "status": "held", "reason": denial})

    deny("red accepted-identity attempt", "red or unsuccessful recovery",
         lambda docs: replace_run(docs, conclusion="failure"))
    deny("missing archive bytes", "missing or duplicate recovery archive", archive=None)
    deny("missing artifact listing", "missing or duplicate recovery archive",
         lambda docs: docs.update(artifacts=[{"total_count": 0, "artifacts": []}]))
    foreign = io.read(RECORDS / "production-pinned/artifacts-43709222718.json")[0]["artifacts"][0]
    foreign["name"] = "aitm-recovery-a1"
    deny("foreign genuine production artifact metadata", "foreign or invalid recovery archive custody",
         lambda docs: docs.update(artifacts=[{"total_count": 1, "artifacts": [foreign]}]))
    deny("corrupt archive bytes", "foreign or invalid recovery archive custody", archive=raw[:-1] + b"x")
    deny("protected SHA moved", "stale or moved protected default target",
         lambda docs: docs["branch-after"]["commit"].update(sha="0"*40))
    deny("wrong recovery event", "wrong recovery event", lambda docs: replace_run(docs, event="schedule"))
    deny("latest run supersedes authorized run", "dispatch superseded or replayed",
         lambda docs: add_candidate(docs, False))
    deny("same signed admission dispatched twice", "dispatch superseded or replayed",
         lambda docs: add_candidate(docs, True))
    deny("same run rerun attempt", "replayed or different dispatch attempt",
         lambda docs: replace_run(docs, run_attempt=2))
    deny("hold disabled before acknowledgment", "explicit hold is missing or bypassable",
         lambda docs: docs["hold-after"].update(enforcement="disabled"))
    pending_docs = load_docs(RECORDS / "pending")
    denial = None
    try:
        verify(RECORDS / "pending", docs=pending_docs, now=now)
    except DENIALS as exc:
        denial = str(exc)
    need(denial == "pending recovery", "native in-progress sample was not held")
    output = {
        "positive_retained_evidence_reconciled": True, "native_pending_denial": denial,
        "source_artifact_sha256": digest(raw), "recovery_controls": rows,
        "production_slot_controls": production_controls(),
    }
    io.write(RECORDS / "control-results.json", output)
    for row in rows:
        print(row["control"], row["reason"])


if __name__ == "__main__":
    main()
