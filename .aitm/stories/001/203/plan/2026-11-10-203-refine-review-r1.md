# #203 independent Refine review round 1

Claude Opus 5.5 high. Reviewed split SHA-256 `71c785d75a269bd606ab48e203cde10613b14398352932359676fbe6688ce804` on November 10, 2026 America/Chicago.

# HOLD

Most of the split holds up on the supplied evidence. The graph is acyclic and keeps both the #119 and #204 order. The three leaves are each within the four-hour cap, each has its own JIT, and M08b4a issues proof without releasing anything. I'm holding it because the artifact says it "carries the complete accepted M08b4 requirement through the three leaves", and that claim isn't true as written. Three original deliverables or constraints have no owning leaf, and one native authority record contradicts the narrowed #203. All four are fixable by amending the text. None of them requires removing a gate.

I reviewed the supplied text only. I did not recompute `71c785d7…`, so this verdict covers the bytes as pasted.

## Blocking findings

**B1. The effective ScopeState hold transition has no owner.**
- The legacy `dispose` moves a hold to GAP or RESOLVED inside ScopeState.
- M08b4a leaves hold state unchanged. M08b4b owns the "scope/coverage projection" and M08b4c owns cursor settlement, but neither says whether the ScopeState hold changes or stays HELD while the journal changes.
- `view()` and `_timeline` read hold state, which affects `prior.held` and routing. So the two stores could end up disagreeing.
- The split must name the leaf that makes the ScopeState hold and the journal outcome agree. It must also say whether that happens in one atomic write or by deriving one store from the other under the existing publication fence. The original "atomic local JournalChange" deliverable depends on this.

**B2. The #115 keyed snapshot contradiction check has no owner.**
- The original requires evaluating these contradictions "against existing claims under real native authority" and "record the dependency".
- The split only says the inputs stay held. No leaf owns the held-input test against existing claims, and no leaf owns the recorded Grok admission dependency.
- "retained unsupported coverage" in M08b4c is too vague to count as that owner.

**B3. Required "keep unsettled" behaviours are missing.** None of these appears in any leaf:
- M09 owns publication of journal-only events. Nothing in the chain may invent a project ACK. The #203 issue says this; the split drops it.
- OVERLAP_UNVERIFIED and all aggregate diagnostics stay unsettled until M08b5.
- A scope difference on copied usage must never become a causal usage revision.
- The quota-only, identical generic and mixed holds are stated as policy but have no executable negative test in any leaf.

**B4. #203's native authority contradicts its new, narrower scope.**
- #203's title, body and `plan-origin` still define the whole M08b4, including `record_disposition`.
- The split narrows #203 to M08b4a but never says to amend that record. Without the amendment, #203 either can never close or closes while claiming M08b4 is done.
- Required: retitle and re-scope #203 as M08b4a, pointing at this split. M08b4b and M08b4c each get `plan-origin` set to this split.

## Verified on the supplied evidence

- **Graph:** 202 → 203 → b → c → 204 → 119. Every leaf also directly blocks #119, the extra 203 → 204 edge is kept, #204 keeps its own direct #119 gate, and there is no cycle. All three stay direct children of #100.
- **Budgets:** 3.75, at most 4 and at most 4 hours. M08b4c is allowed a further accepted split.
- **Proof-only work releases nothing:** M08b4a only proposes GAP or RESOLVED. Routing, holds, journals and cursors stay unchanged, and settlement belongs to the journal leaves.
- **Legacy behaviour:** `dispose` and its test stay as they are. A v1 `_Resolution`, which carries no target or witness, gives no new authority.
- **Preflight:**
  - The appended file starts with the original bytes, so the prefix is unchanged.
  - Source, stream and session match.
  - The terminal at ordinal 29 is at or after the hold end (19), and no observation ends after the terminal.
  - The legacy path refuses, and the hold view is unchanged after the refusal.
  - This shows the gap the split is meant to fill.
- **Gates and requirements carried:** the #204 positive folded-proof gate and the source order stay in force. Each schema-change review requirement is carried as a JIT obligation in M08b4a, and "strict v4" in M08b4b.

## Conditions to carry into the amended split (not optional)

1. **New issues and Rank.**
   - M08b4b and M08b4c enter Backlog and each get their own independent Refine as well as their own JIT. The #199 rule requires this and the artifact says only "JIT".
   - Read back that Project 24 Rank accepts 228.1 and 228.2, and that no other item has those values.
2. **No early release.** M08b4b moves no cursor and settles no dispute. M08b4c records each settlement as a single change that extends `record_disposition`.
3. **Re-check at adjudication.** A proposed RESOLVED is re-checked when the journal acts on it: the hold must still be unexpired, the route the same and the authority current. A stale proposal falls back to GAP or held.
4. **Holds created before M08b4a.** These have no retained physical witness. They stay ineligible for the new proof unless the #203 JIT fixes an exact reproof path.
5. **Fixtures.**
   - The M08b4a end-of-file positive and the M08b4c no-later-usage fixtures must not depend on the preflight's backdated counter (`CUTOFF - 1s` inside a turn stamped `AFTER + 6s`).
   - They must also not depend on a counter that adds zero usage.
   - Add a negative case with genuine usage after the terminal.
   - Drive these through the public read path, not `_capture_position` or `_native_cursor`. The preflight discards `_capture_position`'s return value.
6. **Unchanged state.** M08b4a's tests assert that `view()`, holds, journal and cursors are byte-identical before and after proof issuance and on replay.
7. **Read back before Develop and before Close.** Read back the full native graph before #203 Develop and before Close. Never close #203, M08b4b or M08b4c while a direct successor gate or the #119 gate is missing.

Once B1–B4 are amended into the split, I'd expect the resubmitted bytes to pass. Even then, a PASS authorizes only the split and the native graph, not Develop or code.
