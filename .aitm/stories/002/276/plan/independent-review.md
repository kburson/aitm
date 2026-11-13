# #276 independent review of the controller-owned catalog

I independently queried the canonical CI workflow, trunk and exact attempt, checked the required job outcomes, downloaded the evidence archive, and replayed the pinned full push gate. I checked every candidate diagnostic row and stream digest against its readback. I also ran the three unit tests and a fresh 20-repetition rehearsal with an independent scratch directory. [Issue #276](https://github.com/kburson/aitm/issues/276)

## Exact evidence

| Evidence | Verified identity |
| --- | --- |
| Product commit | `766504a02aaeb9dda339d588172dd7d5bdbd2b3f` |
| Product tree | `6f1ae4a5707f2344bbeb4c15efdb823480866feb` |
| Canonical trunk push | [43257314192 attempt 1](https://github.com/kburson/aitm/actions/runs/43257314192/attempts/1), workflow 412848571 |
| Canonical evidence archive | Artifact 13962226641, SHA-256 `9a88fe3914b7df0765b5f7368c4eed118e5725041db5dd1f79363045d16bce02` |
| Candidate diagnostics SHA-256 | `c9fcc89a5b81a95b6fb9550c84f04a10f843d08eb52e04b8b5f5ddec57895ca1` |
| Candidate readback SHA-256 | `0a90124ad4d722c86d3f1f718fbcaf6d33009d51352c53d7f0a958a1143a2a64` |
| Independent diagnostics SHA-256 | `1d6eada0526c6f1437396e449073f1add93b581e9d8cfdc166d0d5baad28109c` |
| Independent readback SHA-256 | `3e21b715ff6697af396d471405b2c969e2331be75e019377fedba2ace4783972` |

The successful push is the current exact trunk at readback. Its required python, quality and file-checks jobs and collect-evidence job succeeded. Its PR-specific lanes were skipped as expected. I recomputed the hashes for the canonical workflow, Python gate and policy from the pinned Git commit. Applying the exact push-mode gate to the original artifact passed with 1,216 outcomes, 11,272 of 12,276 product lines and 806 of 849 helper lines covered. Each of the six literal required pytest IDs had passing setup, call and teardown with no xfail. Both canonical child records were present, with successful exit and positive coverage. The full gate and its child coverage remain #103 evidence. [Canonical artifact](https://github.com/kburson/aitm/actions/runs/43257314192/artifacts/13962226641)

## Bounded behavior and refusal checks

Each of the candidate and independent rehearsals ran 20 fresh cases, with two behavior observations and four process launches per case. Each run contained 40 passing behavior rows and 80 distinct child PIDs whose observed parent was the same controller for that run. In every CLI launch the console exited 0 and printed the three required help markers. In every one-shot case, register, collect and status exited 0, collection returned a positive sequence, and status reported one-shot with the exact collect process PID. The fixture guard stayed in the case directory. These observations were local Darwin/APFS with Python 3.13.9 and uv 0.10.6.

The direct CLI behavior maps to the mandatory `cli-help` child label and its existing pytest node. That node is outside the policy's six literal `required_tests` IDs. Direct one-shot behavior maps to the `service-one-shot` label and one of those six IDs. The other five required tests, full inventory, line floors and pytest-launched child coverage remain in the existing gate. The local runs exercise equivalent output and producer behavior with an isolated fixture bootstrap. They add no line coverage evidence.

Four negative inputs derived from the canonical outcomes exercised the exact full gate's refusal of a removed required ID, renamed required ID, required skip and required xfail. Two inputs derived from observed local processes exercised the catalog's refusal of a missing collection process and wrong help output. I observed all six refusals in the independent rerun. These are controlled changes to evaluator inputs. The underlying positive process observations were real, and none of the six controls modifies the canonical artifact or the tested product.

The catalog evaluator accepts controller-created typed outcomes within the same local process. Its tested dictionary rejection is a narrow intake check. The rehearsal does not supply independent hostile-worker containment, a production credential boundary, or authenticated report transport. A PPID sampling failure would be refused as missing process evidence, even when the process exited 0.

**Independent disposition.** Accept #276 as a bounded local shadow result. Preserve #103 as the full gate. This catalog has no authority to substitute for the original required test inventory, fixture semantics or coverage, and supplies no production qualification for #146. Keep #148 and #267 on hold pending the reviewed #146/#133 disposition. [#103](https://github.com/kburson/aitm/issues/103) · [#146](https://github.com/kburson/aitm/issues/146)

Signed **Codex / review146_selected**, independent evidence reviewer.
