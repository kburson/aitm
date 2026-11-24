"""Build the #423 single-variable candidate trees, without publishing seed refs."""

import os
from pathlib import Path
import subprocess

BASE = "45db935ac73911b95320a3e38d19f177cedd4fd2"
PACKAGE = Path("packages/aitm-usage")
WATCH = PACKAGE / "src/aitm_usage/host_watch.py"
SCAN = PACKAGE / "src/aitm_usage/sources/scan.py"
WATCH_TEST = str(PACKAGE / "tests/test_host_watch.py")
INVENTORY_TEST = str(PACKAGE / "tests/test_monitor_policy_unit.py")
ORIGINAL = "test_earlier_handoff_holds_later_handoff_with_stale_generation"
ADDED = "test_spike_423_added_inventory"
RENAMED = "test_spike_423_renamed_inventory"
WITNESS = WATCH_TEST + "::test_native_watch_reports_change_and_retires_resources"
SIGNATURES = {
    "leaf": 'item.reason == "startup"',
    "transitive": "WatchError: Authorized watch root is unavailable",
}
MODES = {
    "clean": "full",
    "leaf": "selected",
    "transitive": "full",
    "shared": "full",
    "docs": "full",
    "add": "selected",
    "rename": "full",
    "delete": "full",
    "dynamic": "full",
}
IDENTITY = dict(
    GIT_AUTHOR_NAME="AITM spike #423",
    GIT_AUTHOR_EMAIL="experiment@example.invalid",
    GIT_COMMITTER_NAME="AITM spike #423",
    GIT_COMMITTER_EMAIL="experiment@example.invalid",
    GIT_AUTHOR_DATE="2026-11-24T13:00:00Z",
    GIT_COMMITTER_DATE="2026-11-24T13:00:00Z",
)


def git(repo, *args, input=None):
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, input=input,
        env=os.environ | IDENTITY,
    ).strip()


def replace_once(path, original, edited):
    text = path.read_text()
    if text.count(original) != 1:
        raise ValueError(f"expected one candidate mutation anchor in {path.name}")
    path.write_text(text.replace(original, edited))


def append(path, value):
    with path.open("a") as stream:
        stream.write(value)


def edit(case, repo):
    if case == "clean":
        return None
    if case == "leaf":
        replace_once(repo / WATCH, 'WatchKind.RECONCILE, "startup")',
                     'WatchKind.RECONCILE, "seeded-startup")')
        return WATCH
    if case == "transitive":
        replace_once(repo / SCAN, 'if not path.is_absolute() or ".." in path.parts:\n        raise _ChangedSource\n    fd = os.open(path.anchor',
                     'if not path.is_absolute() or ".." in path.parts or path.name == "watched":\n        raise _ChangedSource\n    fd = os.open(path.anchor')
        return SCAN
    if case == "shared":
        path = PACKAGE / "tests/conftest.py"
        append(repo / path, '\n\n@pytest.fixture\ndef spike_423_unused_fixture():\n    return "spike-423"\n')
        return path
    if case == "docs":
        path = Path("README.md")
        append(repo / path, "\nThis sentence is an isolated documentation change for the TIA validation spike.\n")
        return path
    if case == "dynamic":
        replace_once(repo / WATCH, "import errno\n", "import errno\nimport importlib\n")
        replace_once(repo / WATCH, "from .types import SourceRef\n", 'from .types import SourceRef\n\nimportlib.import_module("".join(("co", "llections")))\n')
        return WATCH
    path = repo / INVENTORY_TEST
    if case == "add":
        append(path, f"\n\ndef {ADDED}():\n    assert _handoff_events()[0].before_generation == 0\n")
    elif case == "rename":
        replace_once(path, f"def {ORIGINAL}(", f"def {RENAMED}(")
    elif case == "delete":
        text = path.read_text()
        start = text.index(f"def {ORIGINAL}(")
        end = text.index("def assert_same_target_conflict(", start)
        path.write_text(text[:start] + text[end:])
    else:
        raise ValueError(f"unknown case {case}")
    return Path(INVENTORY_TEST)


def make_case(source, repo, case):
    git(source, "clone", "--quiet", "--shared", "--no-checkout", str(source), str(repo))
    git(repo, "checkout", "--quiet", "--detach", BASE)
    path = edit(case, repo)
    if path is not None:
        git(repo, "add", "--", str(path))
        git(repo, "diff", "--cached", "--check")
    tree = git(repo, "write-tree")
    head = git(repo, "commit-tree", tree, "-p", BASE, "-m", f"#423 candidate {case}")
    tested = git(repo, "commit-tree", tree, "-p", BASE, "-p", head, "-m", f"#423 tested {case}")
    git(repo, "checkout", "--quiet", "--detach", tested)
    expected = str(path) if path else ""
    if git(repo, "diff", "--name-only", BASE, tested) != expected:
        raise ValueError(f"candidate {case} unexpectedly changed more than {expected}")
    if git(repo, "show", "-s", "--format=%P", tested) != f"{BASE} {head}":
        raise ValueError("incorrect synthetic merge parent order")
    return {"base": BASE, "head": head, "tested": tested, "tree": tree, "path": expected}


def clone_lane(repo, dest, oid):
    git(repo, "clone", "--quiet", "--shared", "--no-checkout", str(repo), str(dest))
    git(dest, "checkout", "--quiet", "--detach", oid)
    if git(dest, "rev-parse", "HEAD") != oid:
        raise ValueError("independent lane identity mismatch")
