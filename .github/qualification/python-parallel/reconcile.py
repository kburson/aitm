"""Compare worker receipts and controller phases before using the #103 verifier."""
import json
import sys
from collections import Counter
from pathlib import Path

from python_gate import _outcomes, collect_child_coverage

directory = Path(sys.argv[1])
workers = int(sys.argv[2])
policy = json.loads(Path(sys.argv[3]).read_text())


def load(name):
    return json.loads((directory / name).read_text())


def write(name, data):
    (directory / name).write_text(json.dumps(data, indent=2) + "\n")


controller = load("controller.json")
receipts = [load(f"gw{number}.json") for number in range(workers)]
assert controller["exit_code"] == 0
assert controller["deselected"] == controller["children"] == controller["collected"] == []
inventory = receipts[0]["collected"]
worker_reports = []
children = []
for receipt in receipts:
    assert receipt["schema"] == controller["schema"] == "aitm.pytest-evidence/v1"
    assert receipt["exit_code"] == 0 and receipt["deselected"] == []
    assert receipt["collected"] == inventory
    worker_reports.extend(receipt["reports"])
    children.extend(receipt["children"])


def report_counter(reports):
    return Counter(json.dumps(report, sort_keys=True) for report in reports)


assert report_counter(worker_reports) == report_counter(controller["reports"])
complete = dict(controller, collected=inventory, children=children)
outcomes, failures = _outcomes(complete, policy["optional_skips"])
assert not failures, failures
assert len(outcomes) == len(inventory)
assert {child["label"] for child in children} == set(policy["required_children"])
assert len(children) == len(policy["required_children"])
assert len({child["pid"] for child in children}) == len(children)
child_proof = collect_child_coverage(complete, directory / ".product")
assert all(item["covered_lines"] and item["returncode"] == 0 for item in child_proof["children"])
write("reconciled.json", complete)
write("children.json", child_proof)
print(f"{len(outcomes)} unique test outcomes, {len(worker_reports)} phase reports")
print(json.dumps(child_proof, sort_keys=True))
