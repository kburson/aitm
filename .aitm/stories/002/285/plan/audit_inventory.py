"""Join pinned collected test IDs with retained CI timing samples."""
from collections import Counter
import json
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
pinned = "a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2"


def nodes(name, expect):
    raw = (root / name).read_text()
    ids = [line for line in raw.splitlines() if re.match(r"^(packages|tools)/.*\.py::", line)]
    assert len(ids) == len(set(ids)) == expect, (name, len(ids))
    return ids


product = nodes("product-collection.log", 1216)
required_helpers = nodes("helper-collection.log", 196)
all_helpers = nodes("all-helper-collection.log", 525)
assert set(required_helpers) <= set(all_helpers)
assert set(product) & set(all_helpers) == {"tools/ci/tests/test_cli_evidence.py::test_usage_console_help"}
required = set(product) | set(required_helpers)
available = set(product) | set(all_helpers)
timings = {}
raw = (root / "hosted-python.log").read_text()
for line in raw.splitlines():
    match = re.search(r" (\d+\.\d+)s (setup|call|teardown)\s+(\S.*\.py::.*)$", line)
    if match:
        seconds, phase, node = match.groups()
        assert node in required
        timings.setdefault(node, {})[phase] = float(seconds)
assert sum(len(phases) for phases in timings.values()) == 15

print(json.dumps({
    "scope": "collection-only",
    "source_revision": pinned,
    "timing_scope": "slowest 15 reported phases, shared runner, no time imputed for unreported IDs",
    "timing_source": {"run": 43418827344, "attempt": 1, "job": 131863407499},
    "profiles": {"product_cli": len(product), "required_ci_helpers": len(required_helpers)},
    "required_union": len(required),
    "collected_union": len(available),
    "module_counts": dict(sorted(Counter(node.split("::")[0] for node in available).items())),
    "tests": [{"id": node, "in_current_gate": node in required, "seconds_by_phase": timings.get(node)}
              for node in sorted(available)],
}, sort_keys=True, indent=2))
