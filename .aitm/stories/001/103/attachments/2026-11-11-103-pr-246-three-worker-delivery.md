# #103 three-worker Python CI delivery through PR #246

## Validation and independent review

The owner directed delivery of #246 before #244, with both Python jobs capped at eight minutes. The refresh integrated the dashboard changes already on trunk. The six-file PR diff was byte-identical to the earlier candidate. The owner's merge instruction supplies the disposition for the workflow, dependency pins and observer changes in that diff. The independent review below binds that scope to the refreshed tree.

- Target `trunk` at `8a17077c3dbabcce3e4682c42d8cd856d5d99f3d`
- PR head `42fd76ce4e880ed7b6275059e7755b54263a8eec`
- GitHub test merge `09fa62c2cf889779c06942ce333d5da4c0e29945`
- Tested tree `3a1554252c19e7065b6a717cccc7ad5caaca185a`
- All six jobs passed. The candidate Python job took 177 seconds and the serial base job took 254 seconds. [PR run 43124351778, attempt 1](https://github.com/kburson/aitm/actions/runs/43124351778/attempts/1)
- Trunk's verifier authenticated signed artifact `13902865941` and subject SHA-256 `eb963bc52dd252b7f26f50235a08460f438f3d7e97f8d9e820d7585d726e73d0`.
- An independent Codex reviewer passed the exact candidate on 2026-11-11 Central time with zero actionable findings. The reviewer checked the diff and reran signature verification. Independent comparison of the retained serial and hosted parallel archives matched all 1,071 product and CLI test IDs, 3,213 phase outcomes, exact line and branch coverage and both PID-linked subprocess proofs. All 190 helper tests passed. The review was conducted off-platform.

## Verified delivery

The trusted verifier passed again immediately before the expected-head GitHub merge. Trunk received merge commit `91e96bd9e3ae3bc907af3ed457ac1b4df424f542` with the ordered parents and tree listed above. The merge completed at 00:11:34 UTC on November 12, 2026. [Merged PR #246](https://github.com/kburson/aitm/pull/246)

The trunk push passed all four applicable jobs. The three-worker Python job took 243 seconds and ran all 1,071 product and CLI tests and 190 CI helper tests. The retained artifact matched the serial test inventory, phase outcomes, line and branch coverage, and both PID-linked child proofs. Its wheel digest matched the PR run. [Trunk push run 43125473626](https://github.com/kburson/aitm/actions/runs/43125473626)
