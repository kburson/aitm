import json
from pathlib import Path

import pytest
from path_map import (
    cache_key,
    full_suite_needed,
    main,
    paths_from_compare,
    select,
    select_trees,
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


def test_maintained_map_falls_back_for_unqualified_or_control_inputs():
    assert {rule["prefix"]: rule.get("tests") for rule in MAP["rules"]}[FIXTURE] == [
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
        "packages/aitm-usage/tests/test_grok.py",
        "../secret.py",
        "",
    ):
        selection = select([path] if path else [], MAP)
        assert selection["mode"] == "full"
        assert selection.get("reason") or selection["paths"][0]["reason"]
    assert select([LEDGER], MAP)["mode"] == "full"


def test_selection_explanation_is_ordered_and_key_tracks_selection(audit):
    base, rules = audit
    candidate = {**base, FIXTURE: _entry("f"), "README.md": _entry("f")}
    a = select([FIXTURE, "README.md"], rules, base=base, candidate=candidate)
    b = select(["README.md", FIXTURE], rules, base=base, candidate=candidate)
    assert a == b
    assert len(a["key"]) == 64
    assert select_trees(base, {**base, HOOK: _entry("f")}, rules)["key"] != a["key"]


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


def test_compare_limit_cannot_narrow_the_suite(tmp_path, capsys):
    assert paths_from_compare({"files": [{"filename": GROK}]}) == [GROK]
    assert paths_from_compare({"files": [{}]}) is None
    assert paths_from_compare({"files": [{"filename": GROK}] * 300}) is None
    renamed = {
        "filename": "docs/moved.md",
        "previous_filename": ".github/workflows/ci.yml",
        "status": "renamed",
    }
    paths = paths_from_compare({"files": [renamed]})
    assert paths == ["docs/moved.md", ".github/workflows/ci.yml"]
    assert select(paths, MAP)["mode"] == "full"
    assert select(["docs/moved.md"], MAP)["mode"] == "full"
    assert (
        paths_from_compare(
            {"files": [{"filename": "docs/moved.md", "status": "renamed"}]}
        )
        is None
    )
    assert (
        paths_from_compare(
            {"files": [{"filename": "docs/moved.md", "previous_filename": ""}]}
        )
        is None
    )
    hidden = {
        "filename": "README.md",
        "previous_filename": "packages/aitm-usage/src/aitm_usage/cli.py",
        "status": "renamed",
    }
    assert select(paths_from_compare({"files": [hidden]}), MAP)["mode"] == "full"
    compare = tmp_path / "compare.json"
    changed = tmp_path / "changed.txt"
    path = tmp_path / "map.json"
    path.write_text(json.dumps(MAP), encoding="utf-8")
    compare.write_text(json.dumps({"files": [{"filename": FIXTURE}]}), encoding="utf-8")
    assert main(["--map", str(path), "--compare", str(compare)]) == 0
    assert json.loads(capsys.readouterr().out)["mode"] == "full"
    compare.write_text(
        json.dumps({"files": [{"filename": "x.py"}] * 300}), encoding="utf-8"
    )
    assert main(["--map", str(path), "--compare", str(compare)]) == 0
    assert json.loads(capsys.readouterr().out)["mode"] == "full"
    changed.write_text("README.md\n", encoding="utf-8")
    assert main(["--map", str(path), "--changed-from", str(changed)]) == 0
    assert json.loads(capsys.readouterr().out)["mode"] == "full"
    path.write_text(
        '{"schema":"aitm.path-map/v1","rules":[{"prefix":1}]}', encoding="utf-8"
    )
    assert main(["--map", str(path), "--changed-from", str(changed)]) == 0
    assert json.loads(capsys.readouterr().out)["reason"] == "invalid trusted path map"


def test_workflow_uses_the_base_selector_and_cancels_a_superseded_run():
    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in WORKFLOW
    assert 'git show "$BASE:tools/ci/path_map.py"' in WORKFLOW
    assert 'git show "$BASE:tools/ci/path_map.json"' in WORKFLOW
    assert WORKFLOW.count('--base "$BASE" --candidate "$GITHUB_SHA"') == 2
    assert WORKFLOW.index("Restore the full-suite stamp") < WORKFLOW.index(
        "Run parallel behavior suite and retain exact coverage"
    )
    assert "steps.full-once.outputs.hit != 'true'" in WORKFLOW
    assert "steps.qualify.outputs.cache_key" in WORKFLOW
    diff = "git diff --name-only --no-renames --diff-filter=ACDMRTUXB"
    assert WORKFLOW.count(diff) == 2
    assert f'{diff} "$BASE" FETCH_HEAD' in WORKFLOW
    assert f'{diff} "$BASE" HEAD' in WORKFLOW
    assert "refs/pull/${PR_NUMBER}/merge" in WORKFLOW
    assert 'test "$(git rev-parse FETCH_HEAD)" = "$GITHUB_SHA"' in WORKFLOW
    assert "compare/${BASE}" not in WORKFLOW


LEDGER = "packages/aitm-usage/src/aitm_usage/ledger.py"
HOOK = "packages/aitm-usage/src/aitm_usage/sources/grok_scope_hook.py"
HOOK_TEST = "packages/aitm-usage/tests/test_grok_scope_receipts.py"


def _entry(oid, mode="100644"):
    return {"mode": mode, "type": "blob", "sha": oid * 40}


@pytest.fixture
def audit():
    entries = {
        GROK_TEST: _entry("a"),
        FIXTURE: _entry("b"),
        HOOK_TEST: _entry("c"),
        HOOK: _entry("d"),
        "README.md": _entry("e"),
    }
    rules = {
        "schema": "aitm.path-map/v2",
        "full_prefixes": [".github/", "tools/ci/"],
        "full_names": ["conftest.py"],
        "rules": [
            {"prefix": "README.md", "tests": [], "reason": "repository documentation"},
            {"prefix": LEDGER, "reason": "shared Ledger consumers"},
            {
                "prefix": FIXTURE,
                "tests": [GROK_TEST],
                "reason": "Grok fixture reader",
                "consumer_digest": "b5c9a1afeff9eb53c612bb862041f82162bfd05927f44b28ae1abdead732fbd2",
            },
            {
                "prefix": HOOK,
                "tests": [HOOK_TEST],
                "reason": "scope hook consumers",
                "consumer_digest": "d2b30c3d23336a6f158798fe1ff108772b0074a8da0a9f2932fcc62ca5e15a46",
            },
        ],
        "self_tests": [],
        "children": MAP["children"],
    }
    return entries, rules


def test_qualified_fixture_and_source_are_explained(audit):
    base, rules = audit
    for path, tests, reason in (
        (FIXTURE, [GROK_TEST], "Grok fixture reader"),
        (HOOK, [HOOK_TEST], "scope hook consumers"),
    ):
        result = select_trees(base, {**base, path: _entry("f")}, rules)
        assert result["mode"] == "mapped"
        assert result["tests"] == tests
        assert result["paths"] == [
            {"path": path, "disposition": "mapped", "reason": reason, "tests": tests}
        ]


def test_unknown_path_forces_full_and_known_docs_preserve_selection(audit):
    base, rules = audit
    base["notes.md"] = _entry("a")
    docs = {**base, "README.md": _entry("f")}
    mapped = {**docs, FIXTURE: _entry("f")}
    assert select_trees(base, docs, rules)["mode"] == "checks"
    assert select_trees(base, mapped, rules)["tests"] == [GROK_TEST]
    for candidate in (
        {**base, "notes.md": _entry("b")},
        {**mapped, "notes.md": _entry("b")},
    ):
        result = select_trees(base, candidate, rules)
        assert result["mode"] == "full"
        assert any(
            row["path"] == "notes.md" and row["disposition"] == "full"
            for row in result["paths"]
        )
    assert select([LEDGER], rules)["paths"][0]["reason"] == "shared Ledger consumers"


def test_changed_consumers_and_moves_force_full(audit):
    base, rules = audit
    changed_base = {
        **base,
        "packages/aitm-usage/tests/test_new_consumer.py": _entry("f"),
    }
    assert (
        select_trees(changed_base, {**changed_base, FIXTURE: _entry("c")}, rules)[
            "mode"
        ]
        == "full"
    )
    deleted = {path: entry for path, entry in base.items() if path != FIXTURE}
    moved = {**deleted, "docs/moved.json": base[FIXTURE]}
    assert select_trees(base, moved, rules)["mode"] == "full"
    assert [row["path"] for row in select_trees(base, moved, rules)["paths"]] == [
        "docs/moved.json",
        FIXTURE,
    ]
    assert (
        select_trees(base, {**base, FIXTURE: _entry("f", "120000")}, rules)["mode"]
        == "full"
    )
    result = select_trees(
        base, {**base, GROK_TEST: _entry("b"), FIXTURE: _entry("f")}, rules
    )
    assert result["mode"] == "full"


def test_cache_key_is_exact_and_rejects_unsafe_values():
    selected = {"key": "c" * 64}
    key = cache_key(12, selected, base="a" * 40, policy="b" * 64)
    assert key == f"pr-12-full-v2-{'a' * 40}-{'b' * 64}-{'c' * 64}"
    assert cache_key(13, selected, base="a" * 40, policy="b" * 64) != key
    assert cache_key(12, selected, base="d" * 40, policy="b" * 64) != key
    assert cache_key(12, selected, base="a" * 40, policy="d" * 64) != key
    assert cache_key(12, {"key": "d" * 64}, base="a" * 40, policy="b" * 64) != key
    with pytest.raises(ValueError):
        cache_key(12, selected, base="wrong", policy="b" * 64)


@pytest.mark.parametrize(
    "control", ["conftest.py", "packages/conftest.py", ".github/workflows/ci.yml"]
)
def test_landed_shared_controls_expire_the_consumer_audit(audit, control):
    base, rules = audit
    base[control] = _entry("f")
    current = {**base, FIXTURE: _entry("c")}
    result = select_trees(base, current, rules)
    assert result["mode"] == "full"
    assert result["paths"][0]["reason"] == "audited consumer scope changed"


def test_stamp_is_published_after_attested_success_and_bound_to_a_completed_run():
    assert WORKFLOW.index("- name: Publish the full-suite stamp") > WORKFLOW.index(
        "Copy the bundle to the evidence directory"
    )
    assert "actions/artifacts?name=" in WORKFLOW
    assert '.status == "completed" and .conclusion == "success"' in WORKFLOW
    assert (
        "prior_workflow" in WORKFLOW
        and '"$prior_workflow" == "$trusted_workflow"' in WORKFLOW
    )
