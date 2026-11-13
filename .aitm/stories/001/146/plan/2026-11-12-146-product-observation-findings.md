# #146 product observation after #268

**Disposition — Product qualification remains blocked at Rank 50.** The independent review accepts the retained receipts as diagnostics for the named macOS/APFS jobs. The production criteria for complete collection, per-test execution and native child coverage remain open. #149 and #168 retain their dependency on #146. #148 and #267 retain their Rank 60 pickup holds. [Independent review](reviews/2026-11-12-146-product-observation-review.md) · [Exact run and artifact readback](product-observation-readback.json)

## Scope and reference

The disposable GitHub Actions workflow ran the same locked product tree as protected trunk commit `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`, tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`. It extended #268’s separate macOS/APFS worker and controller to the normal product pytest commands. The controller owned its receipt and checked access for the worker principal against the named inputs and receipt paths. The trial workflow ran from a dedicated branch. The existing #103 workflow and protection rules continued to govern PR validation. [#268 reviewed pilot](https://github.com/kburson/aitm/blob/822fc938720a5dd9f63828aeb369bdaec85fce82/.aitm/stories/002/268/plan/2026-11-12-268-pilot-findings.md) · [#103](https://github.com/kburson/aitm/issues/103)

The passing reference CI run recorded 1,216 unique pytest IDs, 3,648 passing phases and two native child coverage rows (`service-one-shot`, 6,501 product lines, and `cli-help`, 4,327 product lines). The authenticated artifact establishes which bytes CI retained. The pytest inventory and execution reports came from inside the worker. The coverage reader joined worker coverage shards to worker-reported child PIDs and statuses. [Passing reference CI](https://github.com/kburson/aitm/actions/runs/43257314192/attempts/1) · [Reference artifact](https://github.com/kburson/aitm/actions/runs/43257314192/artifacts/13962226641) · [Child coverage reader](https://github.com/kburson/aitm/blob/766504a02aaeb9dda339d588172dd7d5bdbd2b3f/tools/ci/python_gate.py#L233-L252)

## Hosted results

| Trial | Recorded result |
| --- | --- |
| [1](https://github.com/kburson/aitm/actions/runs/43354052011/attempts/1) | Stopped before worker launch after the controller transferred ownership of scratch and lost the ability to change its mode. |
| [2](https://github.com/kburson/aitm/actions/runs/43354143225/attempts/1) | Verified scoped principal and receipt access controls, directly observed the CLI probe pass and collected a driver exit of 0. The controller could not read the private worker report. |
| [3](https://github.com/kburson/aitm/actions/runs/43354251426/attempts/1) | Verified scoped access controls and directly observed the CLI probe pass. The collect-only driver exited 0 and the worker report matched all 1,216 reference IDs. Full pytest exited 1. Reconciliation stopped the trial before selected execution. |
| [4](https://github.com/kburson/aitm/actions/runs/43354487946/attempts/1) | Repeated the access, direct CLI and exact reference comparison. Full pytest exited 1 with pytest error summaries. Selected pytest exited 4 with zero collected IDs, phases or child records. |

The diagnostic invocation supplied repository-relative paths while running from the package directory. That mismatch accounts for the selected command failing to reach its two assigned tests. The selected receipt has no underlying stderr. The full-run evidence retains summaries and a reconciliation error. It lacks the setup tracebacks needed to diagnose the underlying full-run failure.

| Required evidence | Qualification result |
| --- | --- |
| Complete collection, including dynamically discovered cases | Two same-tree reports agree on all 1,216 reference IDs. An independent inventory source is still required to identify omissions common to both. |
| Assigned per-test execution and outcome | The controller observed driver exits. The worker supplied any per-test phase and outcome claims. Both full product runs failed and the selected product run reached zero tests. |
| Native child lineage and coverage | The controller directly ran `aitm-usage --help`, observed exit 0 and checked two output markers. That probe establishes a direct CLI result. The trial produced no independently observed pytest child lineage or product line coverage. |

## Rank 50 continuation

The next qualification design needs a reviewed inventory outside the worker, with an explicit mapping to the current product obligations and its dynamically collected cases. It needs assignment-bound outcomes observed by the controller and native child lineage and line coverage captured outside worker write authority. Before another full-suite run, demonstrate those properties on a bounded product slice and retain the evidence for missing assignments and stale attempts. A candidate design that can establish only a fixed external catalog must identify the current product obligations it leaves unqualified before any scope decision.

For a future operational rerun, resolve selected node paths against the archived source, retain bounded setup tracebacks before reconciliation and rerun on the same locked toolchain. A passing rerun through the current pytest observer would establish ordinary product execution under the separate worker. Qualification also requires the independent evidence above. The current workflow, rank order and dependency holds continue to apply.
