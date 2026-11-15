# #285 independent behavior and execution cost audit review

**Verdict: ACCEPTED for audit delivery.** Signed by OpenAI Codex, independent review agent `/root/review148`. No blocking findings. [#285](https://github.com/kburson/aitm/issues/285)

## Exact reviewed artifacts

- `2026-11-14-285-behavior-audit.md`, SHA-256 `c43dedceb8f25aa6ccc5e7ad5de30bed72956bbfde734f7b6dbbf2ca9f43b7e2`
- `audit-families.tsv`, SHA-256 `2798ea9c0863eacb9593021a9b9f19578e504a081004ef53f1df9f9b95b9dc40`
- `audit-inventory.json`, SHA-256 `ce2e0c22e3b7d1ed05a6663539a58c3613bfb07e43be5dcb2958b3df90f8e9d4`

## Independent verification

I collected all three profiles independently from a separate Git archive of protected `trunk` commit `a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2`. The exact 1,216 product/CLI, 196 required helper, and 525 all-helper node sets match the saved logs. The inventory reconciles to 1,740 unique IDs and 1,412 directly invoked by #103's product and helper lanes. All 42 family names map one-to-one to collected source modules, and all inventory counts and direct-gate memberships match. The 42 family source files in the audit archive match the independent Git export byte for byte. The supplied recipe regenerated the same inventory JSON.

I independently parsed the 15 hosted phase records and reconciled every node, phase and value with the inventory. Live GitHub matched the pinned protected trunk SHA and the successful canonical push run, exact attempt and Python job. The timings are a slowest-phase sample from one hosted run, with unknown durations for other IDs. The largest families in the inventory are monitor scope (149), monitor journal (136), Codex (115), PR verifier (91) and Claude (88). The behavioral triage covers every source family at module granularity. It leaves cases requiring finer comparison open for investigation and makes no 3,000-test performance claim. [Hosted timing source](https://github.com/kburson/aitm/actions/runs/43418827344/job/131863407499)

## Monitor journal recommendation

I read the parameterized refusal case and ran both exact swap nodes in the separate native fixture directory. Both passed. The owner/rival choice is unused in the swap mutation. Both branches construct the same owner/rival proof order, reverse the same list, and exercise the same settlement and refusal assertions. The six other failure branches use the selected side and remain distinct. The audit correctly defers deleting either swap ID because the current trusted-base comparison requires the base inventory and preserves its passing outcomes. [Current #103](https://github.com/kburson/aitm/issues/103)

The recommended #287 change retains the exact successful-settlement node and uses one stable post-settlement `JournalView` for three contiguous read-only assertions. I traced those reads through the read transaction and passed the existing exact node independently. The three assertions still cover the new settlement, unchanged disputes and preserved first claims. The earlier historical snapshot, both independent cursors, unchanged scope and hold state, persisted progress and later replay sequence check still require separate observations. Timing savings and before/after parity remain #287 evidence. [#287](https://github.com/kburson/aitm/issues/287)
