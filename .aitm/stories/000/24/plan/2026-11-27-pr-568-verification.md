# #568 exact source qualification

- Base `0312853be12468a87fda933401f16a1368e76b2b`
- Head `ac95f99fa2292a29596a4a03c5913da2d3741b72`
- Synthetic merge `f22e45f4f23307403bfd51f100f5d8b1673c80d3`
- Tree `6b3115aaf878d0754bf48d839e855a02fffa1c61`

The focused tests first failed because the intake implementation was absent. The exact local candidate passed all nine focused cases. The real-Git scenario includes installed idea creation and listing, same-minute draft collisions, ambiguous handles, one-commit discard, attachment and tree receipts, tombstone name collisions, stable retry, graduation refusal and a competing remote attachment. Core Ruff lint and formatting and the tooling test passed. The initial local baseline had one C11 failure during a deleted-remote-ref scenario. C11 passed in isolation. The complete exact candidate passed all 932 Core tests locally and in hosted Core CI.

- [Hosted repository CI](https://github.com/kburson/aitm/actions/runs/46083979594/attempts/1) passed with 1,644 unit and 142 integration cases from 1,786 unique Linux cases.
- [Hosted Core CI](https://github.com/kburson/aitm/actions/runs/46083979589/attempts/1) passed with 858 unit and 74 integration cases from 932 unique Linux cases. All 932 Core product tests and one tooling test passed.
- Local macOS aitm-usage collection contained 1,642 unit and 138 integration cases from 1,780 unique cases. Both 92% unit floors remain unchanged.
- The [trusted verifier](2026-11-27-pr-568-verifier.json) confirmed the exact attested repository attempt and both line floors, 18,749/20,685 product statements and 1,060/1,133 helper statements.

#568 was marked ready after those gates passed. The same exact base, head and synthetic merge remained live at readiness. The independent source SAR is the next admission gate.

## Revised candidate

The first candidate was returned to draft after the author reproduced a copied `attachments/draft.md` being mistaken for the canonical document. A second reproduction showed stable retry from a fresh clone reported pending despite the exact receipt already being present on the validated shared ref. The revision restricts entity reads to canonical document depth, keeps retired paths reserved against stale handles, and verifies an already-delivered discard using its retained commit on the validated shared history. No runtime or implementation clock event was recorded.

- Base `0312853be12468a87fda933401f16a1368e76b2b`
- Revised head `460dc8209a245db013be0e9318cec6b8e103988f`
- Synthetic merge `8e00e2a7d16fb9144f554dd57b5cd2d88e88a075`
- Tree `bbc0ba51794afc1d885da75f84372ad4fb420338`

Repository run [46086115199](https://github.com/kburson/aitm/actions/runs/46086115199) and hosted Core run [46086115252](https://github.com/kburson/aitm/actions/runs/46086115252) apply to the revised draft. The earlier hosted and SAR evidence applies solely to the preceding tree.

## Candidate after independent round 1

[Independent Grok round 1](2026-11-27-pr-568-source-sar-r1.md) requested changes on the first candidate. The intermediate draft had already addressed nested attachments and document path reuse and added fresh-clone recovery. Before ready, that draft was superseded to cover the remaining findings. A real Git reproduction confirmed that the stale retained request after a lost CAS blocked a later retry. The revision gives each uncommitted discard attempt its own operation ID and uses the successful tombstone as the durable retry identity. The graduation scan checks the complete canonical stream. A verified retained discard takes precedence over any subsequent graduation record or reused handle.

- Base `0312853be12468a87fda933401f16a1368e76b2b`
- Head `bca68f1e5deac62995dc4f63fb012b17902b116c`
- Synthetic merge `6d56615769c1943849db88a4a8f085c8136cd108`
- Tree `a3c9d44841b21858811029130a864f678dea789c`

The revision remains draft while [repository CI](https://github.com/kburson/aitm/actions/runs/46086369089) and [Core CI](https://github.com/kburson/aitm/actions/runs/46086369032) qualify this exact candidate.

Both runs passed before #568 was marked ready again. Core collected 858 unit and 74 integration tests, all 932 passed, and its tooling test and Ruff passed. Hosted Linux aitm-usage collected 1,644 unit and 142 integration tests. The same 92% floors and coverage gates passed. All nine revised focused Core cases passed locally, including recovery from a lost CAS, a prior evidence event before graduation, retained receipt precedence with an inconsistent later graduation and changed-reason conflict. The [trusted verifier](2026-11-27-pr-568-bca68f1e-verifier.json) qualified the exact repository attempt and tree before the new SAR request.
