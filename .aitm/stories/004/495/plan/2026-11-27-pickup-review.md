# #495 accepted pickup review

Grok 4.7 Build Fast returned PASS.

**PASS.** The #495/C108 plan matches the accepted replan. It is safe to implement as a docs-only facts slice.

**Scope.** The only deliverable is `docs/architecture/legacy-sdlc/action-and-evidence-facts.md`. C108 records the three resident actions, source/test-backed retry, waiting, and recovery, plus markers, typed outputs, historic schemas, review/close evidence, and kind differences. Shared rows stay shared: historical schemas with C107; runtime evidence with C109; deep-dive, plan/estimate, acceptance, dependency, and blocker facts only where the crosswalk names C108. Guard inventory, parent eligibility, story ownership, verbs, directives, hooks, and decision dispositions stay on C107, C109, and C110.

**Authority.** No legacy or Core code changes. Current Core decision policy stays with C110. Runtime hooks and authority stay with C109. The accepted state flow, JIT review threshold, and host authority stay as they are. Ledger issues #12, #37, #80, and #241 remain gated on the C110 trunk decision fixture. Any other named consumer cites the matching disposition at its own JIT.

**Registered actions.** The plan traces exactly the three registry rows through the shared runner:

- `develop` / `residentActions` / `developVerificationAction`
- `test` / `residentActions` / `testQuickCiAction`
- `review` / `residentActions` / `reviewAgentValidationAction`

For each, it requires state visit, intent and correlation, serialization point, and how complete, waiting, failure, and pause are reported. Retries must separate current durable proof, a pending wait, and a restarted visit. Missing-capability and read-only runner paths are in that trace. Terminal closeout is evidence, not a fourth resident action.

**Evidence and recovery.** The facts file must pin implementation and test evidence for source/head, receipt versions, typed outcomes, state-entry, Test and Review evidence, independently approved source, and terminal closeout. It must record migration-relevant historical marker formats and kind-specific exceptions, separate authoritative facts from provider projections, and leave opaque or unverified evidence explicit. Representative restart, waiting, and stale-proof cases must be cited from the pinned Node tests with exact paths. Gaps stay explicit rather than filled in.

**Source pin.** Legacy source is commit `c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905`, tree `844ae26bb169e8618e45fc3b1aedb57f44896fe0`. Integration base is `3e08d0b48e884445edee9217b8db9b64cce67afc`, which already contains verified guard inventory PR #535. C107 `guard-facts.md` is an input. Draft slice PR #536 is the delivery vehicle.

**Delivery gates.** Check link targets and Markdown, and run the installed Core suite. The reviewed Markdown path uses the applicable hosted repository CI. Where the path filter excludes the separate Core job, check Core inputs against that passing hosted baseline. After that exact hosted candidate passes, undraft the PR, run Grok 4.7 SAR, run the trusted verifier, and verify the integration landing before closing #495. Undraft does not change the candidate SHA. Those later checks bind to that same candidate.
