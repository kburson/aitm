# #278 signed independent source assessment

**Source verdict: no material findings.** The reviewed candidate implements durable local advisory warnings and manual repair nominations. Signed by OpenAI Codex, independent review agent `/root/review148`. This assessment used a separate exact-head Git archive. Formal review admission depends on current exact #103 evidence.

- Repository and pull request: [kburson/aitm #283](https://github.com/kburson/aitm/pull/283)
- Literal target: `trunk`
- Base: `b1ff8ce027608da942ec8ac1c7bc124500c5f145`
- Candidate head: `e7fba46767bdad188d432f23584bb2c8e53f5381`
- Synthetic merge: `4a6c463b5e9088378c052f54c81cbf3a83508196`
- Candidate and tested tree: `b2355e454752baf77d71293fed539e966e796cbc`
- Reviewed plan SHA-256: `426dec2c7aa47166cf9b1fe8f4127d9608e12e5a4af793694ac91408ec906166`
- Independent plan review SHA-256: `d37ef87acb77ef660e63e3746e245d3f50b123c472bfc2aa0dd38d8238966632`

Two rounds of source review identified no-run freshness invalidation, retention of an older authenticated failure, sink binding and provenance collisions, exact failure-job evidence retention, and freshness of the warning when a prior failed lane becomes current. The candidate includes fixes and focused regression cases for those findings.

The live entry point reads #277 directly under the serialized SQLite transaction. The shadow entry point consumes saved evidence into a separate provenance-bound store. Reverified no-run target changes invalidate prior repair state and withhold publication of an obsolete queued warning. Delayed red can remain in the deduplicated exact observation history without activating an old incident. The aggregate retains prior failures while warning content distinguishes them from failures of the current attempt. New unresolved observations revoke previous nomination and recovery proof. Current green leaves the active incident for #279 recovery.

The private operator directory is durably bound to the store. Separate live and shadow filenames, atomic replacement, file and directory sync, content-digest readback, and serialized outbox acknowledgment preserve one stable warning for a given attempt through a rejected or lost acknowledgment. Nomination is manual and version-bound. The warning requests a manual pause and a single repair owner. [#278](https://github.com/kburson/aitm/issues/278) · [#103](https://github.com/kburson/aitm/issues/103)

The exact-head export passed **174 tests** across incident, advisory, policy and verifier suites in a locked CPython 3.13.9 environment. Ruff lint and formatting and exact-range Git whitespace checks passed. I reran the real directory shadow rehearsal and reproduced the saved JSON byte for byte. A simulated lost acknowledgment left one stable warning file. Reopen and retry confirmed the same contents and acknowledged its digest, a repeat delivered zero additional warnings and a newer incomplete attempt invalidated the old nomination while retaining historical failure. The saved shadow JSON SHA-256 is `5af53a0e23927dc28fc4fc7a136e859dbd06502783515176558b10e8d2e33477`; the saved warning SHA-256 is `7a8d01538658558dcf20cfaa21eca9809f585b1b02342af491452b4510c5daf3`.
