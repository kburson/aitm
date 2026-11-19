"""Exercise the working-tree report against actual Git repositories."""

import json
import os
import subprocess
import sys
import tracemalloc
from hashlib import sha256
from pathlib import Path

import pytest

from tools.ci import path_map
from tools.ci.tia import working_tree_report as report

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "packages/aitm-usage/src/aitm_usage/sources/grok_scope_hook.py"
MODULE = "packages/aitm-usage/tests/test_grok_scope_receipts.py"
ANCHOR = "8799c5a445dd4b51d499132e9a314b64796ae918"
INVENTORY_SHA = "812bc918dd9da7b413786454906d2ec8f486b5624bc8d1deecf9d546928d48e6"
TOOL_FILES = (
    "tools/ci/tia/working_tree_report.py",
    "tools/ci/tia/working_tree_obligations.json",
    "tools/ci/tests/test_tia_working_tree_report.py",
)


def git(repo, *args):
    env = {key: val for key, val in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return (
        subprocess.check_output(
            [
                "git",
                "-C",
                str(repo),
                "-c",
                "user.name=Test Fixture",
                "-c",
                "user.email=fixture@example.test",
                "-c",
                "commit.gpgsign=false",
                "-c",
                "core.hooksPath=/dev/null",
                *args,
            ],
            env=env,
        )
        .decode()
        .strip()
    )


def write(repo, path, data):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    write(repo, SOURCE, b"LIMIT = 10\n")
    write(repo, MODULE, b"def test_pinned():\n    assert True\n")
    write(repo, "docs/ci.md", b"# Fixtures\n")
    write(repo, "unrelated.txt", b"original\n")
    selector = Path(path_map.__file__).read_bytes()
    write(repo, path_map.SELECTOR_PATH, selector)
    module = {"mode": "100644", "type": "blob", "sha": git(repo, "hash-object", MODULE)}
    rules = {
        "schema": path_map.MAP_SCHEMA,
        "full_names": [],
        "full_prefixes": [],
        "children": {"cli-help": MODULE},
        "rules": [
            {
                "prefix": SOURCE,
                "reason": "Reviewed fixture declaration",
                "tests": [MODULE],
                "consumer_digest": path_map.consumer_digest(
                    {MODULE: module}, SOURCE, []
                ),
            }
        ],
    }
    map_bytes = json.dumps(rules).encode()
    write(repo, path_map.MAP_PATH, map_bytes)
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "Witness base")
    anchor = git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(report, "_ANCHOR_COMMIT", anchor)
    monkeypatch.setattr(report, "_ANCHOR_TREE", git(repo, "rev-parse", "HEAD^{tree}"))
    monkeypatch.setattr(report, "_MAP_SHA256", sha256(map_bytes).hexdigest())
    monkeypatch.setattr(report, "_SELECTOR_SHA256", sha256(selector).hexdigest())
    return repo, anchor


def append(repo, suffix, *, path=SOURCE):
    with (repo / path).open("ab") as stream:
        stream.write(suffix)


def unavailable(result, reason):
    assert result == {
        "schema": "aitm.tia-working-tree-report/v1",
        "mode": "unavailable",
        "reason": reason,
        "node_ids": [],
    }


@pytest.mark.parametrize("stage", ["unstaged", "staged", "mixed"])
def test_audited_comment_report_binds_effective_bytes(sandbox, stage):
    repo, base = sandbox
    append(repo, b" \t\n\t# local note\n")
    if stage != "unstaged":
        git(repo, "add", SOURCE)
    if stage == "mixed":
        append(repo, b"# worktree-only note\n")

    result = report.build_report(repo, base)
    assert result["mode"] == "pinned-mapped-obligations"
    assert (result["base_commit"], result["base_tree"]) == (
        base,
        git(repo, "rev-parse", "HEAD^{tree}"),
    )
    assert result["path"] == SOURCE and result["file_mode"] == "100644"
    assert result["content_sha256"] == sha256((repo / SOURCE).read_bytes()).hexdigest()
    assert (
        result["module"] == MODULE
        and result["consumer_reason"] == "Reviewed fixture declaration"
    )
    assert (
        result["candidate_inventory"] == result["impact_completeness"] == "unqualified"
    )
    assert len(result["node_ids"]) == len(set(result["node_ids"])) == 30
    assert result["node_ids"] == sorted(result["node_ids"])
    assert result["inventory_sha256"] == INVENTORY_SHA
    assert result["authority"]["anchor_commit"] == base
    assert result["authority"]["repository"] == "kburson/aitm"


@pytest.mark.parametrize(
    "suffix",
    [
        b"# comment\rpass\n",
        b"# comment\r\n",
        b"# comment\0\n",
        b"# comment\x0c\n",
        b"# comment\x0b\n",
        b"# comment\x7f\n",
        b"# comment\xc3\xa9\n",
        b"# missing newline",
        b"\n\t  \n",
        b"# title\nLIMIT = 11\n",
    ],
)
def test_nonqualifying_suffix_never_reports_ids(sandbox, suffix):
    repo, base = sandbox
    append(repo, suffix)
    unavailable(report.build_report(repo, base), "unsupported-change")


def test_multiline_comment_validation_limits_temporary_memory():
    base = b"LIMIT = 10\n"
    content = base + b"# local note\n\n" * 2048
    tracemalloc.start()
    try:
        assert report._matches_comment_suffix(content, len(base))
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 128 * 1024


def test_base_without_lf_refuses_comment_suffix(sandbox, monkeypatch):
    repo, _ = sandbox
    write(repo, SOURCE, b"LIMIT = 10")
    git(repo, "commit", "-qam", "No terminal LF")
    base = git(repo, "rev-parse", "HEAD")
    monkeypatch.setattr(report, "_ANCHOR_COMMIT", base)
    monkeypatch.setattr(report, "_ANCHOR_TREE", git(repo, "rev-parse", "HEAD^{tree}"))
    append(repo, b"\n# would append a new line\n")
    unavailable(report.build_report(repo, base), "unsupported-change")


def test_remote_url_does_not_supply_authority_or_change_snapshot(sandbox):
    repo, base = sandbox
    append(repo, b"# working\n")
    initial = report.build_report(repo, base)
    git(repo, "remote", "add", "origin", "https://example.test/other/project.git")
    assert report.build_report(repo, base) == initial


@pytest.mark.parametrize(
    "change", ["extra-untracked", "index-only", "rename", "delete", "symlink", "mode"]
)
def test_unqualified_changed_scope_refuses(sandbox, change):
    repo, base = sandbox
    append(repo, b"# working\n")
    if change == "extra-untracked":
        write(repo, "extra.txt", b"new\n")
    elif change == "index-only":
        write(repo, "unrelated.txt", b"staged new value\n")
        git(repo, "add", "unrelated.txt")
        write(repo, "unrelated.txt", b"original\n")
    elif change == "rename":
        (repo / SOURCE).rename(repo / "renamed.py")
    elif change == "delete":
        (repo / SOURCE).unlink()
    elif change == "symlink":
        (repo / SOURCE).unlink()
        (repo / SOURCE).symlink_to(repo / MODULE)
    else:
        (repo / SOURCE).chmod(0o755)
    result = report.build_report(repo, base)
    assert result["mode"] == "unavailable" and not result["node_ids"]
    assert result["reason"] in {"unsupported-change", "snapshot-unavailable"}


def test_baseline_and_clean_refusals(sandbox):
    repo, base = sandbox
    unavailable(report.build_report(repo, "HEAD"), "invalid-arguments")
    unavailable(report.build_report(repo, "0" * 40), "unqualified-base")
    unavailable(report.build_report(repo, base), "no-local-change")
    write(repo, "unrelated.txt", b"new committed value\n")
    git(repo, "commit", "-qam", "Unqualified baseline")
    append(repo, b"# working\n")
    unavailable(report.build_report(repo, base), "unqualified-base")
    unavailable(
        report.build_report(repo, git(repo, "rev-parse", "HEAD")), "unqualified-base"
    )


def test_report_works_on_qualified_delivery_tree(sandbox):
    repo, anchor = sandbox
    for path in TOOL_FILES:
        write(repo, path, b"# Fixture file; candidate tooling stays unread\n")
    append(repo, b"\nQualified additions.\n", path="docs/ci.md")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "The four delivery paths")
    base = git(repo, "rev-parse", "HEAD")
    append(repo, b"# working\n")
    result = report.build_report(repo, base)
    assert result["mode"] == "pinned-mapped-obligations"
    assert result["base_commit"] == base
    assert result["authority"]["anchor_commit"] == anchor
    append(repo, b"# Unadmitted current change\n", path=TOOL_FILES[0])
    unavailable(report.build_report(repo, base), "unsupported-change")


def test_drift_refuses_after_initial_snapshot(sandbox, monkeypatch):
    repo, base = sandbox
    append(repo, b"# working\n")
    resolve = report.resolve

    def change_after_resolve(*args):
        result = resolve(*args)
        append(repo, b"# callback drift\n")
        return result

    monkeypatch.setattr(report, "resolve", change_after_resolve)
    unavailable(report.build_report(repo, base), "snapshot-drift")


def test_inventory_and_selector_custody(sandbox, monkeypatch, tmp_path):
    repo, base = sandbox
    append(repo, b"# working\n")
    malformed = tmp_path / "invalid-inventory.json"
    malformed.write_text('["unexpected"]')
    with monkeypatch.context() as context:
        context.setattr(report, "_INVENTORY_PATH", malformed)
        unavailable(report.build_report(repo, base), "inventory-unavailable")
    monkeypatch.setattr(report, "_SELECTOR_SHA256", "0" * 64)
    unavailable(report.build_report(repo, base), "selector-unavailable")


def run_cli(*args, tracing=False, cwd=ROOT):
    flags = ["-X", "importtime"] if tracing else []
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-E",
            "-s",
            *flags,
            "-m",
            "tools.ci.tia.working_tree_report",
            *args,
        ],
        cwd=cwd,
        env=os.environ | {"PYTHONPATH": "/unqualified-pythonpath"},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    "args", [(), ("--repo", "."), ("--base", "HEAD"), ("--unknown",)]
)
def test_usage_errors_are_structured(args):
    child = run_cli(*args)
    assert child.returncode == 2
    unavailable(json.loads(child.stdout), "invalid-arguments")


def assert_report_imports(trace):
    modules = {
        line.rsplit("|", 1)[-1].strip()
        for line in trace.stderr.splitlines()
        if line.startswith("import time:")
    }
    assert "tools.ci.tia.snapshot" in modules
    for name in ("pytest", "aitm_usage", "path_map", "tools.ci.tia.local"):
        assert not any(
            module == name or module.startswith(name + ".") for module in modules
        )


def test_exact_cli_has_no_public_fixture_seam(sandbox):
    repo, base = sandbox
    args = ["--repo", str(repo), "--base", base]
    child = run_cli(*args)
    assert child.returncode == 2
    unavailable(json.loads(child.stdout), "snapshot-unavailable")

    trace = run_cli(*args, tracing=True)
    assert trace.returncode == 2
    assert_report_imports(trace)


def test_help_is_human_readable():
    child = run_cli("--help")
    assert child.returncode == 0
    assert "--repo CHECKOUT" in child.stdout


def test_cli_startup_leaves_a_fresh_tooling_checkout_unchanged(tmp_path):
    for path in (
        "tools/ci/path_map.py",
        "tools/ci/tia/snapshot.py",
        "tools/ci/tia/working_tree_report.py",
    ):
        write(tmp_path, path, (ROOT / path).read_bytes())
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}

    child = run_cli("--help", cwd=tmp_path)

    assert child.returncode == 0
    assert {path.relative_to(tmp_path) for path in tmp_path.rglob("*")} == before


def test_exact_cli_on_production_anchor(tmp_path):
    target = tmp_path / "target"
    subprocess.run(
        ["git", "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(target)],
        check=True,
        capture_output=True,
    )
    git(target, "checkout", "-q", "--detach", ANCHOR)
    args = ["--repo", str(target), "--base", ANCHOR]
    bad_base = run_cli("--repo", str(target), "--base", "0" * 40)
    assert bad_base.returncode == 2
    unavailable(json.loads(bad_base.stdout), "unqualified-base")
    initial = run_cli(*args)
    assert initial.returncode == 2
    unavailable(json.loads(initial.stdout), "no-local-change")

    append(target, b"\n# Scratch-only local selection probe for #352.\n")
    before = git(target, "status", "--porcelain=v1")
    body = (target / SOURCE).read_bytes()
    child = run_cli(*args)
    assert child.returncode == 0, child.stderr
    result = json.loads(child.stdout)
    assert result["mode"] == "pinned-mapped-obligations"
    assert result["inventory_sha256"] == INVENTORY_SHA
    assert len(result["node_ids"]) == 30
    assert all(node.startswith(MODULE + "::") for node in result["node_ids"])
    assert result["authority"]["anchor_commit"] == ANCHOR
    trace = run_cli(*args, tracing=True)
    assert trace.returncode == 0 and json.loads(trace.stdout) == result
    assert_report_imports(trace)
    assert git(target, "rev-parse", "HEAD") == ANCHOR
    assert git(target, "status", "--porcelain=v1") == before == f"M {SOURCE}"
    assert (target / SOURCE).read_bytes() == body


def test_exact_cli_qualifies_post_supervisor_anchor(tmp_path):
    target = tmp_path / "target"
    git(tmp_path, "clone", "-q", "--shared", "--no-checkout", str(ROOT), str(target))
    anchor = "4ae28dba1493c2171bd8097e58195198c4001a51"
    git(target, "checkout", "-q", "--detach", anchor)

    append(target, b"\n# Requalification probe.\n")
    child = run_cli("--repo", str(target), "--base", anchor)
    assert child.returncode == 0, child.stdout
    result = json.loads(child.stdout)
    assert result["authority"]["anchor_commit"] == anchor
    assert result["authority"]["consumer_sha256"] == (
        "709aa6dce1bd3f25d169b8cbde4af009275cfe226e9a752c0260ea8e58e8560f"
    )
    assert len(result["node_ids"]) == (38 if sys.platform == "linux" else 36)
    assert all(node.startswith(MODULE + "::") for node in result["node_ids"])

    write(target, "unrelated.txt", b"Not part of the qualified release.\n")
    git(target, "add", "unrelated.txt")
    git(target, "commit", "-qm", "Unrelated committed path")
    child = run_cli("--repo", str(target), "--base", git(target, "rev-parse", "HEAD"))
    assert child.returncode == 2
    unavailable(json.loads(child.stdout), "unqualified-base")
