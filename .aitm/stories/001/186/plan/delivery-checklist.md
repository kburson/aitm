# #186 delivery checklist

Attempt 1. Implementer and closure owner: Codex, acting for the owner. No predecessor. Source branch `codex/aitm-186-planning-evidence` targets `trunk`.

- [x] [Exact design, plan and JIT](jit.md) and [independent acceptance](jit-review.md).
- [x] [PR #196](https://github.com/kburson/aitm/pull/196) opened against base `a495d60a87ac4ca764f019dc266e579f13f1787e`. GitHub readback matches clean head `1e51b9895714fb302608a6e9680bd37589ce9355` and local tree `79a6d0f472d15421b09089eadf9fd13047044197`. The three-path diff is confined to `tools/story_dashboard/`.
- [x] Exact candidate: 7 dashboard unittest cases on CPython 3.13.9, Ruff and file checks passed. The guide example passed prospective validation, atomic publication and replay in a disposable Git fixture. Planning read `caab6f754f877c8c1b3d135e0acee0a48d775640` at `2026-11-10T22:02:49Z` retained 178 stories, 2,123 eligible events and the exact #181 seed. Two older draft events have no story ID and are held with explicit gaps. The unchanged package baseline passed 747 tests.
- [ ] [Current hosted run](https://github.com/kburson/aitm/actions/runs/42914804492), delivered verifier and independent source review.
- [ ] Normal merge, verified landing, retrospective, sign-off and issue/Project closure.

## Author correction during Test

An added regression exposed an identical legacy-registration retry being held as a second seed. The author reproduced the failure, corrected exact retries to deduplicate, and is replacing the candidate. The original run remains evidence only for its original SHA. Conflicting legacy claims remain held.

The original [hosted run](https://github.com/kburson/aitm/actions/runs/42911485968/attempts/1) passed and is superseded. The same PR now has clean head `41361c78a6fdbfe6ad1e08168c9f13c94d390787` and tree `083f30d03da84aad4545e42bb71428e0fc9bed49` on the unchanged base. All seven focused tests, including the retry regression, Ruff, file checks, the guide fixture and pinned planning read passed on the replacement.

## Failed hosted attempt and trunk advance

[Revision 2 attempt 1](https://github.com/kburson/aitm/actions/runs/42912258750/attempts/1) on head `41361c78a6fdbfe6ad1e08168c9f13c94d390787` passed base, quality, and file checks. The existing usage-monitor behavior test `test_cloned_scope_proof_and_changed_authorized_bytes_are_refused` failed while establishing the fixture's native scope proof with “Verified native scope source changed.” The collector consequently failed and the signature job was skipped. No monitor, workflow or CI helper paths were modified in #186. The earlier revision passed the same unchanged package suite. The detailed cause inside the hosted native fixture was not established.

[PR #195](https://github.com/kburson/aitm/pull/195) landed unrelated monitor paths at trunk `49865245d175ce6c52913738f2c9a42c0abea632`. Return to Develop to integrate the new trunk base into the isolated #186 branch and repeat exact candidate checks. Keep the accepted #186 paths and scope. The failed hosted attempt remains in the record.

Revision 3 matches the [PR readback](https://github.com/kburson/aitm/pull/196): clean head `ad8aece4e05e3446063b1568d60549cb97302cbe`, base `49865245d175ce6c52913738f2c9a42c0abea632`, tree `23856755bd01534855842ecee675964c1eece94c`. The three story paths are byte-identical to revision 2 and are the only diff relative to trunk. All seven dashboard tests, Ruff, tracked file checks, disposable capture round trip and the exact #181 seed read passed on revision 3. The monitor test that failed on the previous hosted runner passed when reproduced locally on revision 3. No monitor files were edited for #186.

## Exact-candidate hosted rerun

[Revision 3 attempt 1](https://github.com/kburson/aitm/actions/runs/42913081303/attempts/1) passed base, quality, and file checks. The unchanged usage-monitor test `test_claude_startup_prefix_requires_the_entire_proven_native_chain[foreign]` failed when its fixture discovery returned no candidate; 866 other product cases passed. Evidence collection failed and the signature job was skipped. The exact named test passed in a focused local run on the same revision. Both reported hosted failures were in existing monitor fixtures, with different failure sites; the underlying runner condition is unconfirmed. No CI controls or monitor source changes are in the PR.

[Attempt 2](https://github.com/kburson/aitm/actions/runs/42913081303/attempts/2) reruns **all** jobs on the same head, base and tree. No reuse of passing jobs or artifacts from attempt 1.

All six hosted jobs passed on attempt 2, including the signature job, but the delivered verifier held the evidence with “selected attempt identity or outcome disagrees.” The canonical workflow listing records run `42913081303` creation at `2026-11-10T22:16:55Z`; the exact attempt endpoint records creation at `2026-11-10T22:21:24Z`. The other checked candidate associations and outcomes agree. The verifier requires the two creation timestamps to equal, so a new PR event with its own run and first attempt is required. The next candidate changes commit metadata only and preserves the source tree. Keep the verifier unchanged.

## Fresh PR event

Revision 4 is head `0814a81bc93a829c8130a2a9152120b29907deeb` on the same base `49865245d175ce6c52913738f2c9a42c0abea632` and identical tree `23856755bd01534855842ecee675964c1eece94c`. The empty commit triggers its own [canonical hosted run](https://github.com/kburson/aitm/actions/runs/42914804492) with a fresh first attempt. The PR and local readbacks agree. All seven dashboard tests, Ruff and the guide round trip passed again on revision 4.
