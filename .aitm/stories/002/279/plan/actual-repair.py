"""Read actual #278 delivery and use it in a separate #279 shadow recovery."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import ci_advisory
import ci_incident
import ci_recovery
from verify_pr import GitHub

PLAN = "42ae4ea8215432618da5cc610256d345db5f2034"
RECEIPT = Path(".aitm/stories/002/278/plan/delivery.json")
REVIEW = "3c8f91d6155e81aaebae7177ca2424c101c3564838ed30f7b07b30770fca5379"


def main():
    planning = Path(sys.argv[1])
    github = GitHub(ci_advisory.REPO)
    repair = ci_recovery.verify_repair(
        github, PLAN, str(RECEIPT), sha256((planning / RECEIPT).read_bytes()).hexdigest(), REVIEW,
    )
    green = ci_advisory.observe(github)
    assert green["status"] == "green" and green["sha"] == repair["sha"]
    # The incident is synthetic. The canonical green and reviewed repair are real.
    initial = {
        **green,
        "provenance": "shadow",
        "status": "red",
        "sha": "1" * 40,
        "run_number": green["run_number"] - 1,
        "run_id": green["run_id"] - 1,
        "attempt": 1,
        "started_at": "2026-11-13T09:00:00Z",
        "failures": ["quality:failure"],
        "artifact": None,
    }
    with TemporaryDirectory() as directory:
        store = ci_incident.Store(Path(directory) / "shadow.db", "shadow")
        assert store.observe(initial) == "warning"
        store.nominate(1, "shadow-repairer", repair["pr"])
        observed = {**green, "provenance": "shadow"}
        token = ci_recovery.reconcile(store, 1, observed, repair=repair)
        assert token and store.status()["incident"]["active"]
        assert ci_recovery.acknowledge(store, 1, "shadow-operator", token, observed, repair=repair)
        result = store.status()
        assert not result["incident"]["active"]
    print(json.dumps({"provenance": "shadow", "actual_repair": repair, "actual_green": green,
                      "synthetic_incident": initial, "acknowledged": result}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
