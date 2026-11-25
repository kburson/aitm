# #457 qualification checkpoint

| Acceptance route | Live result |
| --- | --- |
| Codex headless 0.171.0-alpha.13.2 on macOS | The caller enrolled a review-role attempt before launch. Automatic observation and exact delayed replay after reconnecting the store passed. The attempt stayed on #457 after selecting another story. The earlier version-mismatch probe is included in the story's cost table. |
| Codex Desktop owner and app subagent 0.171.0-alpha.13.2 on macOS | Readback from both actual kickoff rollouts passed with exact child-to-parent linkage. Callback handling and delayed retry passed with development fixtures. Native hook dispatch in a trusted live Desktop chat still requires qualification. |
| Claude Code 2.1.331 on macOS | A clean scoped headless launch automatically captured and exactly recovered the turn after reopening the store. Two earlier qualification attempts are included in the story's cost table. |
| Grok Build 1.0.92 on macOS | A fresh supervised headless turn automatically settled against exact retained usage and replayed after reopening the store. |
| AIPR sealed decision association | A fresh Claude Code native review produced a sealed revisions-requested decision. Authenticated AIPR status, the launch participant fingerprint, the pinned artifact digest and the response digest matched. The #457 session store associated the verified decision with exact native usage from the enrolled turn. A prior manual attempt retained usage and no seal. Automatic AIPR launch returned `APR_TRANSPORT_UNAVAILABLE`, and the existing manual broker carried the successful retry. Codex sealed-review coverage retains the #434 gap. [AIPR receipts](457-aipr-qualification.json) |
| Protected planning publication | Published one actual #457 Codex headless receipt to GitHub, then verified an identical remote replay. Concurrent writers, ambiguous acknowledgements, identity conflicts and privacy are covered by local Git fixtures. |

The Codex live desktop readbacks took 40.821 ms for the owner and 4.383 ms for the worker. Codex headless exact recovery and persistence took 2.177 ms. For Claude and Grok see the timed adapter and reopen readback in [provider qualification](457-provider-qualification.json). Initial remote publication and readback took 3720.581 ms, and remote no-op replay took 903.210 ms. Source reads, normalization and Git publication requested zero additional model turns. Provider qualification itself used model turns as itemized in the story.

[Protected planning publication evidence](457-remote-publication.json) · [Codex Desktop hook lifecycle](https://learn.chatgpt.com/docs/hooks)

## Remaining live Desktop gate

Run one fresh Codex Desktop turn after the app has loaded and approved the project-local capture hooks for the enrolled thread. The parent must start and complete through installed lifecycle callbacks, and it must dispatch a real supervised app subagent with the corresponding child callbacks. Verify that the two receipts retain their pre-dispatch assignment after a later story selection and that delayed native replay leaves the bytes unchanged. The live kickoff readback and callback fixtures do not establish that dispatch path. Keep PR #460 in draft and #457 in Test until the live readback exists.
