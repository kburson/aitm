# #292 Hosted fast-story shadow evidence

The deployment [PR #314](https://github.com/kburson/aitm/pull/314) passed the existing #103 verifier and independent review. The protected-default manual workflow used a read-only controller token. Each probe had its own signed admission on protected planning, bound to the exact open PR, base, head, tested GitHub merge, tested tree and review digest. The two candidate PRs are disposable evidence sources.

| Exact probe | Hosted decision | Evidence |
| --- | --- | --- |
| [Markdown addition #315](https://github.com/kburson/aitm/pull/315) | Selected. Trusted and tested collections matched all 1,825 ordered IDs. All seven mandatory tests passed all phases. Both required native children exited zero. | [Run 43721995748/1](https://github.com/kburson/aitm/actions/runs/43721995748/attempts/1) · [Verified receipt](selected/verified.json) · [Signed admission](selected/shadow-admission.json) |
| [Product source path #316](https://github.com/kburson/aitm/pull/316) | Full CI required. The bounded runner started no pytest collection or execution. | [Run 43722007566/1](https://github.com/kburson/aitm/actions/runs/43722007566/attempts/1) · [Verified receipt](fallback/verified.json) · [Signed admission](fallback/shadow-admission.json) |

The selected run recorded 9.62 seconds of pytest wall, 37 seconds from job start to completion, and 4 minutes 30 seconds from workflow registration to completion. This is one Markdown-only sample. Hosted resource queues, representative executable story changes and performance beyond 3,000 tests remain unqualified. The shadow cannot authorize delivery or merge. The initial key is pinned to the independent reviewer for this experiment. Reuse with another reviewer requires a reviewed key change. Protected executable isolation for arbitrary candidate code is outside this profile.

Both raw artifacts and logs remain available. The independent reviewer verified exact input identity, receipt custody, the complete selected verdict and the unqualified fallback. [Independent shadow review](shadow-evidence-review.md) · [Deployment review](formal-review.md) · [Off-host verifier](verify-hosted-shadow.py)

The temporary candidates closed without merging. Live verification then refused both historical receipts because the reviewed pull requests were closed. [Selected closure](selected/closed-probe.json) · [Fallback closure](fallback/closed-probe.json)
