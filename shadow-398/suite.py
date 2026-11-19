"""Select one declared suite against the #383 exact snapshot pair."""
import ast
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from tools.ci.tia.snapshot import ProbeRequest, SnapshotUncertain, resolve


def _outside_body(source, name):
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
    if case["base"] == policy["reviewed_base"] and len(after.changes) == 1:
        change = after.changes[0]
        path = policy["bounded_source"].encode()
        if (
            change.status == "M"
            and change.old and change.new
            and change.old.path == change.new.path == path
            and change.old.mode == change.new.mode == "100644"
        ):
            try:
                old = before.read_content(path)
                new = after.read_content(path)
                old_outside = _outside_body(old, policy["bounded_function"])
                new_outside = _outside_body(new, policy["bounded_function"])
            except (ValueError, SyntaxError, SnapshotUncertain):
                pass
            else:
                digest = sha256(new).hexdigest()
                variant = policy["reviewed_candidate_source_sha256"].get(digest)
                if (
                    sha256(old).hexdigest() == policy["reviewed_previous_source_sha256"]
                    and old_outside == new_outside
                    and sha256(old_outside).hexdigest() == policy["reviewed_outside_sha256"]
                    and variant in {"bounded", "seeded"}
                ):
                    return result | {
                        "mode": "selected", "targets": [policy["target"]],
                        "reasons": ["exact reviewed source variant confined to the headless decoder body"],
                        "witness": {"path": policy["bounded_source"], "function": policy["bounded_function"],
                                    "variant": variant, "source_sha256": digest,
                                    "unchanged_outside_sha256": sha256(old_outside).hexdigest()},
                    }
    return result | {"mode": "full", "reasons": ["change is shared or outside the pinned decoder declaration"]}
