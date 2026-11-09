<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-48ae3de9ffa0067249b56573a8a3b1c8"
role: "author"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_commit: "86ac9caf47c95d6443e329759ede387c2cfe37e6"
artifact_blob: "dfed3624be221f3f7358a00b065bbbc2a456cbc4"
artifact_digest: "sha256:3355a89fdfd38e16b9f4aeb37fc8fb368ea74ce8b7e608f0504b67a2e9288253"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  model_display: "gpt-6-astra"
  session_fingerprint: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
  identity_source: "runtime"
started_at: "2026-11-09T12:48:20.791Z"
submitted_at: "2026-11-09T13:07:06.039Z"
finding_ids: []
answered_finding_ids: ["R2-F001","R2-F002"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Addressed the two required gaps with a typed decomposition source route and inventory-driven migration. For the decomposition finding I used the existing own-document lifecycle rather than adding an inherited-design acceptance mode. The distinction is explicit below for reviewer evaluation, not silently claimed agreement. Round 2's actual retrieved content independently matched all 709 physical lines of its input blob in 12 Read results, with no gaps; the reviewer response used claude-opus-5-5. Author remains gpt-6-astra/xhigh.

## Finding dispositions

| Finding | Disposition | Resolution |
| --- | --- | --- |
| R2-F001 | accepted with an alternative coverage resolution | Added decompose as a plan-entry source into the existing identity protocol, with a typed accepted-plan descriptor, frozen design/plan/entry identities, stable key independent of revisions, one intent/child per key, retained conflict/reconciliation and no fabricated draft. Added decomposition estimate phase; Refine needs an explicit current Refine record. Explicitly specified own-document design coverage and refusal of missing/unsupported inherited coverage, with new acceptance cases. Parent source changes invalidate provenance applicability pending reconciliation and affected renewed acceptance. |
| R2-F002 | accepted | Inventory every observed v0 type/key/field at the pinned tip and classify mapping/opaque/blocker. Added mappings for both dependency event directions, plan-entry bootstrap graduation and estimate, non-runtime provenance, plan-origin/priority and legacy physical worktree paths. Full-corpus inventory plus representative fixtures must cover all required shapes, rather than only #1/#2. Existing raw sources survive unchanged. |

The alternative coverage resolution is deliberate. The existing core implementation plan's “Execution and evidence contract for every leaf” already says each leaf creates its own Design/Plan/JIT records and that parent decomposition is not leaf acceptance; every materialized leaf repeats that boundary. Architecture Backlog exit requires an accepted design. Thus there is an available verified-Done route through actual own-document evidence; the former design needed to state it clearly, not infer inherited acceptance. M1 now names that supported policy mode explicitly. I have not added an optional parent-plan-section acceptance implementation or selected an owner-open review-depth policy. A future request for inherited coverage gets an explicit unsupported result and needs its own design/policy decision. Please assess this bounded resolution against the actual owner and parent constraints rather than treating a proposed example mechanism as mandatory.

## Changes made

Defined plan-entry descriptors in the future v1 plan's semantic decomposition map, so canonical acceptance actually covers the child source and core never infers structured scope from arbitrary Markdown. Existing v0 bootstrap is mapped as historical provenance, not falsely upgraded to that future schema or native command. The initial estimate proposal and later Refine observation are distinct. Added inventory-driven migration and concrete legacy mappings, plus decomposition acceptance tests.

Optional 1 (line break): adopted as formatting clarity. The expansion paragraph is separated at a full sentence, while bounded physical line lengths preserve complete native Read output. Joining a paragraph into a >2,000-character line would risk silent retrieval truncation; hard wraps within a Markdown paragraph are intentional where necessary and remain part of this newly reviewed raw body.

Optional 2 (late oversized discovery): accepted. Stated the existing Plan/JIT→Backlog→Refine route before split, without adding a Plan→Refine edge or permitting post-attempt kind conversion.

## Declined changes and rationale

Declined the suggested addition of a supported parent-plan-section design-acceptance mode in M1. It is unnecessary for the already explicit own-design leaf route and would add new inheritance semantics beyond the accepted parent planning boundary. Missing/unsupported modes fail visibly; no policy is silently selected. The underlying finding's missing decomposition/estimate/coverage contract is addressed through the bounded alternative above, subject to the next review decision.

## Verification

Read the complete round-2 response and checked actual #1–#72 event inventory: it includes core.link.dependency-added and core.link.dependent-added, source plan keys, parent-plan-decomposition and top-level manual-bootstrap provenance. Verified complete round-2 fresh retrieval against its native input commit/digest. Checked revision whitespace, links, bounded physical lines and exact scope before native submit. No runtime implementation, synthetic historical event, production policy, tool repair or epic closure. The next round must freshly read the entire revised file from line 1 through EOF and assess all prior dispositions, including the explicit alternative resolution.
