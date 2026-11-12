# #143 local replacement validation

- [PR #265](https://github.com/kburson/aitm/pull/265) · exact source `717da4ce2540d4ba52f340cd3fe276fc43ccfb5b` · tree `2f5169c7e1129f0cdb089b9d52ffe776de6af782` · base `0dfbcf0c4b346fe014674aae0775a82f40e3a9b8`.
- Python 3.13.9 and uv 0.10.6 with the lock enforced. All 12 [focused node IDs](143-replacement-focused-nodeids.txt) and 147 related TIA cases passed together, **159 passed in 122.49 seconds**. Ruff lint, format and Git whitespace passed.
- The replacement keeps native fixture data under the existing per-user cache hierarchy so activity under the system temporary directory cannot invalidate its ancestor ctime witness. The focused regression checks that the module allocates and removes its scratch directory there.
- [First local workspace diagnostic](native-run-r1-diagnostic.md) records the failed original candidate and controlled parent reproduction. The actual workspace replay and six hosted jobs are checked separately on this replacement.
