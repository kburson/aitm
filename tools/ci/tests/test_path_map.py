import json
from pathlib import Path

import pytest
from path_map import (
    cache_key,
    full_suite_needed,
    main,
    paths_from_compare,
    select,
)

MAP = json.loads(
    (Path(__file__).resolve().parents[1] / "path_map.json").read_text(encoding="utf-8")
)
WORKFLOW = (
    Path(__file__).resolve().parents[3] / ".github" / "workflows" / "ci.yml"
).read_text(encoding="utf-8")
GROK = "packages/aitm-usage/src/aitm_usage/sources/grok.py"
GROK_TEST = "packages/aitm-usage/tests/test_grok.py"
FIXTURE = "packages/aitm-usage/tests/fixtures/grok/headless.json"


def test_maintained_map_covers_the_grok_fixture_and_falls_back():
    fixture = select([FIXTURE], MAP)
    assert fixture["mode"] == "mapped"
    assert fixture["tests"] == [GROK_TEST]
    assert fixture["source"] == "base"
    assert select([GROK, "docs/ci.md"], MAP)["tests"] == [GROK_TEST]
    assert select(["docs/ci.md", "README.md"], MAP)["mode"] == "checks"
    assert select(["packages/aitm-usage/tests/test_grok.py"], MAP)["tests"] == [
        GROK_TEST
    ]
    for path in (
        "tools/ci/path_map.json",
        "tools/ci/path_map.py",
        ".github/workflows/ci.yml",
        "packages/aitm-usage/tests/conftest.py",
        "packages/aitm-usage/pyproject.toml",
        "packages/aitm-usage/src/aitm_usage/cli.py",
        "packages/aitm-usage/src/aitm_usage/rates/2026-11-09.json",
        "../secret.py",
        "",
    ):
        assert select([path] if path else [], MAP)["mode"] == "full"
    assert (
        select(["docs/ci.md", "packages/aitm-usage/src/aitm_usage/cli.py"], MAP)["mode"]
        == "full"
    )


def test_selection_key_ignores_path_order_and_changes_with_tests():
    forward = select([GROK, "docs/ci.md"], MAP)
    backward = select(["docs/ci.md", GROK], MAP)
    assert forward["key"] == backward["key"]
    assert len(forward["key"]) == 64
    other = select(
        ["packages/aitm-usage/src/aitm_usage/ledger.py"],
        MAP,
    )
    assert other["tests"] == ["packages/aitm-usage/tests/test_ledger.py"]
    assert other["key"] != forward["key"]


@pytest.mark.parametrize(
    ("event", "mode", "hit", "needed"),
    [
        ("push", "mapped", False, False),
        ("pull_request", "full", False, False),
        ("pull_request", "mapped", True, False),
        ("pull_request", "mapped", False, True),
        ("pull_request", "checks", False, True),
        ("pull_request", "checks", True, False),
        ("pull_request", "unknown", False, True),
        ("pull_request", "mapped", None, True),
    ],
)
def test_full_suite_runs_once_per_narrowed_selection(event, mode, hit, needed):
    assert full_suite_needed(event, mode, hit) is needed


def test_cache_key_is_exact_and_rejects_unsafe_values():
    selection = select(["docs/ci.md"], MAP)
    assert cache_key(12, selection) == f"pr-12-full-{selection['key']}"
    with pytest.raises(ValueError):
        cache_key(0, selection)
    with pytest.raises(ValueError):
        cache_key(12, {"key": "bad key"})


def test_compare_limit_cannot_narrow_the_suite(tmp_path, capsys):
    assert paths_from_compare({"files": [{"filename": GROK}]}) == [GROK]
    assert paths_from_compare({"files": [{}]}) is None
    assert paths_from_compare({"files": [{"filename": GROK}] * 300}) is None
    compare = tmp_path / "compare.json"
    changed = tmp_path / "changed.txt"
    path = tmp_path / "map.json"
    path.write_text(json.dumps(MAP), encoding="utf-8")
    compare.write_text(json.dumps({"files": [{"filename": FIXTURE}]}), encoding="utf-8")
    assert main(["--map", str(path), "--compare", str(compare)]) == 0
    assert json.loads(capsys.readouterr().out)["tests"] == [GROK_TEST]
    compare.write_text(
        json.dumps({"files": [{"filename": "x.py"}] * 300}), encoding="utf-8"
    )
    assert main(["--map", str(path), "--compare", str(compare)]) == 0
    assert json.loads(capsys.readouterr().out)["mode"] == "full"
    changed.write_text("README.md\n", encoding="utf-8")
    assert main(["--map", str(path), "--changed-from", str(changed)]) == 0
    assert json.loads(capsys.readouterr().out)["mode"] == "checks"
    path.write_text(
        '{"schema":"aitm.path-map/v1","rules":[{"prefix":1}]}', encoding="utf-8"
    )
    with pytest.raises(ValueError):
        main(["--map", str(path), "--changed-from", str(changed)])


def test_workflow_uses_the_base_selector_and_cancels_a_superseded_run():
    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in WORKFLOW
    assert 'git show "$BASE:tools/ci/path_map.py"' in WORKFLOW
    assert 'git show "$BASE:tools/ci/path_map.json"' in WORKFLOW
    assert WORKFLOW.count("python3 tools/ci/path_map.py") == 1
    assert "steps.full-once.outputs.cache-hit != 'true'" in WORKFLOW
    assert "actions/cache/restore@5a3ec84eff668545956fd18022155c47e93e2684" in WORKFLOW
    assert "actions/cache/save@5a3ec84eff668545956fd18022155c47e93e2684" in WORKFLOW
    assert "pr-${PR_NUMBER}-full-${key}" in WORKFLOW
