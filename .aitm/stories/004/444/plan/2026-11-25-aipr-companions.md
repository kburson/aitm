# #444 AIPR companion receipt reconciliation

The [portable effort plan](../../426/plan/2026-11-24-agent-effort-cost-implementation-plan.md) governs this story. Codex implements and coordinates delivery. Target `trunk` starts at `953a051f4954a14a8aeb8c310a561cafbede6185`. GitHub confirmed #437, #440 and #441 closed and Done.

1. Add a portable reconciliation projection over the existing immutable enrollments and fixed effort snapshot. Compare caller-verified review identity, round, attempt, reviewer and artifact to independently verified AIPR decision evidence. Bind usage to a caller-verified exact native observation. Reuse the receipt store for usage lineage and replay.
2. Prove decision-first and usage-first delivery, delayed and reversed rounds, replay after reopening SQLite and mismatched identity refusal. Preserve interrupted Claude and Grok usage and the failed Codex usage from #434 with their decision gaps.
3. Exercise the unchanged qualified Claude Code and Grok Build routes in disposable reviews. Verify sealed artifact and response digests, participant identity, terminal counters, and readback. Preserve only sanitized proof. Codex sealed reviewer admission remains a #434 qualification gap.
4. Obtain independent source review, authenticated hosted CI and trusted verification on the exact candidate. Verify remote merge-tree parity, sign off, close #444 and confirm its linked PR and engagement in Project 24.
