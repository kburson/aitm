# #339 Paired exact PR feedback qualification

The explicit Grok fixture preflight reached the trusted full verdict **4m 52s sooner** in one protected, matched GitHub PR pair. The local module caught the same behavior failure as hosted CI and the treatment needed one fewer hosted candidate. Both corrected attempts exercised the ordinary full gate and verified the identical source tree. [Qualification plan](2026-11-16-339-exact-pr-feedback-plan.md) · [Recorded preflight recovery](2026-11-16-339-preflight-recovery.md)

| Elapsed interval | Hosted-first control | Fixture preflight | Reduction |
| --- | ---: | ---: | ---: |
| Initial edit start to live trusted full verdict | 14m 09s | 9m 17s | 4m 52s |
| Initial edit start to exact signed completion | 13m 46s | 8m 57s | 4m 49s |
| First canonical provider registration to exact signed completion | 13m 40s | 7m 25s | 6m 15s |
| First canonical provider registration to live trusted verdict | 14m 03s | 7m 44s | 6m 18s |
| Corrected publication start to live trusted verdict | 8m 21s | 7m 49s | 31s |
| Corrected candidate registration to live trusted verdict | 8m 15s | 7m 44s | 30s |

The first control registration belongs to the real failing candidate. The treatment's first registration belongs to the corrected candidate. Its edit clock includes the initial TIA refusal, diagnosis, both fixed-module checks and the wait for full canonical evidence. The corrected-publication and final-registration rows isolate time on the repaired candidate. The signed endpoint is the later of the provider's signed artifact timestamp and successful signer completion. Hosted queue, job, artifact and verification times are preserved separately in the machine readout.

## Matched failure and repair

Both initial candidates used tree `a2edad694d88f60013206fafa5c03ae81d0d4e45`. Both corrected candidates used tree `e170e6bee0260f65bdd5211125ca25e0c8ccd915` on base `755fa2ece56cfa8c70a460b269d947ec6e958b2f`. The sole tracked difference from base was the Grok headless test fixture. The two-row refresh reversed the row order. The initial edit also changed the first request's input token count from 12789 to 12790, making the declared counts inconsistent. The correction restored 12789 and kept the row refresh.

The existing `test_headless_projection_is_only_corroboration` required two observations without diagnostics. The same assertion reported zero observations in the bounded local run and the hosted control. The hosted Python job reached terminal failure 5m 22s after edit start. The trusted verifier refused the unsuccessful canonical attempt, and its signer was skipped. The local module reported red 1m 26s after edit start and passed all 33 collected tests after repair. The correction was published only after that local pass.

The stock #143 TIA command refused to run because the current suite policy leaves 12 collected product modules, totaling 250 test IDs, unclassified. An amendment recorded before local fallback or the hosted red outcome pinned the existing `grok-headless-fixture` dependency edge, the unchanged complete `test_grok.py` module, the locked Python 3.13.9 environment and the canonical observer. This result qualifies that explicit fixture preflight. General TIA selection remains unqualified at this production base.

## Full hosted evidence

| Candidate | Canonical attempt | Exact tree verification |
| --- | --- | --- |
| [Control initial](https://github.com/kburson/aitm-feedback-339/pull/1) | [43815750781/1](https://github.com/kburson/aitm-feedback-339/actions/runs/43815750781/attempts/1) | Hold. Python and collector failed. Signer skipped. |
| [Control corrected](https://github.com/kburson/aitm-feedback-339/pull/1) | [43816407550/1](https://github.com/kburson/aitm-feedback-339/actions/runs/43816407550/attempts/1) | Pass. All six required Actions checks passed. |
| [Treatment corrected](https://github.com/kburson/aitm-feedback-339/pull/2) | [43815909956/1](https://github.com/kburson/aitm-feedback-339/actions/runs/43815909956/attempts/1) | Pass. All six required Actions checks passed. |

Both full endpoints retained the same 1,517 candidate and 1,516 trusted-base node IDs and matching per-test phase outcomes, with zero deselections. Both helper invocations passed 196 tests. Product coverage was 14,487/15,925 (90.97%) on control and 14,487/15,925 (90.97%) on treatment. Helper coverage was 806/849 (94.94%) and 806/849 (94.94%), respectively. The signed collector and wheel smoke receipts matched their own exact provider identities. Offline Sigstore replay authenticated each signed subject and its distinct PR, attempt and synthetic commit.

The unchanged verifier treats tracked fixtures as controls. The independent narrow disposition binds the identical corrected tree for the lab verifier only. The treatment's verification without that disposition held and was preserved. The first successful authorized check defines each endpoint. The control's immediate post-push PR API readback lagged. The corrected push already registered successfully, and the control clock continued through read-only recovery without another push or restart.

## Scope

The measured gain comes from avoiding one hosted run of the deliberately failing edit. The paired test uses one fixture edge, known correction and disposable protected repository. It supplies no fleet latency percentile, no 3,000-test forecast and no evidence for preventing unrelated cancellations or GitHub synthetic merge refreshes. The eight observed production PRs in #337 still give the historical baseline of 22m 01s p50 and 45m 55s p95 from first registration through exact signed evidence. [#337 production readout](https://github.com/kburson/aitm/blob/c34a9a9fba8406bf40115edfd7c7f939b6b2529d/.aitm/stories/003/337/plan/production-readout.md)

Production #103's issue, canonical source and state, verifier, policy and effective trunk rules matched the pre-experiment readbacks. The lab's protected base remained frozen and both lab PRs stayed open through evidence capture. No PR was merged. [Evidence archive](exact-pr-feedback-evidence.zip) · [Machine readout](qualification-summary.json) · [Reproduction](reproduction.md)
