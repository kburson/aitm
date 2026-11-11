# #133 Test execution and advisory selection implementation plan amendment

**Goal** Shorten local Python feedback and hosted test execution while
preserving exact test evidence and full-suite fallback.

**Design** [Test execution and advisory selection amendment](../design/2026-11-11-133-test-execution-and-advisory-selection-design.md).
Apply this alongside the [accepted plan](test-impact-analysis-implementation-plan.md)
and the [merge-only amendment](2026-11-11-133-merge-only-stop-the-line.md).

- **Local Python execution.** Apply the 80% `pytest-xdist` worker default
  in the local harness for parallel-safe TIA selections. Exercise one,
  two, and ten available cores and verify worker counts of one, one, and
  eight. Verify private fixture placement and exact selected outcomes.
- **Hosted execution.** Use T11–T14 (#148–#151) for distinct hosted shard
  jobs, immutable assignments, trusted receipt collection, and combined
  coverage. Use the same candidate in serial and sharded comparisons.
  Missing or duplicate receipts, degraded outcomes, and missing required
  child coverage hold the applicable gate. Qualify on AITM-hosted refs.
- **Qualification.** T35 ([#172](../../172/story.md)) compares the
  trusted selector, testmon's advisory results, and the full reference.
  It also measures the local worker default and separate hosted shards
  through the existing timing and coverage acceptance criteria. Testmon
  remains advisory during and after the comparison.

## Delivery constraints

The [PR #197 hold](../../139/plan/delivery-checklist.md) requires delivery
of private fixture roots for both Python lanes and a separate successful
hosted qualification under the existing eight-minute job limit before
any #197 rerun. Verify the complete Python job through wheel smoke and
artifact publication, the successful base job, and the exact-attempt
signed gate. Then refresh #197 to current trunk and run its own required
validation. A local result or partial hosted result leaves the hold in
place. See the [runtime and fixture evidence](../../139/plan/2026-11-11-139-ci-runtime-diagnosis.md).

#159 remains blocked by #157 and #158. The amendment records planning
direction. Implementation pickup and gate cutover use their existing
review and authorization requirements.
