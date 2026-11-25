# #434 independent evidence review

A separate headless Claude Code session used Sonnet 5.5 and reviewed the sanitized results and receipt. This was an off-platform evidence review.

Report SHA-256 `53c3dce04963d762353caa75f203a6dc4ce7547651dfb6d20135b76043f40219`. Receipt SHA-256 `dc0fb4daf5bdd6deb376ea61cfbb594fb85c06763e96e2a2a31e040c40b85af4`.

PASS

The report and receipt agree on all five points.

- **Negative admission:** Both say no tested route passed admission. Both fixtures ended at `awaiting-reviewer` with the broker offline, with `reviewer_joined` false and 0 sealed decisions.
- **Usage by attempt:** The stock attempt is 60,458 input (48,768 cached) and 349 output, and the scoped attempt is 93,157 input (82,816 cached) and 430 output. Terminal totals equal the retained rollout totals in both, and the reasoning-output counts (0 and 24) are consistent with the "includes" statements.
- **Lock controls:** The macOS host sequence matches, with a live owner and then `APR_REVIEW_LOCKED`. After termination the lock reads `unknown / identity-unavailable`, and `APR_REVIEW_LIVENESS_UNKNOWN` appears twice. The Linux sequence also matches, with identity-match, contention, `stale / process-dead`, retained evidence, reacquire and an absent lock after release.
- **Omitted conditional tests:** Sealed rounds are 0, and interruption and replay are `not-run` with reason `no-admitted-route`.
- **Evidentiary limits:** Billed charges are `not-measured`, no Linux model turn ran and no supported Linux host was tested. The lock controls ran outside the reviewer sandbox, and the receipt's `control_scope` says so.

Three report details have no receipt backing: readable procfs, "Docker Desktop" and the wrapper's "three exact fixture operations". The receipt holds only the wrapper hash. They are narrative context, not claims the conclusions depend on, so they are not blocking.
