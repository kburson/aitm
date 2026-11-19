"""Exact-input advisory CLI controls using disposable Git checkouts."""

import json
import subprocess

import pytest

from tools.ci.tia import local, probe


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


@pytest.fixture
def git_checkout(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "commit.gpgsign", "false")
    source = repo / "example.py"
    source.write_text("VALUE = 1\n")
    git(repo, "add", "example.py")
    git(repo, "commit", "--no-verify", "-qm", "base")
    return repo, source, git(repo, "rev-parse", "HEAD")


def argv(repo, base, kind):
    return ["--repo", str(repo), "--parent", base, "--input", kind]


@pytest.mark.parametrize("kind, extra", [("pr", []), ("head", ["--pr-head", "0" * 40])])
def test_ambiguous_input_options_are_unavailable(git_checkout, capsys, kind, extra):
    repo, _, base = git_checkout
    assert probe.main(argv(repo, base, kind) + extra) == 2
    plan = json.loads(capsys.readouterr().out)["plan"]
    assert plan["mode"] == "unavailable"
    assert plan["selected"] == []


def test_cli_reports_exact_index_identity(git_checkout, monkeypatch, capsys):
    repo, source, base = git_checkout
    source.write_text("VALUE = 2\n")
    git(repo, "add", "example.py")
    source.write_text("VALUE = 3\n")
    (repo / "untracked.py").touch()

    def inspect(before, after, private, *, inspected_checkout):
        assert inspected_checkout == repo.resolve()
        assert not private.is_relative_to(inspected_checkout)
        assert after.read_content(b"example.py") == b"VALUE = 2\n"
        assert [entry.path for entry in after.entries] == [b"example.py"]
        return {
            "mode": "selected",
            "selected": [],
            "snapshot": local._snapshot_data(before, after),
        }, None

    monkeypatch.setattr(probe, "_capabilities", lambda _: None)
    monkeypatch.setattr(probe, "_plan", inspect)
    assert probe.main(argv(repo, base, "index")) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["schema"] == "aitm.tia-advisory-probe/v1"
    assert result["provenance"] == "local_advisory"
    identity = result["plan"]["snapshot"]
    assert identity["input"] == "index"
    assert identity["base"] == base
    assert len(identity["endpoint"]["index_digest"]) == 64


def test_endpoint_drift_discards_the_planned_assignment(
    git_checkout, monkeypatch, capsys
):
    repo, _, base = git_checkout

    def move_head(*args, **kwargs):
        git(repo, "commit", "--allow-empty", "--no-verify", "-qm", "moved")
        return {"mode": "selected", "selected": [{"nodeid": "discard-me"}]}, None

    monkeypatch.setattr(probe, "_capabilities", lambda _: None)
    monkeypatch.setattr(probe, "_plan", move_head)
    assert probe.main(argv(repo, base, "head")) == 2
    plan = json.loads(capsys.readouterr().out)["plan"]
    assert plan["mode"] == "unavailable"
    assert plan["selected"] == []
    assert "snapshot-drift" in plan["reasons"][0]


def test_missing_candidate_inventory_never_returns_a_list(
    git_checkout, monkeypatch, capsys
):
    repo, _, base = git_checkout

    def refuse(*args, **kwargs):
        raise local.Refusal("fixture inventory absent")

    monkeypatch.setattr(probe, "_capabilities", lambda _: None)
    monkeypatch.setattr(local, "_collect", refuse)
    assert probe.main(argv(repo, base, "head")) == 2
    plan = json.loads(capsys.readouterr().out)["plan"]
    assert plan["mode"] == "unavailable"
    assert plan["selected"] == []
    assert "candidate-inventory" in plan["reasons"][0]
