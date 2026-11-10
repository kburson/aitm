# #186 delivery checklist

Attempt 1. Implementer and closure owner: Codex, acting for the owner. No predecessor. Source branch `codex/aitm-186-planning-evidence` targets `trunk`.

- [x] [Exact design, plan and JIT](jit.md) and [independent acceptance](jit-review.md).
- [x] [PR #196](https://github.com/kburson/aitm/pull/196) opened against base `a495d60a87ac4ca764f019dc266e579f13f1787e`. GitHub readback matches clean head `1e51b9895714fb302608a6e9680bd37589ce9355` and local tree `79a6d0f472d15421b09089eadf9fd13047044197`. The three-path diff is confined to `tools/story_dashboard/`.
- [x] Exact candidate: 7 dashboard unittest cases on CPython 3.13.9, Ruff and file checks passed. The guide example passed prospective validation, atomic publication and replay in a disposable Git fixture. Planning read `caab6f754f877c8c1b3d135e0acee0a48d775640` at `2026-11-10T22:02:49Z` retained 178 stories, 2,123 eligible events and the exact #181 seed. Two older draft events have no story ID and are held with explicit gaps. The unchanged package baseline passed 747 tests.
- [ ] [Current hosted run](https://github.com/kburson/aitm/actions/runs/42912258750), delivered verifier and independent source review.
- [ ] Normal merge, verified landing, retrospective, sign-off and issue/Project closure.

## Author correction during Test

An added regression exposed an identical legacy-registration retry being held as a second seed. The author reproduced the failure, corrected exact retries to deduplicate, and is replacing the candidate. The original run remains evidence only for its original SHA. Conflicting legacy claims remain held.

The original [hosted run](https://github.com/kburson/aitm/actions/runs/42911485968/attempts/1) passed and is superseded. The same PR now has clean head `41361c78a6fdbfe6ad1e08168c9f13c94d390787` and tree `083f30d03da84aad4545e42bb71428e0fc9bed49` on the unchanged base. All seven focused tests, including the retry regression, Ruff, file checks, the guide fixture and pinned planning read passed on the replacement.
