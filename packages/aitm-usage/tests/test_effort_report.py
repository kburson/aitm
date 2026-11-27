import json
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

from test_effort_trail import PROJECT, effort_snapshot, evidence, ref

from aitm_usage.effort import Attribution, EffortStore, Role


class ExportDirectory:
    """Fixed in-memory export bytes with a read-only filesystem-shaped API."""

    def __init__(self, files):
        self.files = files

    def __truediv__(self, name):
        return SimpleNamespace(read_bytes=lambda: self.files[name])


def test_report_scopes_attempts_and_exports_deterministically(monkeypatch, capsys):
    from aitm_usage.effort.cli import main

    database = Path("/fixture/effort.db")
    worker, first = evidence("worker", story=443)
    reviewer, second = evidence("review", story=444, session="review")
    pending, _ = evidence("pending", story=443)
    orphan, third = evidence("orphan", session="orphan")
    pairs = (
        (worker, first),
        (replace(reviewer, role=Role.REVIEWER), second),
        (replace(orphan, story=None, epic=None), third),
    )
    snapshot = effort_snapshot(*pairs, pending_enrollments=(pending,))

    def open_store(path, project, *, read_only):
        assert (path, project, read_only) == (database, PROJECT, True)
        return SimpleNamespace(snapshot=lambda: snapshot)

    monkeypatch.setattr("aitm_usage.effort.cli.EffortStore", open_store)

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
    link = Attribution(
        PROJECT, third.observation_id, 435, 443, ref("late-authorization")
    )
    snapshot = effort_snapshot(*pairs, pending_enrollments=(pending,), links=(link,))
    attached = json.loads(run("report", "--story", "443"))
    assert attached["total"]["observed_tokens"] == 20
    assert any(
        row["attempt_id"] == str(orphan.attempt_id) for row in attached["attempts"]
    )
    unattached = json.loads(run("report", "--unattached"))
    assert unattached["total"]["observed_tokens"] is None
    assert unattached["attempts"] == []
    assert str(orphan.attempt_id) not in run("report", "--unattached", options=())


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


def test_legacy_export_preserves_identity_and_blocks_combined_total():
    from aitm_usage.effort import RollupTarget
    from aitm_usage.effort.export import read_legacy
    from aitm_usage.effort.report import build_report

    enrollment, receipt = evidence("legacy-overlap", story=443)
    snapshot = effort_snapshot((enrollment, receipt))
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
    files = {
        "manifest.json": (json.dumps(manifest) + "\n").encode(),
        "usage.jsonl": data,
    }

    legacy = read_legacy(ExportDirectory(files), PROJECT)
    report = build_report(snapshot, RollupTarget(PROJECT, story=443), legacy=legacy)
    assert report["total"]["observed_tokens"] == 10
    assert report["combined_coverage"] == "unresolved-overlap"
    assert report["legacy"]["cutoff"] == 44
    assert report["legacy"]["rows"][0]["source"] == row["source"]
    assert report["legacy"]["rows"][0]["observation_revision"] == 2
    assert report["legacy"]["rows"][0]["estimated_usd"] == "0.01"
    assert report["legacy"]["rows"][0]["rate_basis"] == basis


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


def test_report_preserves_grok_native_zero_without_claiming_billing():
    from aitm_usage.effort import RollupTarget
    from aitm_usage.effort.report import build_report, render_text

    enrollment, receipt = evidence("native-zero", story=443)
    receipt = replace(
        receipt,
        turn=replace(receipt.turn, provider="grok"),
        schema="aitm.effort.receipt/v2",
        grok_cost_usd_ticks=0,
        grok_cache_creation_tokens=0,
    )
    target = RollupTarget(PROJECT, story=443)
    report = build_report(effort_snapshot((enrollment, receipt)), target)
    assert report["by_provider"]["grok"]["provider_reported_grok_usd_ticks"] == 0
    assert report["total"]["verified_billed_usd"] is None
    assert "Provider-reported Grok USD: 0.0000000000" in render_text(report)

    missing_enrollment, missing = evidence(
        "native-price-missing", story=443, session="other"
    )
    missing = replace(missing, turn=replace(missing.turn, provider="grok"))
    report = build_report(
        effort_snapshot((enrollment, receipt), (missing_enrollment, missing)), target
    )
    assert report["by_provider"]["grok"]["price_gaps"] == 1
    text = render_text(report)
    assert (
        "Provider-reported Grok USD: 0.0000000000 (known subtotal, price gaps: 1)"
        in text
    )
    assert "Clock domains: 2" in text
