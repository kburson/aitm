# #290 Full-suite scale benchmark results

The pinned private macOS/APFS model ran 3,020 assignments in each cell. The complete current suite supplied 1,817 actual pytest IDs. A deterministic projected cohort supplied 1,203 repeat assignments across all 45 existing test families, preserving required native cases, file mix and fixture behavior. The two cohorts ran as separate pytest sessions with private test state. This measures how the existing workload scales. Future Core behaviors and hosted PR timing are outside the evidence.

| Layout | Dependency setup | Full cohort | Projected cohort | Evidence and setup included |
| --- | ---: | ---: | ---: | ---: |
| 1 worker, cold | 1.260 s | 14:04 | 9:59 | 24:11 |
| 1 worker, warm | 0.076 s | 12:51 | 9:45 | 22:43 |
| 3 workers, cold | 1.094 s | 5:03 | 3:30 | 8:41 |
| 3 workers, warm | 0.076 s | 5:21 | 3:36 | 9:05 |

Each cell passed the exact ordered assignment inventory and all three test phases. Coverage denominators and exact per-file executed line and branch sets agreed across all four layouts within each cohort. The required `cli-help` and `service-one-shot` children exited zero with distinct PIDs and matching covered product line counts. Measured elapsed over the two samples gave three workers a **2.64× speedup**. The matrix has one sample per cell. Cold and warm refer to uv's cache and virtual environment. Source export precedes the timer, and system file caches and transient resource load were not controlled.

Local queue is zero by construction. The separate GitHub-hosted scheduled run executed 1,817 actual tests in 11:08 from registration through result, including 3 seconds between registration and job start. GitHub also registered that run 7 hours 43 minutes late. [Hosted attempt](https://github.com/kburson/aitm/actions/runs/43709222718/attempts/1)

The local result supports using three private workers as the initial full-reference layout for #293. Evaluate duration-balanced hosted shards only if candidate-bound hosted measurements show tail or resource pressure. Hosted 3,000+ trigger-to-verdict and story-validation p95 remain to be measured. [Exact readout](benchmark-readout.json) · [Workload](workload.json) · [Retained evidence](benchmark-evidence.zip)

The retained evidence archive SHA-256 is `ade7d3e0ba0ea6a3f4695017824a0da82eda60702282dd9465e013178fd00d9c`. It carries controller and worker receipts, timed per-PID child coverage attestations, test logs, per-file coverage and the sampled APFS ancestry log. Coverage.py's JSON command removed the timed per-PID files after their verification. Two separate exact-source child controls reproduced the same counts with the files retained using `--keep-combined`. The control runs are excluded from the timing table.

