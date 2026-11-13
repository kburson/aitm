# #146 selected product observation and live negative controls

The selected trial runs the exact product commit `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`, tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`. The full product baseline independently established the exact 1,216-ID source inventory and complete outcomes. The selected trial uses the same APFS boundary and instrumented CPython/pytest observation route. [Full baseline](2026-11-12-146-full-suite-observation-findings.md) · [Readback](selected-observation-readback.json)

The controller observed full discovery and final inventory before authorizing selection, then repeated full discovery and final inventory in the selected execution process. The traced dispatch contained exactly four IDs. It included the two native-child tests and both parameter rows of the quota-authority test. All four emitted complete passing sequences. The receipt explicitly records all 1,212 remaining IDs as unobserved. Both required pytest-launched direct children were created inside their assigned test bodies and exited normally with status 0. External DTrace recorded 4,327 product file/line pairs for CLI help and 6,493 for one-shot collection.

| Control | Observed result |
| --- | --- |
| Worker-origin green report | The unprivileged worker produced a positive pytest-shaped report. Controller intake rejected that input as untrusted. |
| Missing collection | A genuine run omitting the accounting test file collected 1,181 IDs. The exact regular selected dispatch refused with `inventory-mismatch`, exit 4 and no started tests. |
| Observed failure and missing sibling | The observer saw a real assertion failure. Pytest stopped at one failure while the second assigned test remained unobserved. The controller preserved both outcomes and refused the aggregate. Both obligations belonged to one invocation. |
| Wrong invocation | A completed selected trace could not satisfy a different controller invocation. |

The hosted controller keeps raw process and DTrace diagnostics outside the worker's write authority and publishes digests for each stream. The trial also checks archive and receipt identity through authenticated provider reads. The native trace depends on reviewed interpreter instrumentation and a reviewed executable suite. It cannot establish the behavior of arbitrary code sharing that interpreter.

| Hosted run | Result |
| --- | --- |
| [43368532756, attempt 1](https://github.com/kburson/aitm/actions/runs/43368532756/attempts/1) | Selected pass and initial live controls. The omission run used collection-only mode. |
| [43368915281, attempt 1](https://github.com/kburson/aitm/actions/runs/43368915281/attempts/1) | Selected pass and explicit regular-dispatch refusal for the omitted file. |
| [43368915281, attempt 2](https://github.com/kburson/aitm/actions/runs/43368915281/attempts/2) | Selected checks and the live controls repeated. The hosted replay refused when the provider no longer exposed attempt 1's artifact. |

Before rerun, the controller verified and retained the actual attempt-1 archive. The independent reviewer replayed the exact authenticated attempt-1 trace against the live attempt-2 identity. It passed under its own assignment and was rejected under attempt 2. That stale-byte decision ran in a local controller. The hosted attempt confirms fail-closed handling when the original artifact is unavailable. The attempt-1 receipt hash and original diagnostic stream hashes remain in the readback, with the retained selected trace and a sanitized assignment binding in this publication. [Signed independent review](reviews/2026-11-12-146-selected-observation-review.md)
