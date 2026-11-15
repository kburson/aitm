"""Build the exact review subject from authenticated, finished rehearsal records."""

from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import evidence_io as io
from capture import ROOT, RECORDS
from source.operator_recovery import need


def summary():
    data = io.read(RECORDS / "green/result.json")
    completed = io.read(RECORDS / "operator-acknowledgment/receipt.json")
    newer = RECORDS / "native-replay"
    replay = io.read(newer / "result.json")
    artifact_route = (newer / "first-artifact-after-rerun.response").read_text()
    artifact_history = io.read(newer / "artifacts-after-rerun.json")
    need("404" in artifact_route.splitlines()[0] and all(p["total_count"] == 0 for p in artifact_history),
         "post-replay artifact availability readback disagrees")
    replay["attempt_1_provider_artifact_after_rerun"] = {
        "listing_count": 0, "direct_http_status": 404,
        "observed_at": (newer / "first-artifact-after-rerun-read-at").read_text().strip(),
        "retained_archive_path": "records/green/artifact.zip",
    }
    controls = io.read(RECORDS / "control-results.json")
    probe = {n: io.read(RECORDS / f"{n}/rule-suite.json")
             for n in ("held-merge-probe", "green-held-merge-probe")}
    need(all(p["result"] == "fail" and any(row["rule_type"] == "update" and row["result"] == "fail"
                                          for row in p["rule_evaluations"]) for p in probe.values()),
         "native hold probes do not agree")
    gate_before = io.read(RECORDS / "production-pinned/gate-summary.json")
    gate_after = io.read(RECORDS / "production-final/gate-summary.json")
    stable = ("gate_and_shadow_blobs", "effective_rules", "rulesets", "workflows")
    need(all(gate_before[key] == gate_after[key] for key in stable), "production gate or protection drifted")
    for name in ("legacy-protection.json", "issue-103.json"):
        need(io.read(RECORDS / "production-pinned" / name) == io.read(RECORDS / "production-final" / name),
             "production issue or legacy protection changed")
    production = controls["production_slot_controls"]
    first = data["run"]
    auth = completed["acknowledgment"]
    need(first["id"] == auth["run_id"] == replay["run_id"] and data["artifact"]["id"] == auth["artifact_id"]
         and data["artifact"]["digest"] == auth["artifact_digest"], "review subjects disagree")
    pack = {
        "issue": 323, "status": "review-requested", "scope": "disposable recovery only",
        "trunk": {"production_before": gate_before["head"], "production_after": gate_after["head"],
                  "production_at_acknowledgment": auth["production_sha_at_acknowledgment"],
                  "production_control_blobs_unchanged": True, "production_protections_unchanged": True,
                  "production_issue_103_unchanged": True, "owner_cutover_approval": False},
        "production_slot": production["live_production"]["scheduled"],
        "historical_live_production_at_missed_deadline": production["historical_live_production_at_miss"],
        "production_late_registration_seconds": production["late_registration_seconds"],
        "production_diagnostic": production["live_production"]["diagnostic"],
        "disposable_recovery": data, "operator_acknowledgment": completed, "native_replay": replay,
        "native_hold_probe_rule_suite_ids": {name: doc["id"] for name, doc in probe.items()},
        "off_host_controls": controls["recovery_controls"],
    }
    io.write(ROOT / "qualification-summary.json", pack)
    return pack


def zip_records():
    inputs = sorted(path for path in RECORDS.rglob("*") if path.is_file())
    with ZipFile(ROOT / "rehearsal-evidence.zip", "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in inputs:
            entry = ZipInfo(path.relative_to(ROOT).as_posix())
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes(), compresslevel=9)
    with ZipFile(ROOT / "rehearsal-evidence.zip") as archive:
        need(archive.testzip() is None and len(archive.namelist()) == len(inputs), "retained archive is corrupt")
    return len(inputs)


if __name__ == "__main__":
    summary()
    print(zip_records(), "retained files")
