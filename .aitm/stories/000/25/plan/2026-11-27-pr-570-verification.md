# #570 exact draft qualification

Base `fb23ebeb2b36f61e6c6bdfbc67ccc18df3d81359`, head `fff1d41e7a9445b6f807e988ad58f8e9a1197fe6`, synthetic merge `58c9ba4f07135dc283cadc27c5e56f5649fa97c0`, tree `624eb9c9b8c1f204d03db00039548f2912e753fb`.

The focused test initially failed because the source and identity authority contracts were absent. The exact draft passed 37 focused and affected tests. Disposable shared Git repositories and provider doubles exercise distinct operation IDs joining one semantic reservation, reentrant sender contention, lost acknowledgement, positive absence without a fence, supported retry with bound fencing proof, uncertain cancellation, and a frozen draft that changes after reserve. The provider contract tests preserve C13 compatibility.

The PR remains draft while [repository CI](https://github.com/kburson/aitm/actions/runs/46096942277) and [Core CI](https://github.com/kburson/aitm/actions/runs/46096942271) run against the exact candidate.

## Provider ownership revision

The initial draft passed both hosted workflows and its trusted verifier. It returned to draft before revision. A provider reply can name a same-issuer number that belongs to a different entity. The revision claims the issuer/number key and semantic issuance receipt in the same governed CAS, pins both paths for safe replay and refuses a foreign owner. This preserves C13 result types and the same test floors.

Base `fb23ebeb2b36f61e6c6bdfbc67ccc18df3d81359`, head `7b9c6e04db46a6ccf032ae10fccca3caffff892c`, synthetic merge `8bcd91b5f369ec2f99b2bc5fd0974246a1e6b157`, tree `a87e85f7a7688e4439f667511526d76326246292`.

Draft qualification uses [repository CI](https://github.com/kburson/aitm/actions/runs/46097368082) and [Core CI](https://github.com/kburson/aitm/actions/runs/46097368088).

The new foreign-issue regression failed on the previous source and passed on the revision. All 37 affected local cases passed. Both hosted workflows and trusted verification passed while draft on the revised exact candidate. #570 returned to independent review after these gates. [Exact trusted verifier](2026-11-27-pr-570-7b9c6e04-verifier.json)
