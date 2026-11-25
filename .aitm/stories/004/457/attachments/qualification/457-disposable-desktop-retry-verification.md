# Disposable Desktop retry verification

The exact linked chat initially exposed only the bootstrap turn. After the owner authorized one retry, the coordinator sent the test prompt to that chat. Desktop recorded a completed owner turn with the expected reply and one completed supervised subagent. Exact source readback verified that the child's native parent-turn identifier matches the retried owner turn.

| Check | Observed result |
| --- | --- |
| Scratch hook, wrapper, and wheel digests | All match the pinned setup |
| Owner and subagent hook callback evidence | Trace absent. Zero launch enrollments, terminal callbacks, and receipt revisions |
| Candidate replay of exact retained owner turn | `unexpected-harness` |
| Candidate replay of exact retained subagent turn | `unexpected-harness` |
| Story switch and fresh-process receipt replay | Blocked because the candidate produced no receipts |

The pinned wheel recognizes a Desktop parent with native `thread_source: user`. The disposable chat created through the app tool is recorded as `agent_created_thread`, and the child rollout includes a copied parent header with that source. The current reader rejects both paths. This source mismatch explains the retained-read rejection. The absence of hook records does not establish why Desktop failed to produce the callback trace.

#457 remains in Test and PR #460 remains draft. The coordinator counted the completed owner and subagent turns directly from their exact retained metadata for accounting. That measurement is independent of candidate hook qualification.
