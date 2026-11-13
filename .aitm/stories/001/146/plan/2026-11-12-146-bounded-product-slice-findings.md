# #146 diagnostic recovery and bounded product slice

The product remained pinned to `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`, tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`. All changes are on the disposable trial branch. The #103 validation workflow continues to govern production. [Independent evidence review](reviews/2026-11-12-146-bounded-product-slice-review.md) · [Exact hosted artifacts and stream digests](bounded-product-slice-readback.json)

## Recover the failure data

The controller now retains full stdout and stderr for collection, the full and selected drivers, and each reconciliation process, even when the driver exits nonzero. Timeouts retain the partial streams, with byte counts and SHA-256 digests for the original and path-sanitized streams. The upload step runs after failures. The later pytest diagnostic hook emits each failed phase and its traceback as it reaches the controller, before pytest's summary, and enables a 90-second faulthandler traceback. A local xdist setup-failure check verified the hook independently of pytest's summary reporter.

| Hosted job | What the retained diagnostics established |
| --- | --- |
| [Capture only](https://github.com/kburson/aitm/actions/runs/43358167408/attempts/1) | Full stdout retained 5,830,619 bytes. Ledger setup rejected the controller-owned shared ancestor. The full run ended with 64 passed, 189 failed and 963 errors. Selected stderr named the missing repository-relative test file and the driver exited 4. |
| [Fixture ancestry and selected paths](https://github.com/kburson/aitm/actions/runs/43358380231/attempts/1) | The product accepted the root-owned fixture ancestor and both selected tests passed. The full result improved to 1,162 passed, 22 failed and 32 errors. Tracebacks exposed separate ancestry requirements for the account guard resolved from `nobody` and the locked interpreter used by installation tests. Other traces exposed native capture discontinuities that require their own diagnosis. |
| [Dedicated account and root-owned runtime](https://github.com/kburson/aitm/actions/runs/43359225097/attempts/1) | Product preflight passed all three checks for fixture ancestry, account guard ancestry and interpreter ownership. The full driver timed out at 430 seconds. Partial output showed an error by 47% and progress past 59%. This revision still depended on pytest's end-of-run traceback summary. |
| [Separated temp and report paths](https://github.com/kburson/aitm/actions/runs/43360021305/attempts/1) | Full pytest passed all 1,216 tests, with all 3,648 phases reconciled. Both selected tests passed. The separate trace interpreter failed to compile against the runner's OpenSSL 4 headers. |
| [Immediate phase tracebacks](https://github.com/kburson/aitm/actions/runs/43360265384/attempts/1) | Full pytest again passed all 1,216 tests, as did both selected tests. The trace build hit the same compiler error. The retained streams include the full pytest and compiler logs. |

Separating worker home, temp, fixtures and reports removed shared directory churn from the comparison. The independent reviewer separately reproduced the scanner's rejection after an unrelated sibling changed an ancestor's ctime. That control shows how a shared ancestor can create a false continuity failure. The original hosted logs cannot identify the changed ancestor for each failed case.

## Bounded controller observations

The controller read the pinned files, verified their digests, and used the two unparametrized test definitions to establish the bounded inventory. It dispatched an external equivalent for each case. The CLI check required the three help markers and exit 0. The service check required a successful collection with a positive sequence and a later status readback that reported the same producer PID observed by the controller through OS process lineage.

The [first executable slice](https://github.com/kburson/aitm/actions/runs/43361077255/attempts/1) built a disposable Python 3.13.9 with the unused OpenSSL extensions disabled. Both external predicates passed. DTrace rejected both line probes because the provider exposed no matching probe. The retained CPython 3.13.9 source declares the probe but the interpreter has no line-probe call site. The reviewer checked the probe table in an independently inspected unmodified binary. [Upstream CPython source](https://github.com/python/cpython/tree/v3.13.9/Python) · [Upstream tracing discussion](https://discuss.python.org/t/discussion-dtrace-support-in-python-should-we-remove-it-completely-or-restore-pre-3-12-functionality/103321)

The next build added a narrowly scoped call to the CPython line event hook, hashed the changed source and captured the Mach-O probe table. It ran the same two product assertions with the source and interpreter controlled outside the worker's write authority.

The [passing hosted run](https://github.com/kburson/aitm/actions/runs/43361629256/attempts/1) verified the two assignments below. The controller held each product process before importing the product, checked its UID and parent chain through the OS, and waited for DTrace readiness before releasing it. DTrace exited 0 with empty stderr in both cases. The controller retained the raw trace separately from the product stdout and never consumed a worker coverage file for this result. [Verified artifact](https://github.com/kburson/aitm/actions/runs/43361629256/artifacts/14007819897)

| Assignment | Controller outcome | Python line coverage in the native child |
| --- | --- | --- |
| CLI help | Exit 0 with all three help markers | 128 distinct lines in `cli.py`, including required line 417 |
| One-shot collection | Exit 0, positive sequence and a status PID that matched the OS-observed child | 454 distinct lines in `service.py`, including required line 1052 |

**Disposition.** The bounded run establishes independent inventory, assigned behavioral outcomes and Python source-line coverage for the two controller-launched native product children. The selected pytest run and the full 1,216-test comparison are separate worker observations. The bounded observer uses an instrumented CPython build, covers one designated source file per case, and runs external equivalents of two existing assertions. Broader qualification still requires independent dynamic pytest inventory, assignment and per-test evidence for the full suite, pytest-launched native child coverage and production acceptance checks. #146 stays blocked at Rank 50. #148 and #267 retain their Rank 60 holds.
