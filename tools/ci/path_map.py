"""Select PR tests using a reviewed base map and the two exact Git trees."""

import argparse
import json
import re
import subprocess
from hashlib import sha256
from pathlib import Path

MAP_PATH = "tools/ci/path_map.json"
SELECTOR_PATH = "tools/ci/path_map.py"
MAP_SCHEMA = "aitm.path-map/v2"
SELECTION_SCHEMA = "aitm.path-selection/v2"
_PACKAGE = "packages/aitm-usage/"
_EXTRA_CONSUMERS = {
    "tools/ci/pytest_evidence.py",
    "tools/ci/tests/test_cli_evidence.py",
}
_COMPARE_FILE_LIMIT = 300


def full_suite_needed(event, mode, cache_hit):
    """Whether a narrowed PR needs its extra full suite."""
    if event == "push" or mode == "full":
        return False
    if mode not in {"mapped", "checks"} or cache_hit not in {True, False}:
        return True
    return not cache_hit


def _digest(value, size):
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{size}}}", value)


def cache_key(pull_number, selection, *, base, policy):
    """A successful full run applies only to this PR and selection context."""
    key = selection.get("key") if isinstance(selection, dict) else None
    if (
        type(pull_number) is not int
        or pull_number <= 0
        or not _digest(base, 40)
        or not _digest(policy, 64)
        or not _digest(key, 64)
    ):
        raise ValueError("invalid full-suite cache key")
    return f"pr-{pull_number}-full-v2-{base}-{policy}-{key}"


def _json_digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def paths_from_compare(document):
    """Retain both names of a move and reject incomplete compare responses."""
    files = document.get("files") if isinstance(document, dict) else None
    if not isinstance(files, list) or len(files) >= _COMPARE_FILE_LIMIT:
        return None
    paths = []
    for item in files:
        if not isinstance(item, dict):
            return None
        name = item.get("filename")
        if not isinstance(name, str) or not name:
            return None
        paths.append(name)
        if "previous_filename" in item or item.get("status") in {"renamed", "copied"}:
            previous = item.get("previous_filename")
            if not isinstance(previous, str) or not previous:
                return None
            paths.append(previous)
    return paths


def _unsafe(path):
    return (
        not isinstance(path, str)
        or "\\" in path
        or any(part in {"", ".", ".."} for part in path.split("/"))
    )


def _names(values):
    return (
        isinstance(values, list)
        and all(isinstance(item, str) and item for item in values)
        and len(set(values)) == len(values)
    )


def _validate_map(document):
    if not isinstance(document, dict) or document.get("schema") != MAP_SCHEMA:
        raise ValueError("invalid path map")
    for key in ("full_prefixes", "full_names"):
        if not _names(document.get(key)):
            raise ValueError("invalid full-suite policy")
    rules = document.get("rules")
    children = document.get("children")
    if (
        not isinstance(rules, list)
        or not isinstance(children, dict)
        or not children
        or any(not label or _unsafe(path) for label, path in children.items())
    ):
        raise ValueError("invalid path map")
    declared = set()
    for rule in rules:
        path = rule.get("prefix") if isinstance(rule, dict) else None
        if (
            _unsafe(path)
            or path in declared
            or not isinstance(rule.get("reason"), str)
            or not rule["reason"]
            or "tests" in rule
            and (
                not _names(rule["tests"])
                or any(_unsafe(test) for test in rule["tests"])
            )
            or rule.get("tests")
            and not _digest(rule.get("consumer_digest"), 64)
        ):
            raise ValueError("invalid or duplicate path rule")
        declared.add(path)


def read_tree(revision):
    if not _digest(revision, 40):
        raise ValueError("an exact Git revision is required")
    data = subprocess.check_output(["git", "ls-tree", "--full-tree", "-rz", revision])
    entries = {}
    for line in data.split(b"\0")[:-1]:
        metadata, path = line.split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        entries[path.decode("utf-8")] = {"mode": mode, "type": kind, "sha": blob}
    return entries


def consumer_digest(entries, input_path):
    """Bind each declaration to the audited package and canonical CI consumers."""
    inventory = [
        [path, entry["mode"], entry["sha"]]
        for path, entry in sorted(entries.items())
        if path != input_path
        and entry["type"] != "tree"
        and (path.startswith(_PACKAGE) or path in _EXTRA_CONSUMERS)
    ]
    return _json_digest(inventory)


def _regular(entry):
    return entry.get("type") == "blob" and entry.get("mode") in {"100644", "100755"}


def _path_disposition(path, rule, base, candidate, document):
    if path.rsplit("/", 1)[-1] in document["full_names"] or path.startswith(
        tuple(document["full_prefixes"])
    ):
        return "full", "CI control or shared setup", []
    if rule is None:
        return "full", "unclassified input", []
    if "tests" not in rule:
        return "full", rule["reason"], []
    if base is None or candidate is None:
        return "full", "missing exact tree inputs", []
    prior, current = base.get(path, {}), candidate.get(path, {})
    if not (_regular(prior) and _regular(current) and prior["mode"] == current["mode"]):
        return "full", "added, removed or changed file type or mode", []
    tests = sorted(rule["tests"])
    if not tests:
        return "checks", rule["reason"], []
    if any(not _regular(candidate.get(test, {})) for test in tests):
        return "full", "selected test module is missing or non-regular", []
    if consumer_digest(base, path) != rule["consumer_digest"]:
        return "full", "audited consumer scope changed", []
    return "mapped", rule["reason"], tests


def select(paths, document, *, base=None, candidate=None):
    """Explain each changed path and fall back if any input is uncertain."""
    try:
        _validate_map(document)
    except ValueError:
        return _selection("full", [], [], {}, "invalid trusted path map")
    if not paths or any(_unsafe(path) for path in paths):
        return _selection("full", [], [], document["children"], "incomplete path input")
    rules = {rule["prefix"]: rule for rule in document["rules"]}
    evidence = []
    for path in sorted(set(paths)):
        disposition, reason, tests = _path_disposition(
            path, rules.get(path), base, candidate, document
        )
        evidence.append(
            {"path": path, "disposition": disposition, "reason": reason, "tests": tests}
        )
    full = any(row["disposition"] == "full" for row in evidence)
    tests = [] if full else sorted({test for row in evidence for test in row["tests"]})
    mode = "full" if full else "mapped" if tests else "checks"
    return _selection(mode, tests, evidence, document["children"])


def _selection(mode, tests, paths, children, reason=None):
    result = {
        "schema": SELECTION_SCHEMA,
        "mode": mode,
        "tests": tests,
        "key": "full"
        if mode == "full"
        else _json_digest({"mode": mode, "tests": tests}),
        "source": "base",
        "children": children,
        "paths": paths,
    }
    if reason:
        result["reason"] = reason
    return result


def _files(entries):
    return {
        path: {key: entry[key] for key in ("mode", "type", "sha")}
        for path, entry in entries.items()
        if entry["type"] != "tree"
    }


def select_trees(base, candidate, document):
    base = _files(base)
    candidate = _files(candidate)
    paths = [
        path
        for path in base.keys() | candidate.keys()
        if base.get(path) != candidate.get(path)
    ]
    return select(paths, document, base=base, candidate=candidate)


def select_candidate(base_oid, pull_number, base, candidate, document):
    selection = select_trees(base, candidate, document)
    if selection["mode"] != "full":
        policy = _json_digest([base[path]["sha"] for path in (SELECTOR_PATH, MAP_PATH)])
        selection["cache_key"] = cache_key(
            pull_number, selection, base=base_oid, policy=policy
        )
    return selection


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--changed-from", type=Path)
    source.add_argument("--compare", type=Path)
    source.add_argument("--base")
    parser.add_argument("--candidate")
    parser.add_argument("--pull-number", type=int)
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.map.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        document = None
    if args.base:
        if args.candidate is None or args.pull_number is None:
            parser.error("--base requires --candidate and --pull-number")
        result = select_candidate(
            args.base,
            args.pull_number,
            read_tree(args.base),
            read_tree(args.candidate),
            document,
        )
    else:
        paths = (
            paths_from_compare(json.loads(args.compare.read_text(encoding="utf-8")))
            if args.compare
            else args.changed_from.read_text(encoding="utf-8").splitlines()
        )
        result = select(paths, document)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
