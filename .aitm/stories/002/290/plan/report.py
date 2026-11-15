"""Render the #290 benchmark report from the verified readout."""
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys


def elapsed(seconds):
    minutes, rem = divmod(round(seconds), 60)
    return f"{minutes}:{rem:02d}"


def main(path, archived):
    data = json.loads(path.read_bytes())
    cells = data["measurements"]
    hosted = data["observed_hosted_1817"]
    created = datetime.fromisoformat(hosted["run"]["created_at"])
    started = datetime.fromisoformat(hosted["job"]["started_at"])
    finished = datetime.fromisoformat(hosted["run"]["updated_at"])
    queue = (started - created).total_seconds()
    hosted_elapsed = (finished - created).total_seconds()
    changes = data["coverage_differences_against_serial_cold"]
    counts = {cohort: {mode: len(delta) for mode, delta in modes.items()} for cohort, modes in changes.items()}
    assert all(not difference for modes in changes.values() for difference in modes.values()), counts
    print("""# #290 Full-suite scale benchmark results

The pinned private macOS/APFS model ran 3,020 assignments in each cell. The complete current suite supplied 1,817 actual pytest IDs. A deterministic projected cohort supplied 1,203 repeat assignments across all 45 existing test families, preserving required native cases, file mix and fixture behavior. The two cohorts ran as separate pytest sessions with private test state. This measures how the existing workload scales. Future Core behaviors and hosted PR timing are outside the evidence.

| Layout | Dependency setup | Full cohort | Projected cohort | Evidence and setup included |
| --- | ---: | ---: | ---: | ---: |""")
    for width in (1, 3):
        for cache in ("cold", "warm"):
            row = cells[f"workers-{width}-{cache}"]
            full = row["cohorts"]["full"]["test_seconds"]
            projected = row["cohorts"]["projected"]["test_seconds"]
            layout = "1 worker" if width == 1 else "3 workers"
            print(f"| {layout}, {cache} | {row['setup_seconds']:.3f} s | {elapsed(full)} | {elapsed(projected)} | {elapsed(row['elapsed_seconds'])} |")
    print(f"""
Each cell passed the exact ordered assignment inventory and all three test phases. Coverage denominators and exact per-file executed line and branch sets agreed across all four layouts within each cohort. The required `cli-help` and `service-one-shot` children exited zero with distinct PIDs and matching covered product line counts. Measured elapsed over the two samples gave three workers a **{data['local_three_worker_speedup']:.2f}× speedup**. The matrix has one sample per cell. Cold and warm refer to uv's cache and virtual environment. Source export precedes the timer, and system file caches and transient resource load were not controlled.

Local queue is zero by construction. The separate GitHub-hosted scheduled run executed 1,817 actual tests in {elapsed(hosted_elapsed)} from registration through result, including {queue:.0f} seconds between registration and job start. GitHub also registered that run 7 hours 43 minutes late. [Hosted attempt](https://github.com/kburson/aitm/actions/runs/43709222718/attempts/1)

The local result supports using three private workers as the initial full-reference layout for #293. Evaluate duration-balanced hosted shards only if candidate-bound hosted measurements show tail or resource pressure. Hosted 3,000+ trigger-to-verdict and story-validation p95 remain to be measured. [Exact readout](benchmark-readout.json) · [Workload](workload.json) · [Retained evidence](benchmark-evidence.zip)

The retained evidence archive SHA-256 is `{sha256(archived.read_bytes()).hexdigest()}`. It carries controller and worker receipts, timed per-PID child coverage attestations, test logs, per-file coverage and the sampled APFS ancestry log. Coverage.py's JSON command removed the timed per-PID files after their verification. Two separate exact-source child controls reproduced the same counts with the files retained using `--keep-combined`. The control runs are excluded from the timing table.
""")


if __name__ == "__main__":
    main(*map(Path, sys.argv[1:3]))
