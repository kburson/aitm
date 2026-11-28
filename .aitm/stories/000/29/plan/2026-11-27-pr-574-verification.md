# #574 exact source qualification

Base `a213708a05ab734a60e1f010807d93f0ba1d363f`, head `060f58e3562ea514cf0cf4b2ac0e9742a961f34a`, synthetic merge `61d0e37b444e544721a8e64717d6aa3b13473cab`, tree `4c5a8524e9f870824bc9da05c925d5562642505b`. Repository CI and separate hosted Core CI passed while #574 was draft. The Core job authenticated both ordered parents and the tree and ran the full product suite, tooling check, and Ruff. The trusted verifier observed the exact hosted repository attempt from the clean base. Product line coverage was 18,749/20,685. Helper line coverage was 1,060/1,133. [Repository CI](https://github.com/kburson/aitm/actions/runs/46103679309/attempts/1) · [Core CI](https://github.com/kburson/aitm/actions/runs/46103679293/attempts/1).

- aitm-core: 940 unit, 80 integration, 1020 total. Exact integration ratio 80/1020. 8000 < 8160.
- aitm-usage: 1644 unit, 142 integration, 1786 total. Exact integration ratio 142/1786. 14200 < 14288.

Both existing 92% unit floors passed. The strict integration limit was computed on unrounded, unique full collections. One new integration case proves the real Git apply contract for a repository-relative base creation and edit, CRLF content, a missing final newline, an empty acknowledgement, original byte retention, and isolation from inherited Git environment. The new unit cases prove schema and identity refusal, byte chain checking, input inventory and file type checks, and single-file patch framing. No existing integration case changed category or was removed.

Local verification passed all 32 focused tests, the separate tooling check, Ruff lint and formatting, and compatibility replay of all 44 archived portable bundles (17 SAR, 16 SPR, 11 XPR). Ten native-only archive layouts are retained for the C58 adapter.

The PR was marked ready at `2026-11-28T03:41:19Z`. [Round 1](2026-11-27-pr-574-source-sar-r1.md) raised a finding. A direct reproduction and the exact Git integration case contradicted the finding, and independent round 2 passed on the same candidate. The verifier ran again with the reviewed tree. The branch required a clean merge state and seven successful hosted checks at admission. [Before readiness](2026-11-27-pr-574-verifier.json) · [Before merge](2026-11-27-pr-574-premerge-verifier.json) · [Independent SAR](2026-11-27-pr-574-source-sar.md).
