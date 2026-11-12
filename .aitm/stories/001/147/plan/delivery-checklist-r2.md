# #147 delivery checklist addendum — attempt 1 replacement

This addendum continues the original [attempt 1 delivery checklist](delivery-checklist.md). Test → Develop was recorded with independent source findings at planning `86feef6f22ecf937574aece7a94662a846c05e47`. The accepted plan and JIT still apply, and the implementation estimate remains 3.5 agent-hours.

- Existing [PR #261](https://github.com/kburson/aitm/pull/261), target `trunk`, pinned base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, exact replacement head `0d8f8ea353d71ab19802e882ceecbd105e6837ae`, tree `9699130f9be8411cb2a5646197e803956b1ef1b3`. The original `a9f97f937369192b6f565f6d5cec1e26340358ab` is preserved in ancestry.
- The [original run 43140683160 attempt 1](https://github.com/kburson/aitm/actions/runs/43140683160/attempts/1) completed successfully on `a9f97f9`. Both source findings held owner disposition for that candidate. The old hosted result is retained on its original head.
- The correction binds `ControlCandidate.suite_policy` to the existing caller-authenticated T02 `SuitePolicy` and exact `Scope` policy hashes, and validates nested T02 reference scope provenance. Only the two owned paths changed. The exact replacement passed 55 focused, 231 related and Ruff checks. [Replacement local validation](local-validation-r2.md)

- [ ] Push the replacement head using the existing branch and PR. Read back exact current head and base and record the new Test checkpoint.
- [ ] Require fresh #103 exact-candidate jobs, authenticated run/attempt and ordered tested-merge parents/tree. Obtain the existing exact tested-tree owner disposition. Run the protected-target verifier with that independent disposition.
- [ ] Obtain a new independent source verdict after the replacement's exact hosted proof passes. Continue normal review, delivery mapping, signed implementer retrospective and closure using the original checklist.
