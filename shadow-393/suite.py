"""Select one declared suite against the #383 exact snapshot pair."""
import ast
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from tools.ci.tia.snapshot import ProbeRequest, SnapshotUncertain, resolve


def _outside_test_body(source, name):
    module = ast.parse(source)
    target, = (node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == name)
    lines = source.splitlines(keepends=True)
    first = target.body[0].lineno - 1
    if first <= target.lineno - 1:
        raise ValueError("single-line function body")
    return b"".join(lines[:first] + lines[target.end_lineno:])


def _path(entry):
    return None if entry is None else entry.path.decode("utf-8", "backslashreplace")


def select(repo: Path, case, policy_path):
    declaration = policy_path.read_bytes()
    policy = json.loads(declaration)
    assert policy["schema"] == "aitm.pytest-suite-inputs/v1"
    authority = ProbeRequest(
        "local/checkout", "pr", case["base"], case["head"], case["tested"], case["tree"]
    )
    result = {
        "schema": "aitm.suite-shadow-plan/v1",
        "provenance": "local_advisory", "suite": policy["suite"],
        "declaration_sha256": sha256(declaration).hexdigest(), "targets": [],
    }
    try:
        before, after = resolve(repo, authority)
    except SnapshotUncertain as error:
        return result | {"mode": "unavailable", "reasons": [str(error)]}
    result |= {
        "snapshot": {
            "before": before.digest, "after": after.digest,
            "base": asdict(before.endpoint_identity), "tested": asdict(after.endpoint_identity),
            "head": asdict(after.provenance.head), "git": asdict(after.provenance.git),
        },
        "changes": [{"status": change.status, "old": _path(change.old), "new": _path(change.new)}
                    for change in after.changes],
    }
    if len(after.changes) == 1:
        change = after.changes[0]
        target = policy["target"]
        path = target.encode()
        if (
            change.status == "M"
            and change.old and change.new
            and change.old.path == change.new.path == path
            and change.old.mode == change.new.mode == "100644"
        ):
            try:
                old = _outside_test_body(before.read_content(path), policy["bounded_test_body"])
                new = _outside_test_body(after.read_content(path), policy["bounded_test_body"])
            except (ValueError, SyntaxError, SnapshotUncertain):
                pass
            else:
                if old == new:
                    return result | {
                        "mode": "selected", "targets": [target],
                        "reasons": ["change confined to a declared test body"],
                        "witness": {"path": target, "test_body": policy["bounded_test_body"],
                                    "unchanged_outside_sha256": sha256(old).hexdigest()},
                    }
    paths = sorted({path for change in result["changes"] for path in (change["old"], change["new"]) if path})
    reasons = []
    for path in paths:
        if path in policy["shared_paths"]:
            reasons.append(f"{path}: {policy['shared_paths'][path]}")
        elif any(path.startswith(prefix) for prefix in policy["shared_prefixes"]):
            reasons.append(f"{path}: shared CI or workflow input")
        else:
            reasons.append(f"{path}: change outside the bounded test-body rule")
    return result | {"mode": "full", "reasons": reasons or ["empty or unknown change set"]}
