# #276 Controller-owned product catalog

**Disposition: pass for a two-behavior local shadow catalog.** The exact reviewed product source passed all 20 repetitions, totaling 40 direct behavior assertions and 80 child processes. The prototype refused all six benign negative inputs. It leaves #103 authoritative and establishes no general candidate-independent pytest or production merge authority. [Spike #276](https://github.com/kburson/aitm/issues/276) · [#103](https://github.com/kburson/aitm/issues/103)

## Tested inputs and results

The controller archived product commit `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`, tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`, and installed it using its lock, CPython 3.13.9 and uv 0.10.6. The local host was macOS 26.6.2 arm64 and the fixture volume was APFS. Each repetition created a distinct private project, registration, source fixture directory and account writer guard. The bootstrap changes the guard path only inside the child fixture process. It runs the pinned CLI implementation and avoids writing to the actual account control root.

| Catalog case | External behavior and mapping | Result |
| --- | --- | --- |
| CLI help | Launch the installed console directly. Require exit 0 and output markers `usage: aitm-usage`, `--help` and `collect-once`. Map to `test_usage_console_help` and required child label `cli-help`. | 20/20 |
| One-shot collection | Launch registration, collection and status as distinct direct children. Require exit 0, a positive collection sequence, producer mode `one-shot` and a status PID equal to the collection child PID observed by the controller. Map to literal required ID `test_one_shot_status_uses_collecting_subprocess_pid` and child label `service-one-shot`. | 20/20 |

The controller checked OS parent PID, exit status and output from its own subprocess pipes. It retained 40 sanitized behavior rows containing the 80 process receipts. The four-command case set had zero observed failures. The single-user local setup tests the semantics of the external checks. It does not demonstrate hostile process isolation or protected receipt storage for arbitrary product code. [Diagnostics](diagnostics.jsonl)

The exact live #103 push attempt 43257314192, attempt 1, bound the canonical workflow, required job identities and artifact 13962226641 to the same product SHA. The downloaded ZIP hash matched GitHub's `9a88fe3914b7df0765b5f7368c4eed118e5725041db5dd1f79363045d16bce02`. Replaying the pinned #103 gate and policy passed 1,216 tests and both native coverage obligations. The workflow's existing evidence covers six literal required test IDs. CLI help is an explicit required child label. The service one-shot test is both an explicit required test ID and a required child label. The other five required tests remain covered by the existing full #103 result. The local catalog supplies no independent line coverage. [Canonical attempt](https://github.com/kburson/aitm/actions/runs/43257314192/attempts/1) · [Artifact](https://github.com/kburson/aitm/actions/runs/43257314192/artifacts/13962226641) · [Readback](readback.json)

## Negative controls

| Control | Evidence path and result |
| --- | --- |
| Required test ID omitted | Remove the exact service ID and its phases from an in-memory copy of the real #103 evidence. The unmodified pinned gate refused the required ID. |
| Required test ID renamed | Change the service ID and corresponding phase IDs in a copy. The pinned gate refused the original required ID. |
| Required test skipped | Replace the recorded service call outcome with a synthetic skip. The pinned gate refused the outcome and required ID. |
| Required test xfailed | Mark the synthetic skip as xfail. The pinned gate reported unexpected xfail and refused the required ID. |
| Required process absent | Withhold the controller's collection-process record from the positive case. The external evaluator refused missing process evidence. |
| Expected output changed | Give the external evaluator a copy of the positive help record with harmless alternate stdout. It refused the marker mismatch. |

The first four controls are copied-artifact admission checks and the last two are external evaluator checks on controller records. The experiment does not modify pytest tests, alter the product or run an adversarial worker. A first APFS preflight passed a directory directly to `diskutil`, which accepts the volume or device here. The corrected preflight resolves the device with `df` before checking the filesystem. The 20 repetitions started after that setup correction.

## Recommended #146 disposition

Keep #103 as the mandatory gate. Treat this catalog and exact-tree receipt intake as optional, independently reviewed evidence. In a production shadow follow-up, store the catalog and assertions in controller-owned, reviewed source. Verify actual hosted account separation and protected receipt custody before consuming shadow evidence. Preserve the exact #103 result, its six required tests, both child obligations and coverage policy. A catalog failure can inform review and the #275 advisory warning and manual repair workflow. The general hosted selected gate remains unqualified because this experiment does not independently establish arbitrary candidate pytest collection or in-process outcomes. Replan #133 explicitly around those narrower guarantees if retaining the broader scope no longer has a justified implementation path. #148 and #267 retain their current holds.

## Reproduction

Run from the evidence directory with authenticated read-only GitHub CLI access, exact repository objects, CPython 3.13.9 and uv 0.10.6 on macOS/APFS.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
PYTHONDONTWRITEBYTECODE=1 python3 rehearse.py --repo "$AITM_REPO" --python "$PINNED_PYTHON" \
  --uv "$PINNED_UV" --repetitions 20 --diagnostics reproduced-diagnostics.jsonl \
  > reproduced-readback.json
```
