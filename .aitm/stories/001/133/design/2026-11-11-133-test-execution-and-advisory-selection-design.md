# #133 Test execution and advisory selection design amendment

This amendment records the owner's execution and selection direction for
future work. Read it with the [accepted design](test-impact-analysis-design.md),
the [implementation amendment](../plan/2026-11-11-133-test-execution-and-advisory-selection.md),
and the [merge-only Stop the Line amendment](2026-11-11-133-merge-only-stop-the-line-design.md).
The accepted revision and review records remain available as exact evidence.

## Local workers and hosted shards

Run parallel-safe local Python TIA selections with `pytest-xdist`.
Default to `max(1, floor(0.8 × available_cores))` worker processes,
where available cores are the logical CPUs available to the invoking
process. Keep private fixture roots and the reviewed isolation rules for
tests that share host resources, leases, or process lifecycle. Record the
resolved worker count alongside the test results.

On hosted CI, use a separate ephemeral instance for every shard. Assign
tests by package, test type, runner capability, and isolation group.
Name each job for its package or group, lane, and shard. Balance compatible
groups from recorded test durations and runner setup costs. Apply the
existing inventory, coverage, subprocess evidence, and same-attempt
receipt reconciliation to the complete shard set. Hosted shard counts
and per-runner worker counts come from hosted qualification.

## Advisory Python dependency observations

Evaluate `pytest-testmon` as an advisory source of Python dependencies
and test ordering hints. Report its suggestions separately from the
trusted selection and compare them with full-run outcomes. A missing,
stale, or incompatible testmon history supplies no advisory evidence.
Use observed dependencies to propose additions to the reviewed graph.
Testmon results carry no authority to omit tests or pass validation.

The trusted selector still reports the selected test IDs and an evidenced
dependency path from each changed file to its affected tests. Uncertain
impact selects the full applicable suite, even if testmon suggests zero
tests. The scheduled full trunk suite and merge-only incident policy
continue under their existing qualification and cutover requirements.
