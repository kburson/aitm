# PR #197 Python runtime and fixture isolation

The frozen comparison uses trunk `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`,
PR head `dbbc729574c9b078658af310b2efa2945020224f`, and approved tree
`7d93353e06c8177c19bc1f918217e2f8ccf75da7`. The PR was held during this work.

## Hosted runtime

[Attempt 2](https://github.com/kburson/aitm/actions/runs/43062845686/job/130725314269)
passed all 1,071 product and CLI cases in 454.86 seconds. Product coverage
was combined and written. The CI-helper tests reached 79 percent before
the eight-minute job limit cancelled the lane. The wheel check and
artifact publication had yet to run.

The [earlier signed attempt](https://github.com/kburson/aitm/actions/runs/43058239273/attempts/3)
completed the candidate job in 7m26s. Its retained product JUnit reports
390.55 seconds across test phases. The largest contributions were native
monitor scope (128.35s), install (72.41s), monitor journal (51.95s),
activation receipt (32.95s), and rollup (31.36s). On the timed-out attempt,
two install/upgrade cases alone took 52.64 seconds. The suite includes
real filesystem custody, SQLite, process start and restart, and installed
wheel behavior. Serial execution was the starting baseline specified by
[the #103 design](../../103/design/github-ci-quality-gates-design.md).
That design calls for xdist once isolation is proven and retains the full
test inventory, coverage and required child-process checks.

## Fixture failure

Both reported errors were reproduced against the exact #197 source with
the real `NativeScopeFixture`. A scratch probe created a sibling directory
during the snapshot read or between the frontier's two path checks. The
transcript bytes, inode, and mtime were identical. The unrelated directory
change moved an ancestor ctime and the capture check rejected the read.
The same two probes passed when the fixture was moved outside that
directory's ancestry. This demonstrates a cause for both signatures.
The process responsible for the original hosted change remains unconfirmed.

The existing [fixture isolation commit](https://github.com/kburson/aitm/commit/d1916b81fc05417c6ff709beb59890d22369243b)
in [PR #231](https://github.com/kburson/aitm/pull/231) creates a fresh
`--basetemp` for each Python lane, separate from evidence output. All
seven executed base jobs in the retained isolated and fresh #209 run
receipts passed. An additional base job never acquired a runner. This
change addresses the shared-directory exposure while retaining the
capture checks. Its delivery is tracked in [#209](../../209/plan/delivery-checklist.md).

## Local worker trial

The experiment used Python 3.13.9, pytest 9.2.0, coverage 7.17.2 and
pytest-xdist 3.8.0 on an arm64 macOS 26.6.2 host. It used the exact approved
tree and the same product and CLI collection in every run.

| Configuration | Wall time | Outcomes |
| --- | ---: | --- |
| Serial, coverage enabled | 285.65s | 1,071 passed |
| Three workers, coverage output under a fixture ancestor | 108.24s | 1,066 passed, two failed, three setup errors |
| Three workers, separate fixture and coverage roots | 108.08s | 1,071 passed |

The successful serial and parallel runs had identical test IDs and
outcomes, identical coverage files, and identical executed lines and
branch arcs per file. Both covered 10,655 of 11,604 executable lines and
3,079 of 3,816 branches. The three-worker run used `--dist worksteal`.
The successful parallel run demonstrates that this collection can run
out of serial order with private fixtures. Host-specific performance and
isolation still need qualification on the GitHub runner.

Adding `-n` to the current evidence command is insufficient. The
two-case control passed both required subprocess tests and produced six
phase reports. Its controller receipt had an empty inventory and no
child-process records. A local adapter gave each worker its own observer
file, checked matching collections and phase reports, then reconciled the
workers' child PIDs against raw coverage. Both required child labels were
recovered with positive coverage.

The full three-worker run with the receipt adapter passed in 110.47s.
The adapter reconciled 1,071 unique outcomes and 3,213 phase reports. Both
required subprocess labels had positive PID-linked coverage. The combined
line and branch sets still matched the serial run exactly. The unmodified
#103 Python policy evaluator accepted those local product receipts with
the retained 1,070-case exact-base and helper evidence. This replay
exercises policy evaluation. Hosted runner timing and GitHub signing
remain outside this trial.

## Before rerunning #197

Deliver the private `--basetemp` change already reviewed in #231. Qualify
the worker change separately under #103 with a pinned xdist dependency,
private fixture roots, and a reconciled receipt from every worker. Trial
two and three workers on the hosted macOS runner against the same tree.
Measure the whole job through wheel smoke and artifact publication under
the existing eight-minute limit, with the complete test inventory,
coverage, required child evidence and signing. The base lane can use its
isolated serial command during candidate-worker qualification. The
[accepted #133 plan](../../133/plan/test-impact-analysis-implementation-plan.md#t11-assign-isolated-test-shards--3h-p2-t02t08)
tracks sharding across separate CI jobs.

No workflow change was delivered during the investigation. PR #197
remained on attempt 2, #139 stayed in Test, and #159 remained blocked by
#157 and #158.
