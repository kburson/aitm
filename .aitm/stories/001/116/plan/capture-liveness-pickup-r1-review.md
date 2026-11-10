# #116 M06 liveness pickup review round 1

Claude Opus 5.5, high effort, completed the independent local pickup review on November 10, 2026. [Exact proposal](capture-liveness-pickup-r1.md) · [Earlier source hold](source-review-attempt-2.md).

# Verdict: HOLD

I reviewed only the supplied packet and used no tools. The refinement does not take on later work. Scheduler, journal, qualification, adoption and service remain with their owners, and the gates and the 4.0-hour estimate stay as approved. Four parts are sound:

- **Callback omissions:** a missing callback entry never counts as proof that a stream is gone.
- **Absent streams:** the gap is open-ended, so no physical end is invented, and the gap is never backfilled.
- **Earlier evidence:** evidence that was already staged and authorized keeps its original eligibility.
- **Applied receipts:** a command reaches "applied" only when the per-stream results, the permission change and the receipt are saved in one write.

These problems block a PASS.

## Blocking corrections

**1. Waiting on an unfinished tail brings back Finding A.** The plan holds the command while a Codex turn is in progress or the last line is incomplete. Nothing guarantees that ends:
- A Codex turn whose process crashed never settles. `read_codex` keeps its checkpoint at `None` for good.
- A partial last line from a dead writer never gets its newline.
- A Claude stream that died before its pending rows reached the commit frames stays that way.

In each case the disable waits forever while the other streams keep being admitted. Waiting also places the fence after rows written after the owner's command, so a long turn that started before a disable stays eligible all the way to its end.

Recommended fix:
- Arm every present stream at its count of complete rows when the change is first set up.
- Record `[next ordinal after the durable prefix, fence)` as a gap for that stream.
- Treat any observation whose original span starts in that gap as a crossing gap. The accepted M06 contract already says an unsplittable span crossing a fence is a gap.
- A partial last line will later become row N. Either put the fence at N+1 or include row N in the gap.

This only works if the reader reports where an unfinished Codex turn or Claude commit run starts. If that needs M04 adapter changes, reopen planning rather than wait.

**2. Show that an idle stream can actually reach the condition.** "The checkpoint covers every complete byte and no commit run is unresolved" must hold for a quiet, fully finished stream from both providers. Both readers split rows into committed rows and lookahead rows, and the packet doesn't show how that split is made. If either reader always holds back its last rows until a later row arrives, the quiet-stream fence never fires. Run the idle-plus-active disable test separately for Claude and for Codex.

**3. Use one fence rule for every stream.** For a stream that grew after the change was set up, the plan uses "the first qualified boundary at or after the armed next ordinal". That leaves rows between the armed position and that boundary under the old permission. Instead:
- When the setup read certified the stream's tail, the fence is that armed next ordinal.
- Any later read only checks that the armed prefix is unchanged: same locator, incarnation, offset and prefix witness.
- If that check fails, set the stream up again. Never move the fence to a later boundary.

With this rule, "advanced after arming" no longer needs its own case.

**4. The fence must be an absolute file row number.** `_lines` starts its count at 0 for whatever stream it is given. The fence has to use the same absolute numbering as boundary ordinals, so state that and test resuming from a nonzero checkpoint. Rows that are oversized or don't decode still count, which `_lines` already does. Also cover a zero-byte file: its fence is ordinal 0, and its witness is the origin value (`source-origin`), not a `source-prefix` value.

**5. Proof of absence needs its own directory walk.** `_transcripts` skips any `OSError` and moves on, so it cannot be the basis for proving a file is gone. Require a new strict walk that:
- fails on any error;
- rechecks every directory's identity and timestamps only after the whole walk finishes, which catches a file moved between two directories mid-walk;
- produces a proof that is never saved and is only valid within the same apply pass, under the coordinator lease;
- is a private type that callers cannot construct, like `VerifiedBoundary`.

**6. Define the private interface in types.** The plan needs to spell out:
- `locate(known) -> {stream: Located | VerifiedAbsence | Unavailable}`.
- `VerifiedBoundary` with two variants, `NativeBoundary` and `StableTailFence`. Only the source verifier can produce them, and each has its own key namespace.
- Which variants the direct `set_permission` and `enroll_stream` calls accept.
- That `apply_pending` differs from the approved `boundary_verifier` signature, so later work items consume this new shape.

As written, the stable-tail fence is neither "an adapter-produced boundary" nor "an observation" under the approved contract. The extension has to be explicit, not implied.

**7. Read blocking during a pending disable is too broad.** "Closes ordinary new-read admission for that project/source edge" stops reads of rows before the fence that haven't been collected yet. That silently narrows eligibility that M06 already accepted. Change it to a per-stream limit at the armed fence. Rows before the fence stay readable after the change commits, as long as the root is still approved. Likewise, "close collection for the edge" in the absent-stream case should apply only to the absent stream.

**8. One pending command per project/source pair.** Allow at most one armed pending command per pair, taken in durable queue order. The earlier hold's risk that two commands both get armed is otherwise still open.

## Non-blocking (state explicitly)

- **Changed root and adapter `ValueError`:** say whether each holds the command or rejects it, and test the chosen outcome.
- **File that returns without continuity:** it stays held and never enrolls as a new stream under the same stream key.
- **Nested Claude streams:** say that they are out of scope and fail closed.
- **Remaining budget:** give the number of hours left out of the 4.0, not just "the remaining budget".

## Tests to add

- An abandoned Codex turn, a permanently incomplete last line and a dead Claude commit run each end in a fence plus gap, not an endless wait.
- Idle-stream fences for both providers.
- Resuming from a nonzero checkpoint and the zero-byte file case.
- A rename race and an unreadable directory during the absence walk.
- An absence proof cannot be reused in a later pass.
- Two pending commands on one project/source pair.
- Rows before the fence are still readable after a disable commits.
