"""Verify the production gate bytes and trunk rules against the preflight snapshot."""

import json
import subprocess
from hashlib import sha256
from pathlib import Path

CURRENT = Path(__file__).resolve().parent
ORIGINAL = CURRENT.parent / "delivery-293"
PLANNING = CURRENT.parent / "planning"
FILES = (
    ".github/workflows/ci.yml",
    "tools/ci/policy.json",
    "tools/ci/pytest_evidence.py",
    "tools/ci/python_gate.py",
    "tools/ci/verify_pr.py",
)


def git(*args):
    return subprocess.check_output(["git", "-C", str(PLANNING), *args])


def api(path):
    return json.loads(
        subprocess.check_output(["gh", "api", f"repos/kburson/aitm/{path}"])
    )


before = (ORIGINAL / "source-base").read_text().strip()
readback = api("branches/trunk")["commit"]["sha"]
git("fetch", "--quiet", "origin", "refs/heads/trunk:refs/remotes/origin/trunk")
after = git("rev-parse", "origin/trunk").decode().strip()
assert after == readback
before_rules = json.loads((ORIGINAL / "trunk-rules-before.json").read_bytes())
after_rules = api("rules/branches/trunk")
assert before_rules == after_rules
gate = {}
for path in FILES:
    old = git("show", f"{before}:{path}")
    new = git("show", f"{after}:{path}")
    assert old == new, path
    gate[path] = sha256(new).hexdigest()
print(
    json.dumps(
        {
            "issue": 103,
            "trunk_baseline": before,
            "trunk_readback": after,
            "same_trunk_head": before == after,
            "verified_gate_sha256": gate,
            "effective_rules_before": before_rules,
            "effective_rules_after": after_rules,
        },
        indent=2,
        sort_keys=True,
    )
)
