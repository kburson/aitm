**Independent source review and exact-head verification PASS**

Base `2b257a4775551f2989613c39a5347fdd40f681ee`, head `cb695169af8a618c4bdbaf539cdabc3ed0513635`, tested tree `3eeeef7bae9ce65434b416cbb387b43d4ca1b1f5`.

Independent review reproduced and rechecked lifecycle and recovery issues. The fixes wake on output overflow even with inherited pipes, await bounded direct-child cleanup on cancellation, and explicitly preserve unknown descendant state. Exact recovery checks the bounded input across short reads and pins the original harness version. No remaining blockers in #438's shared interface.

All 34 focused tests passed on macOS and Linux. The 14 added fixtures comprise six units and eight systems integration tests. The signed [hosted run](https://github.com/kburson/aitm/actions/runs/45547058371/attempts/1) passed all six jobs and the exact-tree trusted verifier. The full product run passed all 1,583 tests. Its 1,467 units represent 92.67%, above 90%.

Provider-specific parsing and qualification remain in #439–#441. #100's monitor and cutover are outside this change.
