# #568 exact source qualification

- Base `0312853be12468a87fda933401f16a1368e76b2b`
- Head `ac95f99fa2292a29596a4a03c5913da2d3741b72`
- Synthetic merge `f22e45f4f23307403bfd51f100f5d8b1673c80d3`
- Tree `6b3115aaf878d0754bf48d839e855a02fffa1c61`

The focused tests first failed because the intake implementation was absent. The exact local candidate passed all nine focused cases. The real-Git scenario includes installed idea creation and listing, same-minute draft collisions, ambiguous handles, one-commit discard, attachment and tree receipts, tombstone name collisions, stable retry, graduation refusal and a competing remote attachment. Core Ruff lint and formatting and the tooling test passed. The initial local baseline had one C11 failure during a deleted-remote-ref scenario. C11 passed in isolation, and the complete hosted Core suite passed.

- [Hosted repository CI](https://github.com/kburson/aitm/actions/runs/46083979594/attempts/1) passed with 1,644 unit and 142 integration cases from 1,786 unique Linux cases.
- [Hosted Core CI](https://github.com/kburson/aitm/actions/runs/46083979589/attempts/1) passed with 858 unit and 74 integration cases from 932 unique Linux cases. All 932 Core product tests and one tooling test passed.
- Local macOS aitm-usage collection contained 1,642 unit and 138 integration cases from 1,780 unique cases. Both 92% unit floors remain unchanged.
- The [trusted verifier](2026-11-27-pr-568-verifier.json) confirmed the exact attested repository attempt and both line floors, 18,749/20,685 product statements and 1,060/1,133 helper statements.

#568 was marked ready after those gates passed. The same exact base, head and synthetic merge remained live at readiness. The independent source SAR is the next admission gate.
