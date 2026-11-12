# #143 local candidate validation

- [PR #265](https://github.com/kburson/aitm/pull/265) · source `e2c87eef770bd89a2ab68c7795a7d0a34398cfef` · tree `8b71d7263241fdeb8f4e057f4daa6b5b14d0ac82` · base `0dfbcf0c4b346fe014674aae0775a82f40e3a9b8`.
- Python 3.13.9 and uv 0.10.6 with the lock enforced. All 11 [focused node IDs](143-focused-nodeids.txt) and all 147 related TIA cases passed together, **158 passed in 115.93 seconds**.
- The Git fixture exercised the module entry point, selected and full execution, failure exit, drift, native capability refusal, copy integrity and required child outcomes. The nested-cache regression passed on the exact candidate. Ruff lint, Ruff format and Git whitespace passed.
- The actual Darwin APFS workspace replay and unchanged hosted six-job #103 workflow are tracked separately. The focused local command tests are outside the hosted helper list.
