import json
from dataclasses import replace
from hashlib import sha256

from test_effort_trail import PROJECT, evidence

from aitm_usage.effort import EffortStore, Role


def test_report_scopes_attempts_and_exports_deterministically(tmp_path, capsys):
    from aitm_usage.effort.cli import main

    database = tmp_path / "effort.db"
    store = EffortStore(database, PROJECT)
    worker, first = evidence("worker", story=443)
    reviewer, second = evidence("review", story=444, session="review")
    pending, _ = evidence("pending", story=443)
    orphan, third = evidence("orphan", session="orphan")
    for enrollment in (
        worker,
        replace(reviewer, role=Role.REVIEWER),
        pending,
        replace(orphan, story=None, epic=None),
    ):
        store.enroll(enrollment)
    for receipt in (first, second, third):
        store.ingest(receipt)
    original = database.read_bytes()

    def run(command, *scope, options=("--json",)):
        assert (
            main(
                [
                    "--database",
                    str(database),
                    "--project",
                    str(PROJECT),
                    command,
                    *scope,
                    *options,
                ]
            )
            == 0
        )
        return capsys.readouterr().out

    story = json.loads(run("report", "--story", "443"))
    assert story["total"]["observed_tokens"] == 10
    assert story["total"]["engaged_us"] == 1_000_000
    assert story["total"]["estimated_usd"] is None
    assert story["total"]["provider_reported_grok_usd_ticks"] is None
    assert story["total"]["verified_billed_usd"] is None
    assert story["unsettled_attempts"] == 1
    assert {row["attempt_id"] for row in story["attempts"]} == {
        str(worker.attempt_id),
        str(pending.attempt_id),
    }
    epic = json.loads(run("report", "--epic", "435"))
    assert epic["by_role"]["reviewer"]["observed_tokens"] == 10
    assert epic["by_provider"]["codex"]["observed_tokens"] == 20
    assert epic["total"]["working_wall_us"] is None
    assert json.loads(run("report", "--unattached"))["total"]["observed_tokens"] == 10
    export = run("export", "--epic", "435", options=())
    assert export == run("export", "--epic", "435", options=())
    assert json.loads(export)["schema"] == "aitm.effort.report/v1"
    assert "Verified billed USD: unknown" in run("report", "--story", "443", options=())
    assert database.read_bytes() == original


def test_missing_store_is_not_created(tmp_path, capsys):
    from aitm_usage.effort.cli import main

    database = tmp_path / "missing.db"
    assert (
        main(
            [
                "--database",
                str(database),
                "--project",
                str(PROJECT),
                "report",
                "--unattached",
            ]
        )
        == 2
    )
    assert not database.exists()
    assert capsys.readouterr().out == ""


def test_legacy_export_preserves_identity_and_blocks_combined_total(tmp_path):
    from aitm_usage.effort import RollupTarget
    from aitm_usage.effort.export import read_legacy
    from aitm_usage.effort.report import build_report

    database = tmp_path / "effort.db"
    store = EffortStore(database, PROJECT)
    enrollment, receipt = evidence("legacy-overlap", story=443)
    store.enroll(enrollment)
    store.ingest(receipt)
    basis = f"standard-api-USD:2026-11-09:sha256:{'a' * 64}"
    row = {
        "source": f"hmac-sha256:{'b' * 64}",
        "observation_revision": 2,
        "provider": "codex",
        "availability": "complete",
        "tokens": {"total_tokens": 10},
        "price": {
            "availability": "complete",
            "currency": "USD",
            "rate_basis": basis,
            "usd": "0.01",
        },
    }
    data = (json.dumps(row) + "\n").encode()
    manifest = {
        "schema": "aitm.usage.export/v1",
        "project_id": str(PROJECT),
        "cutoff": 44,
        "row_count": 1,
        "rate_basis": basis,
        "sha256": sha256(data).hexdigest(),
        "coverage": {"complete": 1, "partial": 0, "unknown": 0},
        "diagnostics": [],
    }
    manifest_file = tmp_path / "manifest.json"
    usage_file = tmp_path / "usage.jsonl"
    manifest_file.write_text(json.dumps(manifest) + "\n")
    usage_file.write_bytes(data)
    original = manifest_file.read_bytes()
    legacy = read_legacy(tmp_path, PROJECT)
    report = build_report(
        store.snapshot(), RollupTarget(PROJECT, story=443), legacy=legacy
    )
    assert report["total"]["observed_tokens"] == 10
    assert report["combined_coverage"] == "unresolved-overlap"
    assert report["legacy"]["cutoff"] == 44
    assert report["legacy"]["rows"][0]["source"] == row["source"]
    assert report["legacy"]["rows"][0]["observation_revision"] == 2
    assert report["legacy"]["rows"][0]["estimated_usd"] == "0.01"
    assert report["legacy"]["rows"][0]["rate_basis"] == basis
    assert usage_file.read_bytes() == data
    assert manifest_file.read_bytes() == original


def test_read_only_store_accepts_an_existing_pre_trail_database(tmp_path):
    import sqlite3
    from contextlib import closing

    database = tmp_path / "effort.db"
    store = EffortStore(database, PROJECT)
    enrollment, receipt = evidence("pre-trail", story=443)
    store.enroll(enrollment)
    store.ingest(receipt)
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("DROP TABLE scope_markers")
        connection.execute("DROP TABLE handoffs")
    original = database.read_bytes()
    snapshot = EffortStore(database, PROJECT, read_only=True).snapshot()
    assert snapshot.attributed[0].receipt == receipt
    assert snapshot.markers == snapshot.handoffs == ()
    assert database.read_bytes() == original


def test_report_preserves_grok_native_zero_without_claiming_billing(tmp_path):
    from aitm_usage.effort import RollupTarget
    from aitm_usage.effort.report import build_report, render_text

    store = EffortStore(tmp_path / "effort.db", PROJECT)
    enrollment, receipt = evidence("native-zero", story=443)
    receipt = replace(
        receipt,
        turn=replace(receipt.turn, provider="grok"),
        schema="aitm.effort.receipt/v2",
        grok_cost_usd_ticks=0,
        grok_cache_creation_tokens=0,
    )
    store.enroll(enrollment)
    store.ingest(receipt)
    report = build_report(store.snapshot(), RollupTarget(PROJECT, story=443))
    assert report["by_provider"]["grok"]["provider_reported_grok_usd_ticks"] == 0
    assert report["total"]["verified_billed_usd"] is None
    assert "Provider-reported Grok USD: 0.0000000000" in render_text(report)
