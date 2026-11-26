# Story #461 findings

## Scope and deployment

The live source was the #457-merged usage package at `87bc3d8a2875884014b59281117f68b9d63fabee`. All 57 Python modules in the qualified wheel matched that commit. The existing disposable Desktop hook configuration and pinned wrapper were verified, and all five hooks reported trusted and enabled. The ordinary AITM project hook settings were outside the experiment. The capture store retained its preexisting isolated origin. Publication uses the shipped freeze and import commands with a separately configured writer store for the same project.

| Qualification leg | Observation |
| --- | --- |
| Composer capture and delayed callback retry | Unrun in #461. #457 is the separately recorded composer baseline. |
| Forwarded capture and exact attribution | The owner and exactly one child completed. SubagentStart returned 0. SubagentStop and Stop returned 2. UserPromptSubmit was absent from wrapper entry, no owner terminal callback was retained, and the single retained child was pending with zero exported #461 receipts. The existing route-dispatch caveat reproduced. |
| Missing-binding CLI control | Pass. The same exact #461 child was run through a separate private CLI store with owner-start omitted. Terminal and retry both returned 2, the callback remained retained, the story and parent remained null, and both #461 and #458 exports were empty after switching. |
| Shipped fixtures | The focused Codex-session and publication suite passed all 19 tests on #457's merge. It includes lost-acknowledgement readback and a bounded refusal simulation. |

The original requested experiment and the forwarded fallback are documented independently. [Accepted plan](../../plan/2026-11-25-agent-owned-closeout.md) · [Forwarded route addendum](../../plan/2026-11-25-forwarded-route-addendum.md).
