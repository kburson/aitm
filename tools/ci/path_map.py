"""Choose pull-request tests from the trusted base path map.

The candidate tree does not choose the tests. Callers pass paths changed
between the pull-request base and the tested merge, plus the map blob from
that base. An absent map is handled by the workflow, which records mode full
without executing this file.
"""

import argparse
import json
from hashlib import sha256
from pathlib import Path

MAP_SCHEMA = "aitm.path-map/v1"
SELECTION_SCHEMA = "aitm.path-selection/v1"
_EXECUTABLE_SUFFIXES = {".py", ".sh", ".bash", ".zsh"}
_SOURCE_DATA_SUFFIXES = {".json", ".toml", ".yaml", ".yml"}
_COMPARE_FILE_LIMIT = 300


def full_suite_needed(event, mode, cache_hit):
    """Return whether a narrowed pull request must start the full suite.

    Push and mode full already run the full suite as the required check, so
    they do not start a second one. A mapped or checks pull request starts it
    only when this selection has no successful stamp. An unknown mode starts
    it, which fails closed.
    """

    if event == "push" or mode == "full":
        return False
    if mode not in {"mapped", "checks"} or cache_hit not in {True, False}:
        return True
    return not cache_hit


def cache_key(pull_number, selection):
    """Return the exact Actions cache key for one pull request and selection."""

    key = selection.get("key") if isinstance(selection, dict) else None
    if (
        type(pull_number) is not int
        or pull_number <= 0
        or not isinstance(key, str)
        or not key
        or any(character in key for character in "\n ,")
    ):
        raise ValueError("invalid full-suite cache key")
    return f"pr-{pull_number}-full-{key}"


def paths_from_compare(document):
    """Return compare filenames, or None when the response cannot narrow tests."""

    files = document.get("files") if isinstance(document, dict) else None
    if not isinstance(files, list) or len(files) >= _COMPARE_FILE_LIMIT:
        return None
    paths = []
    for item in files:
        name = item.get("filename") if isinstance(item, dict) else None
        if not isinstance(name, str) or not name:
            return None
        paths.append(name)
    return paths


def select(paths, document):
    """Return a full, mapped, or checks selection for the changed paths."""

    _validate_map(document)
    if not paths or any(_unsafe(path) for path in paths):
        return _selection("full", [], document)
    if any(_is_full(path, document) for path in paths):
        return _selection("full", [], document)
    chosen = []
    for path in paths:
        tests = _rule_tests(path, document)
        if tests is None:
            if _executable(path):
                return _selection("full", [], document)
            continue
        chosen.extend(tests)
    unique = sorted(set(chosen))
    return _selection("mapped" if unique else "checks", unique, document)


def _selection(mode, tests, document):
    body = {"mode": mode, "tests": tests}
    key = (
        "full"
        if mode == "full"
        else sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    return {
        "schema": SELECTION_SCHEMA,
        "mode": mode,
        "tests": tests,
        "key": key,
        "source": "base",
        "children": document["children"],
    }


def _validate_map(document):
    if not isinstance(document, dict) or document.get("schema") != MAP_SCHEMA:
        raise ValueError("invalid path map")
    prefixes = document.get("full_prefixes")
    names = document.get("full_names")
    rules = document.get("rules")
    self_tests = document.get("self_tests")
    children = document.get("children")
    if (
        not _strings(prefixes)
        or not _strings(names)
        or any("/" in name for name in names)
        or not isinstance(rules, list)
        or not _strings(self_tests)
        or any(
            pattern.count("*") != 1 or not pattern.endswith("*.py")
            for pattern in self_tests
        )
        or not isinstance(children, dict)
        or not children
        or any(
            not isinstance(label, str)
            or not isinstance(path, str)
            or not label
            or not path
            for label, path in children.items()
        )
    ):
        raise ValueError("invalid path map")
    for rule in rules:
        prefix = rule.get("prefix") if isinstance(rule, dict) else None
        tests = rule.get("tests") if isinstance(rule, dict) else None
        if not isinstance(prefix, str) or not prefix or not isinstance(tests, list):
            raise ValueError("invalid path map")
        if any(not isinstance(test, str) or not test for test in tests):
            raise ValueError("invalid path map")


def _strings(values):
    return (
        isinstance(values, list)
        and all(isinstance(item, str) and item for item in values)
        and len(values) == len(set(values))
    )


def _unsafe(path):
    return (
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or "\\" in path
        or path == ".."
        or path.startswith("../")
        or path.endswith("/..")
        or "/../" in path
        or "/./" in path
    )


def _is_full(path, document):
    name = path.rsplit("/", 1)[-1]
    return name in document["full_names"] or any(
        path.startswith(prefix) for prefix in document["full_prefixes"]
    )


def _rule_tests(path, document):
    best = None
    best_length = -1
    for rule in document["rules"]:
        prefix = rule["prefix"]
        matched = path.startswith(prefix) if prefix.endswith("/") else path == prefix
        if matched and len(prefix) > best_length:
            best = list(rule["tests"])
            best_length = len(prefix)
    for pattern in document["self_tests"]:
        if _glob_match(pattern, path) and len(pattern) > best_length:
            best = [path]
            best_length = len(pattern)
    return best


def _glob_match(pattern, path):
    head, _, tail = pattern.rpartition("*")
    if "*" in head or "*" in tail or "/" in tail or not head:
        return False
    rest = path[len(head) :]
    middle = rest[: -len(tail)] if tail else rest
    return (
        path.startswith(head)
        and middle != ""
        and "/" not in rest
        and rest.endswith(tail)
    )


def _executable(path):
    suffix = Path(path).suffix.lower()
    if suffix in _EXECUTABLE_SUFFIXES:
        return True
    return (
        path.startswith("packages/aitm-usage/src/") and suffix in _SOURCE_DATA_SUFFIXES
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--changed-from", type=Path)
    source.add_argument("--compare", type=Path)
    args = parser.parse_args(argv)
    document = json.loads(args.map.read_text(encoding="utf-8"))
    _validate_map(document)
    if args.compare is not None:
        paths = paths_from_compare(json.loads(args.compare.read_text(encoding="utf-8")))
        result = (
            _selection("full", [], document)
            if paths is None
            else select(paths, document)
        )
    else:
        paths = [
            line
            for line in args.changed_from.read_text(encoding="utf-8").splitlines()
            if line
        ]
        result = select(paths, document)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
