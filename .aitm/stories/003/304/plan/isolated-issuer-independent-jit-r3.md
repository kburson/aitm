[05:23:59]
**JIT_304: PASS**

I couldn't recompute either SHA-256 because I have no tool that can read local files. I judged the evidence on the excerpts you pasted, and trusting those hashes rests on your run.

**R2 blocker (R1 #2 remainder): closed**
- **Where `_admitted` comes from.** The field already exists on trunk at `monitor_scope.py:341` as a frozen `frozenset[UUID]`.
  - It is filled at `:1277`. On the Codex branch the value comes from `_admitted_readers` (`:1193`). On the Grok branch it is the empty set (`:1250`).
  - `_admitted_readers` raises unless at least one admitted unbounded reader with a valid physical prefix exists (`:1056`, `:1073`). So a naturally issued Codex batch always has a nonempty set, and a Grok batch is always empty.
  - The draft states what the set means and does not claim it proves who owns an observation.
- **Callers.** The draft lists every direct caller of `_require_batch_qualification`, `_recheck_batch`, `_journal_view` and `_fresh_view`, and the AST extraction matches on trunk `6b64ea8` and #300 `0542848`.
  - For each caller, the only change is the `decision` payload on an exception that was already raised.
  - Lease, identity and view failures happen before the decision branch, and an unpinned root yields `None` (`monitor_registry.py:701`).
- **Prepare side.** Trunk has no coverage recorder. On #300 the only coverage catch is around the first read and Grok preflight (`prepare:860–882`), and `_fresh_view:902` and both `_reserve` rechecks sit outside it. So no new recorded exclusion appears.
  - This holds together because trunk's `read_source` already raises decision-bearing refusals through `_approved_candidate(observed=True)`. Upstream handlers already see that payload; only where it can now be raised changes.
- **Hosted tests.** All four cases are specified with exact types:
  - admitted, first reserve: decision expected;
  - admitted, same-progress retry: decision expected;
  - empty, first reserve: `_LiveSourceUnavailable(None)`;
  - empty, same-progress retry: `_LiveSourceUnavailable(None)`.
  - The tests also cover a refusal on the prepare side, rollback after staging, and checks that durable state and reopened state don't change. The empty-batch monkeypatch is limited to one real prepare and is restored before revocation.

**Pilot, currentness, proof, reachability:** unchanged from what R2 closed. R3 adds nothing that reopens them.

**Conditions for red/green and Test (not blockers):**
1. **Revocation must not change the batch's registry view.** If owner revocation or the forced checker failure changes `RegistryView`, the admitted cases will fail at the view check (`:1589`) with `LedgerError` and never reach the decision. The same applies if `reserve_batch` with zero candidates, or the order of the empty-batch retry comparison, stops the call before `_fresh_view`. If any exact-type assertion can't be met, stop and re-JIT; don't loosen the assertion.
2. **Make the `reserve` test unconditional.** The single-candidate `reserve` test is written as "when the fixture has a routed obligation." Either build the fixture so it has one, or record in Test evidence that this route wasn't exercised.
3. **Add a handler check to the AST test.** No `except` clause that catches `_LiveSourceUnavailable` (or a base class) may read `.decision` anywhere except the #300 first-read catch. Without this, the "only the payload changes" claim isn't proven for boundary, view and settlement callers.
