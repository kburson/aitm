---
schema: "aitm.review-response/v0"
story: 138
round: 1
level: "spr"
execution: "declared-manual"
input_commit: "15150b12f9cbb29867999b3a97faf4bc17c4d8b7"
inputs: {"plan": {"path": ".aitm/stories/001/138/plan/2026-11-10-138-pin-serial-baseline.md", "sha256": "869d24d514a2b1b6d32e91166baace48d1dc78e7a2fe992c79a316c03e1c5612", "lines": 251}, "jit": {"path": ".aitm/stories/001/138/plan/2026-11-10-138-jit.md", "sha256": "13a4aecb525c29d698df5a8f360e57689cb886ab1d46c4955b4db420302b94d8", "lines": 228}}
role: "reviewer"
role_session: "codex-collaboration:/root/plan140"
finding_ids: ["R1-F001"]
---

# #138 plan and JIT · Independent SPR round 1

Declared-manual Codex SPR by a reviewer distinct from the author. Candidate commit identity is `15150b12f9cbb29867999b3a97faf4bc17c4d8b7` from the candidate receipt. I used the isolated review checkout, read both artifacts from first line through EOF in numbered ranges, and independently compared raw byte hashes and physical line counts to the receipt.

| Candidate file | Raw SHA-256 | Physical lines | Numbered ranges read |
| --- | --- | ---: | --- |
| `.aitm/stories/001/138/plan/2026-11-10-138-pin-serial-baseline.md` | `869d24d514a2b1b6d32e91166baace48d1dc78e7a2fe992c79a316c03e1c5612` | 251 | 1–85, 86–168, 169–251 |
| `.aitm/stories/001/138/plan/2026-11-10-138-jit.md` | `13a4aecb525c29d698df5a8f360e57689cb886ab1d46c4955b4db420302b94d8` | 228 | 1–76, 77–152, 153–228 |

## Scope and verification

- The accepted own design and T01 hashes match the JIT. The two source paths and sanitized planning attachment match T01 ownership and are disjoint from #140. The offline projection preserves distinct candidate, base, push and advisory helper roles. The attempted worktree and branch remain intent, separate from authorization. The Planning stop and #139 hold for incomplete comparison are explicit.
- I independently matched all six retained ZIP hashes and checked member integrity. The signed and collector subjects are byte-identical. The subject hashes match the raw candidate inventory, source inventory and base receipt. The base identity agrees with the candidate's expected-base record and the retained policy bytes. The premerge verifier disposition and delivered tree agree with the #115 closure record. I used retained coordinator metadata for GitHub job/check and archive ownership and did not repeat the live provider reads or certificate verification.
- I verified the bytes of the protected #103 gate and policy against their pinned blob IDs and replayed in memory. The historical PR and push each passed with 630 product/CLI outcomes, product 7,146/7,825 and helpers 778/821. The historical PR also retained 592 trusted base outcomes. The current trunk push passed with 714 outcomes, product 8,404/9,229 and helpers 778/821. #116's closure record independently anchors the current trunk delivery tree. The two historical raw timing records match their respective warm timing buckets. Cold observations and finer unavailable measurements stay role-bound Unknown.
- I independently checked the retained observer's exit 0, 182 unique IDs, empty deselection/report/child records and sorted compact-array digest `69cef362f4c87ba65846443eda6a2c8ae3dca3431f76905dcefc459c1e7200a4`. That is local advisory collection. The JIT accurately separates the focused file from the four hosted helper test targets and the resolver from the four gated helper source paths.
- The existing exact-current #103 requirement, exact-tree owner disposition for the `tools/ci/` additions, independent source review and hold conditions carry through to delivery. The 2.5h estimate depends on ready verified inputs, a small projection using the existing verifier and gate, and no new cold experiment. The four-hour cap and identified custody, advisory and route invalidators give a practical replan boundary. A mid-slice check that the first complete synthetic proof projects and mixed-attempt input refuses would expose a projection overrun earlier.
- This is document review. I made no artifact or checkout changes and ran no product or candidate tests.

## Required findings

### R1-F001 — Establish red through the public projection

Plan lines 100–110 make the red run call a test-local stub that always returns canonical output, then replace that callable when the real module is wired. That red proves the assertion fails on the fixture stub. It does not show the #138 entry point missing the behavior, because the entry point under test changes before green. T01 and the accepted leaf design require the named regression to fail first and to support the red/green delivery record.

Write the test against `tia.baseline.build_baseline` from the start, using a minimal importable scaffold in the owned module that lacks the mixed-attempt check. Keep the test, target and mixed-attempt fixture stable across red and green. Require the red to reach the same behavior assertion on that entry point, with the missing refusal visible, and retain that result.

## Decision

revisions-requested
