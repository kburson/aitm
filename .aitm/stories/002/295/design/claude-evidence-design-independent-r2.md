[18:09:08]
# DESIGN_295: PASS

# CARRIER_SCOPE_INSERTION: PASS, with conditions to meet at activation (listed below)

## Scope of these verdicts

The verdicts cover the R2 design at `9edffbf4…c3b74d`, read against `review-r1.md` (`0119ebb0…`), R3 (`75d073bd…`), the two Claude JSON receipts (`d94f8b4c…`, `dcdc61be…`) and the Refine HOLD (`52741b3d…`).

- **Digests not checked.** This session has no file-read or shell tools, so I could not recompute any digest. Both verdicts hold only if the bytes match. That also means the Refine HOLD's point B3, which needs the R3 bytes checked against `75d073bd…`, is still open.
- **Possible filename/content swap.** The supplied text for `claude-quota-three-channel-join.json` has the schema `three-channel-corroboration`. The text for `…-monitor-readback.json` has the schema `single-flight-join`. Confirm which content goes with which digest.
- **Graph before insertion matches R2's starting state.** #119's prerequisites are {118, 199, 201, 202, 203, 209, 210, 295}, and only #295 is open. #295's only prerequisite is {210} and its only dependent is {119}. So nothing was created from an unaccepted design.

---

## DESIGN_295: PASS

**D1 is resolved.**
- The new scope and authority need explicit acceptance from the parent plan whatever the estimate. R2 says so twice: "regardless of estimated size" and "even if the work fits an existing estimate."
- The new account authority, the launcher, the OTLP receiver and the adapter-constructor work all move to the separate carrier story. #295 keeps exactly its R3 containment scope.
- This is the first resolution path the Refine HOLD offered.

**D2 is resolved.**
- **How the hosted fixture gets its evidence:**
  - A hash-pinned test subprocess uses real pipes and the same loopback receiver.
  - It generates fresh identifiers and keys on every run.
  - The real registry arms the scratch source, captures its first boundary and authorizes the fixture account.
  - The same verification code as the native path issues the evidence.
  - The cursor is produced only through the public journal entry points.
- **Why this isn't transplanted evidence or cursor seeding:** each run generates fresh inputs inside the test, and nothing is imported or written directly to persistence.
- **Kept apart from production:** the fixture mode is not available to the runtime support matrix, and the carrier still needs its own native run before delivery.

**The six items R1 left for later are all handled.** Each is either answered or explicitly handed to JIT with a fail-closed fallback:
1. **Mapping each diagnostic to what closes it:** cold-read step 5. If anything is still unresolved after the real cold read, the gate stays held.
2. **Claim count:** cold-read step 3 expects two admitted claims and one cursor, with the warmup excluded.
3. **Trust on first use:** authority item 1 now names it as such and lists what the operator checks.
4. **Replay record:** the v1 contents, the size cap, dropping raw output, retirement, and the restart rule that quota can be checked only against its commitment.
5. **Cold-read step table:** the cold read now clearly comes after the measured turn.
6. **Public paths only in tests:** stated.

**Gates are preserved.**
- No graph change from the design alone.
- #295 stays in Refine, and its Refine recovery and JIT happen only after the carrier is delivered.
- The R3 tests still run red then green, and the hosted-validation, signing and source-review requirements stay.
- #119, #122 and #123/#124 keep their ownership. Epic #2, C01 and production cutover stay excluded.

**For JIT (not blocking)**
1. **Setup vs. warmup.** "Separate setup and warmup" (cold-read step 1) could mean a fourth Claude process, which conflicts with "three … invocations." State whether setup is a Claude invocation in the same session. If it is, its rows must be shown to be excluded like the warmup's.
2. **The native cost-state sideband is a source R2 doesn't name.** If it is per-project state in `~/.claude.json`, it is a native file outside the pinned transcript. Other Claude processes can change it at the same time. JIT should name it, put it under the same custody, and fail closed if it changes between snapshots.
3. **Keep the fixture executable out of runtime.** Add a negative control showing the runtime launcher refuses the fixture executable's hash and configuration.
4. **Fixture provenance.** The carrier's hosted fixture should record what R3 requires for its fixture: a provenance digest, the surface and build, and the field allowlist.
5. **Which public diagnostics surface?** "Read-only public diagnostics" must name an existing public reader. If none exists, the tests should assert through `coverage_changes`, `cursor_for` and the claim dispositions only. Otherwise a new public API turns up without having been scoped.
6. **Support-matrix effect.** State that the carrier adds no entry to the provider support matrix. "Qualify … carrier" could be read as a support claim.

---

## CARRIER_SCOPE_INSERTION: PASS

**What's exact and sound**
- **Identity:** the stable plan key `M08b6-Claude-Carrier`, the exact title, and a direct Epic #100 parent.
- **Edges:** its only prerequisite is #210 and its only dependent is #295. #295's prerequisites become {210, carrier}.
- **#119 is unaffected.** It has no direct edge to the carrier, and its exact R3 prerequisite set is unchanged.
- **Ownership split:**
  - The carrier owns the launcher and its custody, the proof storage, the writer-issued authority, and the fixture mechanism.
  - #295 keeps all of R3's hold, expiry, duplicate and unrelated-diagnostic behaviour.
  - The carrier owns none of the overlap logic, ACK, publication, report or export.
- **Files:** limited to listed module categories inside `packages/aitm-usage`. Exact paths and sizing are decided at the carrier's own Refine/JIT. An oversize story needs a separately accepted split. No dependency changes by implication.
- **Order:** PASS is published and the graph is verified natively before the carrier's Refine opens.

**Conditions at activation** (the same kind R1 attached to #100)
1. **Record what it amends.** Cite the base it amends: the frozen Epic #100 plan plus R3 `75d073bd…`. State that it replaces only R3's M08b6 line "Prerequisite #210" with {#210, M08b6-Claude-Carrier}. All other R3 text stays in force.
2. **Name exact readback targets.**
   - #295's prerequisites are exactly {210, carrier} and its dependents are exactly {119}.
   - The carrier's prerequisites are exactly {210} and its dependents are exactly {295}.
   - #119's set is unchanged and has no direct carrier edge.
   - The carrier's parent is #100, and it has no link to #2.
   - Record the numeric ID against the plan key through native readback.
   - If any step fails, leave the prior graph in place and stop, as R3 requires.
3. **Sequence it with the #100 sibling activation.** R1's #100 PASS states that #295's prerequisite set {210} is preserved, and its activation captures the #100 child set before any write. Adding the carrier changes both. Do one of the following:
   - Run the #100 activation first and read it back, then insert the carrier.
   - Insert the carrier first and update the #100 activation's expected child set and #295 readback.

   Either order fails closed, but neither procedure should stop because of a mismatch it was never told to expect.
4. **Leave exact paths to the carrier's Refine.** If any path falls outside the listed categories or outside `packages/aitm-usage`, the scope must be accepted again. In particular, any discovery-module work for the typed locator-ambiguity refusal stays with #295. The carrier doesn't take it on silently.

**Downstream risk this insertion leaves open:** the carrier only gives cursors to supervised scratch runs. M19's "receipt and cursor continuity on … Claude Code" for ordinary, unsupervised sessions is still unaddressed. R2 makes no claim about it, but M18/M19 Refine should know it is still open.
