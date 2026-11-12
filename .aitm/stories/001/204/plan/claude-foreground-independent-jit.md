[15:04:40]
HOLD

**Decision.** The producer predicate from Refine still stands. Nothing in this packet shows a concrete path, under the existing gates, that gives either member original eligible ownership and a source span. The packet itself says there is no positive authority test. The code excerpts show why.

**Why the existing model cannot issue the route**
1. **Child observations never enter the verified stream.** The adapter gives nested child usage its own stream, `_isolation(ledger, stream, "nested")`. Three places then drop anything outside `locator.stream_ref`: `_native_delta`'s `boundaries` filter, `_verify_next`, and `_observation_proofs`. No discovered locator carries the nested stream ref. So no epoch, frontier or scope proof can ever cover ordinals 10 or 17. That matches `same_stream:false` and `checkout_proven:false` under both roots.
2. **The covering parent has the same problem.** The aggregate gets `_isolation(..., "aggregate")`, is recorded as `PARTIAL`, and is gapped as `OVERLAP_UNVERIFIED`. The parent's own same-stream proofs (23 and 31) are evidence for the parent stream, not for the aggregate's span. The packet has no route that ties the aggregate's interval to the parent's own epoch without a new rule.
3. **Arming cannot predate the child.** `capture_frontier` and `_native_delta(arm=True)` only arm at the current complete EOF of a file that discovery has already found. The child sidecar is created by the native process after dispatch. Any arm placed on it comes after its own first frames, so the span [0, 18) would be admitted after the fact. That is a gate violation. Pinning the parent before dispatch does not change this: the parent's epoch is not the child's.
4. **The parent root is correctly refused.** Both locators derive `stream_ref` from the shared `session_ref`, so `_approved_candidate`'s `len(matches) != 1` check trips. Keeping that refusal is required, so the parent root cannot help.

**Child-only subroot result: does not qualify.**
- "Unique native locator accepted" is only an effect of narrowing the root. It is not evidence that the child is eligible.
- The child's `stream_ref` is the same session pseudonym as the parent's. Admitting it would put the child's ordinals in the parent's stream and epoch namespace, which is exactly the forbidden relabel or epoch reuse.
- Its observations are still nested-isolated and partial, with no checkout. There are no startup frames and no own scope evidence.

**Smallest gate-preserving experiment (read-only, no writes, no gate change)**
Run a test-only probe over the three pinned immutable captures, through the existing scope recognizer and `_observation_proofs` logic. It must not use the parent's evidence or the scratch hook. It asks two questions:
- **(a) Child:** if the nested isolation ref is supplied as the locator stream, does the child file *on its own* yield a verified checkout across [0, 18)?
- **(b) Parent:** does the aggregate's ordinal fall inside an interval that the parent's own enrolled epoch and scope proofs cover, using the parent's physical prefix only?

**Can present data prove it?**
- Present data can settle (a) and (b). The current readback cannot tell "no own scope evidence" apart from "never evaluated because the stream was filtered", and the probe separates the two.
- Present data cannot prove point 3, original admission before the child's first frame. No existing capture armed the child before it was created, and the existing primitives cannot do so.

**Smallest pre-M09 authority prerequisite (new issue, direct #119 blocker)**
- **Mechanism:** a writer-issued reservation of the child's stream and ordinal namespace, made under the pinned parent epoch before dispatch and keyed by the outer tool-use ID. The child is then admitted at offset 0 under its own authenticated physical prefix and its own scope evidence.
- **Why it needs separate approval:** this is a new permission and registry shape. It needs M08b-style schema and admission review, and it exceeds the four-hour bound.
- **If probe (a) is negative:** the native child is never independently admissible. #204 then cannot be satisfied under the accepted plan, and it needs a changed parent plan, independently re-accepted, rather than this prerequisite.

**Disposition**
- Keep `OVERLAP_UNVERIFIED`, the earlier frontier, routing, the journal and diagnostics unchanged.
- Record the failing gate on #204 as "no original eligible child or aggregate span; arm cannot predate the sidecar".
- Keep #204 open and #119 blocked.
