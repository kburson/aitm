"""Pinned report reopening follows the requested immutable artifact."""

import json
import subprocess
from pathlib import Path
from uuid import UUID

import pytest

from aitm_usage.effort.cli import main
from aitm_usage.effort.pinned_report import (
    ReportUnavailable,
    freeze_report,
    reopen_pinned_report,
    report_path,
    validate_envelope,
)

PROJECT = UUID(int=451)
STORY = 458
RATE = "a" * 64
WINDOW = {
    "window_start_utc": "2026-11-25T00:00:00Z",
    "window_end_utc": "2026-11-26T00:00:00Z",
    "cutoff_utc": "2026-11-26T01:00:00Z",
}


def _git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args]).decode().strip()


def _commit(repo, message):
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def target(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@example.com")
    root = repo / ".aitm/stories/004/458"
    root.mkdir(parents=True)
    (root / "story.md").write_text("---\nid: 458\n---\n")
    return repo, _commit(repo, "source evidence")


def _manifest(pin, rate=RATE):
    return {
        "project": str(PROJECT),
        "story": STORY,
        "planning_commit": pin,
        "window": WINDOW,
        "rate_sha256": rate,
        "inputs": {},
    }


def _report(price="0.00123"):
    return {
        "tokens": {"cached_input": 100, "new_input": 200, "output": 4},
        "api_estimate_usd": price,
        "cost_eligible": False,
        "cost_hold_reasons": ["coverage-unavailable"],
    }


def _publish(repo, raw):
    report_id = validate_envelope(raw)["report_id"]
    path = repo / report_path(STORY, report_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return report_id, path, _commit(repo, "frozen report")


def test_exact_reopen_preserves_both_representations_after_repricing(
    target, capsys, monkeypatch
):
    repo, pin = target
    original = freeze_report(_manifest(pin), _report())
    assert original == freeze_report(_manifest(pin), _report())
    report_id, _, artifact_commit = _publish(repo, original)
    replacement = freeze_report(_manifest(pin, "b" * 64), _report("0.00892"))
    latest_id, _, latest_commit = _publish(repo, replacement)
    assert latest_id != report_id and latest_commit != artifact_commit

    def invalid_renderer(*_):
        raise AssertionError("Reopen invoked the current renderer")

    monkeypatch.setattr(
        "aitm_usage.effort.pinned_report._render_text", invalid_renderer
    )
    for mode in ("json", "text"):
        result = main(
            [
                "--project",
                str(PROJECT),
                "story-report-open",
                str(STORY),
                report_id,
                "--repository",
                str(repo),
                "--artifact-commit",
                artifact_commit,
                "--format",
                mode,
            ]
        )
        assert result == 0
        output = capsys.readouterr().out
        envelope = validate_envelope(original)
        if mode == "text":
            assert output == envelope["text"]
        else:
            assert json.loads(output) == envelope["report"]
    with pytest.raises(ReportUnavailable, match="missing"):
        reopen_pinned_report(repo, artifact_commit, PROJECT, STORY, latest_id)


def test_reopen_refuses_corrupt_artifact_and_scope_mismatch(target, capsys):
    repo, pin = target
    raw = freeze_report(_manifest(pin), _report())
    report_id, path, artifact_commit = _publish(repo, raw)
    with pytest.raises(ReportUnavailable, match="scope"):
        reopen_pinned_report(repo, artifact_commit, UUID(int=4), STORY, report_id)
    path.write_bytes(raw.replace(b"0.00123", b"0.00124"))
    corrupt_commit = _commit(repo, "corrupt artifact")
    args = [
        "--project",
        str(PROJECT),
        "story-report-open",
        str(STORY),
        report_id,
        "--repository",
        str(repo),
        "--artifact-commit",
        corrupt_commit,
        "--format",
        "text",
    ]
    assert main(args) == 3
    assert "unavailable" in capsys.readouterr().err
    assert reopen_pinned_report(
        repo, artifact_commit, PROJECT, STORY, report_id
    ) == json.loads(raw)


def test_cli_requires_exact_pin_database_only_on_private_commands(target, capsys):
    repo, pin = target
    report_id, _, _ = _publish(repo, freeze_report(_manifest(pin), _report()))
    assert (
        main(
            [
                "--project",
                str(PROJECT),
                "story-report-open",
                str(STORY),
                report_id,
                "--repository",
                str(repo),
                "--artifact-commit",
                "HEAD",
                "--format",
                "json",
            ]
        )
        == 2
    )
    assert "immutable" in capsys.readouterr().err
    with pytest.raises(SystemExit, match="2"):
        main(["--project", str(PROJECT), "report", "--story", str(STORY)])
    assert "--database" in capsys.readouterr().err


def test_validation_rejects_noncanonical_bytes_and_external_paths(target):
    _, pin = target
    raw = freeze_report(_manifest(pin), _report())
    with pytest.raises(ValueError):
        validate_envelope(raw + b" ")
    manifest = _manifest(pin)
    manifest["inputs"] = {"path": str(Path("/Users/private/session.jsonl"))}
    with pytest.raises(ValueError):
        freeze_report(manifest, _report())
