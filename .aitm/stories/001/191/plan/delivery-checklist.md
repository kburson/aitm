# #191 delivery checklist

Attempt 1. Implementer is the assigned Codex agent. Closure owner is the coordinating Codex agent. Target trunk. Pickup base `5cc77ab5f66e98d9d2777d7816f662e71a8804e9`. Predecessors #190 are delivered. File ownership is defined by the exact pickup.

- [x] [Design, Plan and JIT](jit.md) and [independent acceptance](jit-review.md).
- [ ] Local verification, applicable hosted CI and independent source acceptance.
- [ ] Verified merge, implementing-agent sign-off, and issue/Project closure.

## Candidate 1

[Source PR #220](https://github.com/kburson/aitm/pull/220) targets trunk base `5cc77ab5f66e98d9d2777d7816f662e71a8804e9`. Exact head `49bd8aa83b9470718133e4f73401f0c905b99a5d` and tree `d18b7601487260506bdb4bf33cc7beb85d8f0ac5` contain only the reviewed story paths. Focused dashboard tests, the full dashboard suite, Ruff, and whitespace checks passed on the clean checkout.

- [ ] [Hosted CI](https://github.com/kburson/aitm/actions/runs/42961437891), delivered verifier and independent source review.

## Live capture and board readback

The published pilot at planning `527dce9bd7847181a67dc23c6bb2c9844f15c87f` registered exactly one immutable #191 receipt. [Exact receipt](https://github.com/kburson/aitm/blob/527dce9bd7847181a67dc23c6bb2c9844f15c87f/.aitm/stories/001/191/attachments/timing/live-pilot-a06-191.json) SHA-256 `8d3bf226f4e47fac1153dad67b4ecae5fdbabb24ccbc73ebaf8ed9ae7d13076c`. Its exact replay was a no-op at the same planning commit. The recorded turn and its nested tool run are separately bounded in the receipt. The safe checkpoint source binds the switch to #192. #192 work stayed outside #191. An explicit owner request was observed and its response was not available at pilot publication. The pilot retains the missing-response gap and Owner wait Unknown.

The baseline at planning `a23893955d7cedb68aabf3b216553b83c48472f2` and UTC cutoff `2026-11-11T04:43:31.905Z` has Unknown Actual and snapshot digest `72888c5ffdc7cc6e00ee2b8da6d006d6de73b59cb3e8a3738d7e71181ee21478`. A separate clean reader rebuilt the later pin at `2026-11-11T04:45:27Z`, snapshot digest `94a2c286b3de1bce4e49eb38cc1b35128ce470de83c644e65f843809a33f6fe9` and validation digest `80a1adbe65515b073b01aa49bf02c5e2982b93a8af32f75527fdff724afa7803`. The later snapshot shows one #191 contribution of 4891 ms. The nested 3896 ms tool interval is counted once inside that value. Actual coverage is Partial through `2026-11-11T04:43:35.855Z`. Calibration is ineligible. Cost is Unknown.

[AITM-PY board](https://github.com/users/kburson/projects/24) readback at the verified item for #191, using the bound later snapshot. The first interruption stopped after the interim marker, and the second after writing Actual. Each resume rechecked issue identity, scoped planning inputs, the exact snapshot and validation binding, and all three field values.

| Readback | Actual | Actual coverage | Cost |
| --- | --- | --- | --- |
| Original | Blank | Blank | Blank |
| First interruption and resume | Blank | Pending verification | Blank |
| Second interruption and resume | 0.0014 h | Pending verification | Blank |
| Final and independent readback | 0.0014 h | Partial. Verified #191 pilot through 2026-11-11T04:43:35.855000Z. | Blank |
