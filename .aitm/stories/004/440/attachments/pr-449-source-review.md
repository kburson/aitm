**Independent source review and exact-head verification PASS**

Base `6a87bd438ca4e26cbf2a6b6ea0f7eae43a3fb630`, head `1b0613b26c91fa7239887d79b085bf4701cb76c2`, tested tree `1822829abc06608b0a35532e9ab419703e84164a`.

Independent review reproduced and rechecked four controls. The revised adapter scopes harness metadata to the selected prompt, rejects two requests claiming one message or one request attached to two prompts, and refuses a cancelled result that contradicts a settled transcript. All 13 new tests are units and existing classifications were preserved.

All 88 focused tests passed on macOS and Linux. Claude Code 2.1.331 on macOS qualified fresh and resumed headless evidence, partial cancellation, and a configured Stop callback with exact delayed recovery. The cancelled case's counters were present in the live per-result evidence; retained recovery did not reproduce those counters. Verified receipt replay left story attribution unchanged.

The signed [hosted run](https://github.com/kburson/aitm/actions/runs/45615682494/attempts/1) passed all six jobs and the exact-tree trusted verifier. All 1,637 tests in the full product suite passed. Its 1,520 unit tests represent 92.85%, above the 90% gate.

Qualification is bounded to the recorded build and surfaces. #100 stays outside this change.
