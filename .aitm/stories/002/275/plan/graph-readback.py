"""Read the current #133 leaf graph and the existing Rank 50/60 holds."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

REPO = "kburson/aitm"
HERE = Path(__file__).resolve().parent


def read(endpoint):
    return json.loads(subprocess.check_output(["gh", "api", f"repos/{REPO}/{endpoint}"]))


def main():
    leaves = read("issues/133/sub_issues?per_page=100")

    def row(leaf):
        number = leaf["number"]
        dependencies = read(f"issues/{number}/dependencies/blocked_by?per_page=100")
        return number, {"title": leaf["title"], "state": leaf["state"], "state_reason": leaf["state_reason"],
                        "blocked_by": sorted(item["number"] for item in dependencies)}

    with ThreadPoolExecutor(max_workers=6) as pool:
        graph = dict(pool.map(row, leaves))
    assert graph[146]["blocked_by"] == [144, 145]
    assert graph[148]["blocked_by"] == [139]
    assert graph[267]["blocked_by"] == [143]
    assert graph[149]["blocked_by"] == [146, 147, 148]
    assert graph[168]["blocked_by"] == [146, 163, 165]
    assert graph[172]["blocked_by"] == [143, 171, 267]
    payload = {"source": "authenticated GitHub issue dependency readback", "epic": 133, "leaves": graph}
    (HERE / "graph-readback.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Read {len(graph)} live leaves and {sum(len(row['blocked_by']) for row in graph.values())} prerequisite edges.")


if __name__ == "__main__":
    main()
