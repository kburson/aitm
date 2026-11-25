# Disposable Desktop composer and forwarded route comparison

After restart, both runs used the same five authorized scratch commands, pinned adapter, standalone repository, exact chat and prompt. A supervisor and one child completed each run without hook retries. The native root turn sources confirm the app-tool-forwarded and composer routes. [Sanitized trace and replay](457-desktop-forwarded-route.json).

| Observation | Forwarded by app tool | Entered in Desktop composer |
| --- | --- | --- |
| Owner UserPromptSubmit at wrapper entry | Absent, including as a rejected-thread entry | Present, matched, adapter status 0 |
| SubagentStart | Matched, adapter status 0 | Matched, adapter status 0 |
| SubagentStop and Stop | Both matched, adapter status 2 | Both matched, adapter status 3 |
| Callback-based receipts after replay | None. Owner start enrollment was unavailable | Two complete receipts retained under #457 |
| Exact retained recovery from the native turns | Two complete receipts in a separate scratch store | Verified directly from the live pending callbacks |

The forwarded run did not enroll its owner. It retained its child callback and produced no live receipts. The diagnostic narrowed the missing event to before wrapper entry. The run does not distinguish whether the upstream route omitted the hook event or hook dispatch suppressed it. Exact retained recovery in a separate store recovered both turns, then preserved both bytes under #457 after a story switch and fresh-process readback.

The composer run enrolled the owner and child. Both terminal callbacks were saved pending while the native turns finished. With #458 selected, fresh CLI processes retried the exact child and owner callbacks in that order. The scratch store then held two complete receipts under #457, and a further fresh process read back identical bytes. The scratch selection was restored to #457. The forwarded child callback was excluded from this recovery because its start-time owner binding was absent.

The scratch test qualifies composer lifecycle and delayed settlement in this build. App-tool-forwarded live receipt capture remains incomplete. The original chat's hooks remain unapproved.
