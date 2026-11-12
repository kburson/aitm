# #210 independent completion receipt proposal review

Claude Opus 5.5 high. One Refine recovery. Proposal SHA-256 `c6bd7600893ddc3c59e68a98b7aa2b8c32147e21c080dc3aa198813c58029d36`. Packet SHA-256 `d399625899f91a4f8eb9d2da0c6bed39702d680b911f8736a8b35cab59baff8e`. Literal trunk `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`.

PASS

**Decision:** I accept the exact proposal (`d0c3df99a48055b4662dccdf743793ec631405cf`, at trunk `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, tree `b4a757f106b89086a24d0e909bc259d7b5b93c88`) as a bounded Refine scope amendment to #210. It lets #210 try to qualify a native carrier anchored at the completion of the command's own turn. This is the only recovery after the first HOLD, and it follows the route that HOLD allowed: "M08b4c's own independent JIT."

The amendment is viable for a structural reason. Under the current parser, the next-turn receipt opens a turn that can only close cleanly through later usage. The command turn is different: it already contains the post-output provider request and its counter, so it can close cleanly before the terminal. That removes the design contradiction behind the first HOLD without weakening any gate.

## What this PASS does and does not establish

| Accepted | Not established |
|---|---|
| #210 may seek a terminal at the completion of the command's own turn | That any qualified native carrier exists. The probe shows that today's public reader exposes neither a receipt nor a cursor through completion (rows 60 and 61) |
| The anchor change as scope for a later exact JIT | JIT readiness, any source change, Develop, or release |
| The 10-turn sample as a description of observed ordering | That ordering as a universal guarantee. The proposal says this itself |

A genuine native Desktop disposition positive through `ScopeState.read_source` remains a hard gate. Until it is shown, #210 stays open and so do its direct #204 and #119 gates.

## Corrections to record with the acceptance (non-blocking)

1. **Owner approval of the change itself.** The proposal says the anchor move needs owner approval *and* independent acceptance. What I was given shows the owner approved *submitting* it. Record the owner's explicit approval of the anchor change before the JIT. This PASS does not replace it.
2. **Sample mismatch.** The receipt-placement sample counts 10 completed tool-bearing turns. The event-shape sample counts 8 `task_complete`, 1 `turn_aborted` and 10 `task_started`. State whether these are the same chat and window. Also state whether each "usage record after last tool output" had a *changed* total. A repeated cumulative vector, which occurred 19 times in that sample, does not count.
3. **Output type.** The probe was corrected from function-call output to custom-tool output. The JIT must pin which output type a genuine Desktop disposition command actually produces. It must accept only that type and test the other one as a negative.

## Proof and invariants the exact JIT must satisfy

**No migration or reinterpretation**
- The completion-anchored terminal gets a new, closed, typed record and version. Codecs fail closed on mixed or unknown formats.
- `_route_proposal` and `verify_route_disposition` keep their next-turn behaviour unchanged: `BoundaryKind.TURN`, cursor `None`, exactly one `BOUNDARY_UNVERIFIED`.
- Existing #203 and #209 records never satisfy the new route.
- Both scope and journal already refuse a second disposition per hold. So a hold that already has a next-turn proposal stays held under the new route. The JIT may not add a "supersede" path for it; fresh holds only.

**Clean same-turn accounting before completion**
- The command and its output are serial, not parallel, with a matching call and segment.
- The completion matches the same `turn_id`. It is not a child or forked turn, and `root_turn_id` must be consistent.
- After the last tool output, a changed-total counter settles the post-output response. At completion, all of these hold: `response is None`, no ambiguity or conflict, not tainted, no enrollment output, no pending compaction, `seen_counter` true.
- Same source, session, stream, checkout and anchor project throughout.
- The typed current grant and request digest bind to this exact command receipt. A parser receipt ID alone is not enough.

**Negatives that must stay held and replayable**
- A completion without a counter, or with only a timed counter.
- A repeated or zero-delta counter, or a backdated one.
- Missing baseline, regression, or abort.
- Any changed-total usage after the terminal.
- Stale, copied, foreign, wrong-scope or disabled-capture inputs.
- A changed route or hold, or an expired hold.
- The existing `later_usage` and `counterless_completion` controls stay as negatives.

**Deferred accounting**
- Today's reader still reports `BOUNDARY_UNVERIFIED` at EOF right after completion. Making that frontier verifiable relies on an ordering guarantee the evidence does not establish.
- The JIT must either cite native producer evidence that a turn's final usage precedes its completion, or use a fail-closed design.
- Either way, it must prove that same-turn usage appended *after* completion cannot be consumed or reinterpreted. That covers a cursor or settlement advanced past it and any release already committed. Such usage must surface as held, replayable evidence, with an explicit fixture for it.

**Frontier**
- The terminal is at or after the original span end.
- The fixed physical prefix is rechecked before and after publication.
- There is no other boundary or usage after the terminal within the fixed read.

**Settlement**
- Exactly one atomic, writer-verified JournalChange carries the effective state and any proven settlement.
- Owner and rival are re-proven separately at adjudication; one owner's completion never settles a rival.
- Cursor and effective view stay consistent, and first ownership is retained.
- Crash before commit leaves everything pending; reading again after commit is idempotent.
- `_boundaries_settled` recognizes the new receipt only through the verified journal outcome, never through a key or hint.

**Bound**
- A measured checkpoint at or under the existing #210 limit (4 hours after its JIT). If that is not met, the JIT needs an independently accepted further split that keeps all native gates.

## Unchanged

- #204 and #119 stay gated until #210 is verified as delivered.
- Recheck Rank 228.2 and the parent, project and successor edges before Develop.
- Epic #2, C01 and production cutover remain out of scope.
