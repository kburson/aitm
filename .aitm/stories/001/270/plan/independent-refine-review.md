[22:04:39]
**PASS.** This is a valid and feasible follow-up scope that preserves the gates, with conditions. It stays inside M08b5 as a prerequisite to #204. It keeps the authority result read-only for the journal, leaves ACK and publication with #119, and does not change ordinary discovery, scope or report behavior. Two of the conditions below can still turn it into HOLD.

## Check results

| Check | Result | Notes |
|---|---|---|
| Approved-source consent | Passes if JIT fixes it | Consent rests on the existing root approval. It does not create new permissions or backdate scope, and reading origin metadata is kept separate from accounting reads. The wording is ambiguous in two places (JIT items 1–2). |
| Separately proven child origin and checkout | Passes | The packet requires a recorded absence before dispatch and a process-bound witness of the child's origin and prefix before any metered usage. The child gets its own namespace and an origin key not derived from path, inode or time alone. Its checkout is proven independently. |
| No reliance on the parent epoch | Weak | "A stored parent epoch *alone* cannot satisfy the child boundary" still lets the parent epoch count as part of the proof. JIT must remove "alone" (item 3). |
| Terminal fence | Passes as a direction, under-specified | Closure is checked against the process outcome, the fixed native files and late-append controls, and hooks supply no authority. The fence itself is left to JIT (item 6). |
| Four-hour bound | Stated, but at risk | A new namespace, a receipt store, a special lookup path, the full set of controls, restart checks and a live native rerun are a lot for four hours. The optional private-custody branch is the main risk (item 8). |
| Ordinary lookup and OVERLAP_UNVERIFIED | Passes if the entry point is kept separate | Ordinary ambiguity rejection is preserved, and the refusals are run on both unchanged trunk and the candidate (item 5). |
| #204 → #119 | Preserved | #270 sits before #204 inside M08b5. It does not depend on M09 or M11. |

## Choices JIT must fix

1. **Which root the child lives in.** The packet says the child proves its boundary "in that root" and asks to "reopen the exact approved root", but #269 found the child in a *separately approved* root. JIT must name the one root (or roots), the approval record and the project/provider permission edge in force at the child's origin. A permission change or revocation inside either span must hold.
2. **Where consent comes from.** Write "parent approval" as the existing root and provider permission edge. It must not be anything derived from the parent stream's enrollment or epoch.
3. **Parent epoch.** State that the parent epoch is neither necessary nor sufficient for the child's boundary. It authenticates only the parent span [37, 47). Keep #269's refusal ("Private source identity changed") as a regression test.
4. **The child's first eligible request and its full accounting.** The writer armed at ordinal 9, and the child has observations at 10 and 19. JIT must say which request is first eligible and what "the earlier metered request" refers to. M08b5 needs *all* of the child's accounting inside the authorized span, not just the selected request at [19, 20). If any child request falls outside the span, the result is a gap, not a positive.
5. **Parent duplicate locators.** #269 found two locators matching the parent, and the child sits in a separate root. Before spending the four hours, JIT must identify what the second locator is from the existing evidence. If the authenticated child origin key does not explain it, the result is HOLD. The special lookup must be a separate API entry point, not a flag on the ordinary lookup, and must not be reachable from ordinary scope or report calls.
6. **Terminal fence mechanics.** JIT must define:
   - the closure source (process exit plus fixed file sizes and hashes),
   - when the fence is checked relative to receipt issuance under the same lease,
   - how an append after the fence revokes or holds the receipt,
   - how error completion is handled,
   - how the closed child set is established, including extra and missing children.
7. **Fitting the existing capture model.** The child receipt must be a `VerifiedBoundary` / `CaptureEpoch` under the existing M06/M07 contracts, consistent with the migration rule's "new post-boundary origin". If it needs a parallel authority type, the scope changes the capture model and needs parent-plan re-acceptance, so HOLD.
8. **Storage and restart.** Pick one storage mechanism up front, and prefer the existing registry/epoch store. If private custody is needed, JIT must bound the receipt's reopen, expiry and revocation. JIT must also say which controls go in the four hours, and that going over the ceiling means HOLD, not a wider scope.
9. **What the observation window reads.** Name the exact bytes it reads and limit them to the approved root. Content before the boundary is used only to witness the origin. It is never kept or used for accounting.
10. **Isolation.** Pin the native client version and binary hash, and run with an isolated config. Scratch hooks must not touch any production settings.
11. **Baseline command.** Use the isolated fixture-root run (285 tests passing). Record that the shared system temp directory run is not a valid baseline, since its failure cause is still unverified.

**Turns into HOLD if:** item 5 cannot be explained from the existing evidence, item 7 requires a new authority type, or JIT cannot fit items 4, 6 and 8 inside four hours.
