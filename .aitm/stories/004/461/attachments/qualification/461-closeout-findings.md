# Story #461 closeout findings

The same disposable Codex Desktop agent recovered its own completed owner turn and one supervised child after a forwarded prompt, then published both receipts through the existing writer. Protected `planning` contained one byte-exact revision for each identity under #461. Replaying the frozen batch returned the same commit and created no registration. [Receipt commit](https://github.com/kburson/aitm/commit/af046d26d724e1effca8df302d2baff4001cb5d5) · [Readback evidence](461-closeout-readback.json).

| Qualification leg | Verdict |
| --- | --- |
| Live composer capture and delayed callback settlement | Unrun for #461. The owner chose direct forwarding. #457 provides the prior composer evidence. |
| Forwarded automatic owner capture | Failed. The capture turn completed, SubagentStart returned 0, and both terminal callbacks returned 2. The wrapper recorded no UserPromptSubmit. The owner Stop returned 2 and the store retained no owner callback. The shipped handler checks enrollment before saving a terminal callback, which is consistent with the missing owner-start event. The live hook store retained one child callback with pending binding and exported zero receipts. No status 3 was observed in this run, so it supplies no evidence of the planned delayed-callback path. |
| Exact retained recovery and agent-owned publication | Qualified pass after human authorization and explicit recovery. The retained child named the exact owner turn from app readback. The original live capture store was switched to #458 and the unbound child retry returned 2. The same agent explicitly enrolled the verified pair in a separate private store, recovered exact native records, switched the separate store from #461 to #458, and froze #461 through a fresh CLI process. The same invocation published and replayed the frozen batch using the separate writer context. |
| Origin refusal and unassigned evidence | Passed. A local unmatched `file:` origin failed the writer guard, the batch hash was unchanged, and both paths were absent on protected planning after the refusal. The exact #461 child remained pending, without parent or story, both in the original hook store and in the isolated CLI control. Both #461 and #458 exports were empty for those unbound attempts. |
| Transport ambiguity | Fixture-only pass in the shipped tests. The live refusal was a remote-identity mismatch, and the live write returned a normal result. The pinned focused suite passed 19 tests including lost acknowledgement and bounded rejection. |

**Overall verdict — qualified pass for exact retained recovery and same-chat publication.** The composer path stayed unrun in this spike. The forwarded route reproduced its automatic capture gap.

## Reproduction and evidence

1. Verify the #457 wheel and hook pins, app trust, isolated disposable chat and current GitHub rules. All 57 wheel Python files matched the shipped merge. The five scratch hooks were trusted. Select #461 in the existing capture store and forward one owner prompt that runs one native child and waits.
2. Record the completed app turn, callback statuses and retained child binding. Have the same chat switch the capture store to #458 and run `session-codex-hook … --retry ATTEMPT` in a fresh process. Check the original child remains unassigned and verify its exact parent in private retained data. A separate CLI control withheld owner-start and reached the same result.
3. Once the owner explicitly authorizes publication for this route, use the shipped `SessionStore.expect`, `recover_codex_desktop`, `bind` and `accept` to settle the exact pair in a private recovery store. Switch that store to #458 and run `session-export-batch SESSION 461`. The fresh-process batch matched the stored bytes.
4. Run `session-publish-batch 461 REPOSITORY BATCH` against the unmatched local origin, then against the authorized existing writer. Independently read the current GitHub branch protection, commit and both blobs, and enumerate story receipt paths for identity uniqueness. Repeat the identical batch once. The publication commit changed precisely the two receipt files.
5. Restore the original hook store selection to #457. Verify the same callback data and hook config digest.

| Receipt | Protected planning path | SHA-256 |
| --- | --- | --- |
| Owner | [Revision 1](https://github.com/kburson/aitm/blob/af046d26d724e1effca8df302d2baff4001cb5d5/.aitm/stories/004/461/attachments/effort/session/2033d1a0782e55bba0b7bad845bb36106ab6ad725d74e5bcbc4cda04c9119d04-r1.json) | `f64fe88983e3e1230f12c52be424dcd41e1588a17bf17e3aabd3c31c64d50998` |
| Child | [Revision 1](https://github.com/kburson/aitm/blob/af046d26d724e1effca8df302d2baff4001cb5d5/.aitm/stories/004/461/attachments/effort/session/f16038236a38d5aaaa636948e9cb9467a6c61e5e6ef029c765ccd9e0dcf2c858-r1.json) | `e19d4803d369f1a5727030e6c35e595c39461df78c2ab50fa7572f9ad1a4ea18` |

Publication used the existing GitHub SSH authority and the shipped writer. The successful forwarded closeout took 51.433 seconds of native owner engagement. Its local exact recovery took 18.48 ms, the CLI origin refusal took 197.77 ms, the writer's publish and internal readback took 3.848 s, and the replay took 1.009 s. The owner capture lasted 8.242 seconds and its child lasted 2.943 seconds with overlap. Two preceding Desktop closeout attempts spent 16.899 and 26.447 seconds confirming authority. One explicit owner authorization in the coordinating chat resolved the path. The coordinator forwarded the capture prompt, supplied the exact completed owner reference from app readback, and forwarded the authorized closeout. Three extra Desktop turns were used, including the two authority checks and the successful closeout. One command invocation recovered and published the earlier work pair. The closeout turn's own exact usage became available after that turn ended. It needs later settlement to become a published receipt.

The usage record separates cached input, new input and output tokens and includes native timings for the four Desktop owner turns, one supervised child turn, and both sealed plan XPR rounds. The prices are standard API list estimates, and verified billed cost is unknown. [Usage and timing evidence](461-closeout-usage.json).

## Recommendation

Using #457’s composer qualification as the basis, keep collection on the owning agent. On a subsequent closeout turn, retry exact pending work, freeze the story batch, and call the existing writer. Verify the protected readback before reporting delivery. Treat the closeout turn as later evidence. A forwarded start gap requires exact retained attribution and an explicit recovery path. Keep an unproven child pending and unassigned. If the caller has access to the existing writer, the supported frozen-batch command can use a separate writer context in the same chat, as observed here.

[Accepted plan](../../plan/2026-11-25-agent-owned-closeout.md) · [Forwarded addendum](../../plan/2026-11-25-forwarded-route-addendum.md) · [Capture and control checkpoint](461-forwarded-capture.md).
