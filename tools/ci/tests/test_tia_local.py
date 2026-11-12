import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from tia import local
from tia.snapshot import LocalRequest, resolve

_SOURCE = Path(__file__).resolve().parents[3]
_PRODUCT = "packages/aitm-usage"
_SAMPLE = f"{_PRODUCT}/src/aitm_usage/sample.py"
_ACCOUNTING = f"{_PRODUCT}/tests/test_accounting.py"
_CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
_SERVICE = f"{_PRODUCT}/tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid"
_OTHER = f"{_PRODUCT}/tests/test_codex.py::test_unaffected"
_PARAM = _ACCOUNTING + "::test_value[1]"


def _git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.check_output(
        ["/usr/bin/git", "-C", str(repo), *args], env=env, text=True
    ).strip()


def _write(repo, name, contents):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def _node(repo, nodeid, label=None):
    path, name = nodeid.split("::", 1)
    path = repo / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        if label:
            stream.write(
                f"\ndef {name}(pytestconfig):\n"
                "    import subprocess, sys\n"
                "    import pytest_evidence\n"
                "    child = subprocess.Popen([sys.executable, '-c', 'pass'])\n"
                f"    pytest_evidence.record_child(pytestconfig, {label!r}, child.pid, child.wait())\n"
            )
        else:
            stream.write(f"\ndef {name}():\n    assert True\n")


@pytest.fixture
def checkout(tmp_path):
    repo = tmp_path / "work"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "trunk")
    _git(repo, "config", "user.name", "Fixture")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    for path in (
        "tools/ci/policy.json",
        "tools/ci/pytest_evidence.py",
        "tools/ci/tia/suites.json",
        "tools/ci/tia/edges.json",
        f"{_PRODUCT}/pyproject.toml",
        f"{_PRODUCT}/uv.lock",
    ):
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_SOURCE / path, repo / path)
    for path, text in {
        _SAMPLE: "VALUE = 1\n",
        f"{_PRODUCT}/src/aitm_usage/__init__.py": "",
        f"{_PRODUCT}/src/aitm_usage/cli.py": "def main():\n    return 0\n",
        _ACCOUNTING: (
            "import pytest\nfrom aitm_usage import sample\n\n"
            "@pytest.mark.parametrize('value', [1])\n"
            "def test_value(value):\n    assert sample.VALUE >= value\n"
        ),
    }.items():
        _write(repo, path, text)
    policy = json.loads((repo / "tools/ci/policy.json").read_bytes())
    for node in policy["required_tests"]:
        _node(repo, node, "service-one-shot" if node == _SERVICE else None)
    _node(repo, _CLI, "cli-help")
    _node(repo, _OTHER)
    for helper in policy["helpers"]:
        _node(repo, "tools/ci/tests/test_" + Path(helper).name + "::test_helper")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "fixture")
    return repo, _git(repo, "rev-parse", "HEAD")


def _cli(repo, base, flag, **injected):
    return subprocess.run(
        [sys.executable, "-m", "tools.ci.tia.local", "--base", base, flag],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(_SOURCE), **injected},
        text=True,
        capture_output=True,
        check=False,
    )


def _native():
    if sys.platform != "darwin" or shutil.which("uv") is None:
        pytest.skip("requires the local Darwin APFS and uv route")


def test_frozen_copy_rejects_changed_bytes_and_added_inputs(checkout, tmp_path):
    repo, base = checkout
    (repo / _SAMPLE).write_text("VALUE = 2\n")
    _git(repo, "add", _SAMPLE)
    (repo / _SAMPLE).write_text("VALUE = 3\n")
    _write(repo, "guide-é.md", "untracked\n")
    before, after = resolve(
        repo, LocalRequest("local/checkout", "local-effective", base)
    )
    old = local._freeze(before, tmp_path / "old")
    new = local._freeze(after, tmp_path / "new")
    assert (old.root / _SAMPLE).read_text() == "VALUE = 1\n"
    assert (new.root / _SAMPLE).read_text() == "VALUE = 3\n"
    assert (new.root / "guide-é.md").read_text() == "untracked\n"
    (new.root / _SAMPLE).write_text("VALUE = 4\n")
    with pytest.raises(local.Refusal, match="copy-drift"):
        new.verify()
    (new.root / _SAMPLE).write_text("VALUE = 3\n")
    _write(new.root, "unexpected.py", "")
    with pytest.raises(local.Refusal, match="copy-drift"):
        new.verify()


def test_local_dirty_snapshot_never_mints_hosted_proof(checkout):
    _native()
    repo, base = checkout
    _write(repo, _SAMPLE, "VALUE = 2\n")
    observed = _cli(
        repo,
        base,
        "--plan",
        PYTEST_ADDOPTS=f"--ignore={_ACCOUNTING}",
        PYTEST_PLUGINS="missing_ambient_plugin",
    )
    assert observed.returncode == 0, observed.stderr
    data = json.loads(observed.stdout)
    plan = data["plan"]
    assert data["result"] is None
    assert plan["provenance"] == "local_advisory"
    assert plan["mode"] == "selected"
    assert plan["snapshot"]["base"] == base
    assert plan["snapshot"]["before"] != plan["snapshot"]["after"]
    assert plan["changes"][0]["new"]["hex"] == _SAMPLE.encode().hex()
    assert any(row["nodeid"] == _PARAM for row in plan["selected"])
    assert not any(row["nodeid"] == _OTHER for row in plan["selected"])
    assert "hosted_collection_proof" not in observed.stdout
    assert (repo / _SAMPLE).read_text() == "VALUE = 2\n"


def test_selected_run_reports_real_failure_and_plan_identity(checkout):
    _native()
    repo, base = checkout
    _write(repo, _SAMPLE, "VALUE = 0\n")
    observed = _cli(repo, base, "--run")
    assert observed.returncode == 1, observed.stderr
    data = json.loads(observed.stdout)
    plan, result = data["plan"], data["result"]
    assert plan["mode"] == "selected"
    assert result["provenance"] == "local_advisory"
    assert result["status"] == "failed"
    assert result["exit_code"] == 1
    assert result["profiles"][0]["returncode"] == 1
    assert {row["nodeid"]: row["outcome"] for row in result["profiles"][0]["outcomes"]}[
        _PARAM
    ] == "failed"
    assert result["plan_sha256"] == local._digest(local._canonical(plan))


def test_selection_failure_runs_entire_applicable_suite(checkout, monkeypatch, capsys):
    _native()
    repo, base = checkout
    _write(repo, _SAMPLE, "VALUE = 2\n")
    monkeypatch.chdir(repo)

    def broken(*args):
        raise RuntimeError("selector fixture failure")

    monkeypatch.setattr(local, "select", broken)
    assert local.main(["--base", base, "--run"]) == 0
    data = json.loads(capsys.readouterr().out)
    plan, result = data["plan"], data["result"]
    assert plan["mode"] == "full"
    assert any("selector fixture failure" in reason for reason in plan["reasons"])
    assert result["status"] == "passed"
    selected = [row["nodeid"] for row in plan["selected"]]
    assert len(selected) == len(set(selected))
    assert {_PARAM, _OTHER, _CLI, _SERVICE} <= set(selected)
    assert result["executed"] == len(selected)
    assert {
        row["label"] for item in result["profiles"] for row in item["children"]
    } == {
        "cli-help",
        "service-one-shot",
    }


def test_stops_on_checkout_drift_before_execution(checkout, monkeypatch, capsys):
    _native()
    repo, base = checkout
    _write(repo, _SAMPLE, "VALUE = 2\n")
    monkeypatch.chdir(repo)
    build = local._plan

    def drift(*args):
        result = build(*args)
        _write(repo, _SAMPLE, "VALUE = 4\n")
        return result

    monkeypatch.setattr(local, "_plan", drift)
    assert local.main(["--base", base, "--run"]) == 2
    data = json.loads(capsys.readouterr().out)
    assert data["result"]["status"] == "refused"
    assert data["result"]["executed"] == 0
    assert any("snapshot-drift" in error for error in data["result"]["errors"])


def test_unsupported_capability_refuses_before_pytest(checkout, monkeypatch, capsys):
    repo, base = checkout
    monkeypatch.chdir(repo)
    monkeypatch.setattr(local.platform, "system", lambda: "Linux")
    assert local.main(["--base", base, "--run"]) == 2
    data = json.loads(capsys.readouterr().out)
    assert data["plan"]["mode"] == "unavailable"
    assert any("capability" in reason for reason in data["plan"]["reasons"])
    assert data["result"]["executed"] == 0


def test_missing_child_is_not_a_local_pass(checkout):
    _native()
    repo, base = checkout
    _write(repo, _CLI.split("::")[0], "def test_usage_console_help():\n    pass\n")
    observed = _cli(repo, base, "--run")
    assert observed.returncode == 2, observed.stderr
    result = json.loads(observed.stdout)["result"]
    assert result["status"] == "failed"
    assert any(
        "cli-help" in error
        for profile in result["profiles"]
        for error in profile["errors"]
    )


def test_bad_base_ref_reports_unavailable(checkout):
    repo, _ = checkout
    observed = _cli(repo, "--not-a-ref", "--plan")
    # An option-like value belongs after --base=, not in the Git option list.
    assert observed.returncode == 2
    observed = subprocess.run(
        [sys.executable, "-m", "tools.ci.tia.local", "--base=--not-a-ref", "--plan"],
        cwd=repo,
        env={**os.environ, "PYTHONPATH": str(_SOURCE)},
        text=True,
        capture_output=True,
        check=False,
    )
    assert observed.returncode == 2
    assert json.loads(observed.stdout)["plan"]["mode"] == "unavailable"


def test_copy_recreates_a_relative_symlink_in_its_own_directory(checkout, tmp_path):
    repo, base = checkout
    links = repo / "links"
    links.mkdir()
    (links / "sample").symlink_to("../" + _SAMPLE)
    _, after = resolve(repo, LocalRequest("local/checkout", "local-effective", base))
    frozen = local._freeze(after, tmp_path / "frozen-link")
    assert (frozen.root / "links/sample").is_symlink()
    assert (frozen.root / "links/sample").read_text() == "VALUE = 1\n"


def test_candidate_collection_that_mutates_copy_is_refused(checkout):
    _native()
    repo, base = checkout
    _write(
        repo,
        f"{_PRODUCT}/tests/conftest.py",
        "from pathlib import Path\n\n"
        "def pytest_sessionfinish(session):\n"
        f"    Path({_SAMPLE!r}).write_text('VALUE = 9\\n')\n",
    )
    result = _cli(repo, base, "--run")
    assert result.returncode == 2, result.stderr
    document = json.loads(result.stdout)
    assert document["plan"]["mode"] == "unavailable"
    assert any("copy-drift" in error for error in document["plan"]["reasons"])
    assert document["result"]["executed"] == 0
    assert (repo / _SAMPLE).read_text() == "VALUE = 1\n"


def test_nested_pytest_cache_stays_outside_bound_source(checkout, tmp_path):
    _native()
    repo, base = checkout
    helper = "tools/ci/tests/test_python_gate.py"
    _write(
        repo,
        helper,
        "import subprocess, sys\n\n"
        "def test_nested_pytest():\n"
        f"    subprocess.run([sys.executable, '-m', 'pytest', '-q', {_ACCOUNTING!r}], check=True)\n",
    )
    _, after = resolve(repo, LocalRequest("local/checkout", "local-effective", base))
    runtime = local._prepare(after, tmp_path / "nested-run")
    result = runtime.pytest("ci-helpers", (helper,), collect=False)
    assert result.returncode == 0, result.diagnostic
    runtime.verify()
    cache = runtime.root / _PRODUCT / ".pytest_cache"
    assert (cache / "v/cache/nodeids").is_file()
    assert not cache.resolve().is_relative_to(runtime.root)


def test_native_fixtures_avoid_the_shared_temporary_ancestor(
    checkout, tmp_path, monkeypatch, capsys
):
    repo, base = checkout
    cache = tmp_path / "home/Library/Caches"
    cache.mkdir(parents=True)
    shared = tmp_path / "shared"
    shared.mkdir()
    monkeypatch.chdir(repo)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    monkeypatch.setattr(local.tempfile, "tempdir", str(shared))
    observed = []

    def inspect(before, after, private):
        observed.append(private)
        return local._unavailable("fixture stops after allocating scratch"), None

    monkeypatch.setattr(local, "_capabilities", lambda _: None)
    monkeypatch.setattr(local, "_plan", inspect)
    assert local.main(["--base", base, "--plan"]) == 2
    assert json.loads(capsys.readouterr().out)["plan"]["provenance"] == "local_advisory"
    assert len(observed) == 1 and observed[0].parent == cache.resolve()
    assert not observed[0].exists()
