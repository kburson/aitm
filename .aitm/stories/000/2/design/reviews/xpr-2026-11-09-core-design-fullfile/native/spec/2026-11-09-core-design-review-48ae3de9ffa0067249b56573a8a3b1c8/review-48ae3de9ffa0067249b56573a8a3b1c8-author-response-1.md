<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-48ae3de9ffa0067249b56573a8a3b1c8"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_commit: "bcacb1378ca2cf268bb194cdf80f4fe21f155b2d"
artifact_blob: "767b7bbf82da157494fc94feb5ebf3092c97ed55"
artifact_digest: "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  model_display: "gpt-6-astra"
  session_fingerprint: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
  identity_source: "runtime"
started_at: "2026-11-09T12:48:20.791Z"
submitted_at: "2026-11-09T12:58:15.789Z"
finding_ids: []
answered_finding_ids: ["R1-F001","R1-F002","R1-F003"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Addressed all three sealed required findings and all five separately numbered optional suggestions. These are bounded M1 builder calls filling existing lifecycle, independent-review and record contracts; no open owner policy was selected. The author is gpt-6-astra/xhigh (observed current Codex turn context). Round 1's actual Read tool results were independently compared with the input Git blob before revision: all 657 physical lines matched, no gaps or mismatches. Claude reports 658 split elements because the file ends with a newline; that is not a missing authored line.

## Finding dispositions

| Finding | Disposition | Rationale and revision |
| --- | --- | --- |
| R1-F001 | accepted | Graduation now records explicit resolved kind. A bounded pre-Develop Refine split converts the same ID to a Backlog epic, invalidates leaf applicability while retaining history, and requires new aggregate design/estimate and a nonempty accepted child set. Children use the existing safe graduation/link route; no distributed all-at-once creation is invented. Common Backlog/Refine/Ready guards are explicit for every kind, with the four-hour ceiling on leaf kinds only. v0 kind migration and acceptance cases are defined. |
| R1-F002 | accepted | Defined aitm.source-review/v1, its core adapter, immutable response/source/attempt/generation and participant proof, finding closure and committed source-review policy. Independent means distinct from the retained implementing-session set, with optional stronger provider separation. Declared assurance remains declared; self-review, unknown comparison and stale/missing proof cannot activate. Added negative and conforming activation evidence. |
| R1-F003 | accepted | Added explicit pivot and reconfiguration acceptance rows, retaining actor-authentication limits and provider-neutral scope. The discarded-draft suggestion is covered with the entity-editing/discard proof. |

Optional suggestions are not additional sealed finding IDs; all receive dispositions here rather than inflating the protocol count:

1. Expand inputs/state — accepted. Explicit kind, frozen draft handle and reason; initialized Backlog child follows ordinary design/estimate/plan/JIT gates, origin pause remains continuous.
2. Review-open fact — accepted. Added core.doc-review.opened with the stable level ID/input identity; completion uses the real open as its outer start, with Unknown/provenance retained for legacy records lacking it.
3. YAML scalar typing — accepted. Specified a versioned JSON-scalar resolver and cross-language vectors instead of selecting a parser's defaults. Semantic fields reject incompatible scalar types, including YAML-only numeric forms.
4. Draft/idea save route — accepted. Entity-scoped open, sync and unbind reuse containment/base/binding protections and preserve unsynced data through graduation/discard.
5. Review-policy example — accepted. Added an explicitly labeled test fixture including separate document/source rules and disabled exceptions. It is not a product default, nor owner confirmation of document depth or sequence policy.

## Changes made

Revised the FUR's configuration example, event table, binding/editing, kind/split lifecycle, planning guards, canonical header typing, source-review evidence, live review opening, expansion input, CLI, migration and acceptance sections. Updated only this revision's generated header fields before renewed review. Architecture and owner decisions remain unchanged. The implementation plan is deliberately unchanged in this design cycle and must be reconciled with these accepted contracts in its separately authorized full-file validation.

## Declined changes and rationale

None. No unresolved required finding is deferred. General-purpose or post-Develop kind mutation was not added: the minimal split path satisfies the Refine decomposition requirement while preserving identity, attempt and expansion invariants. New permanent child identities still use the established recoverable provider protocol.

## Verification

Checked every disposition against the complete submitted response, parent architecture, owner decision record and current design. Verified fresh round-1 retrieval using actual numbered tool-result content, not just Read requests. Checked exact changed-file scope and Markdown whitespace, kind/CLI/event/acceptance cross-references and preservation of the existing open decisions. This is document revision; no product code/tests, implementation, global settings, trunk changes or issue closure. Next reviewer must freshly reread the complete revised FUR from line 1 through EOF, including all new contracts, and verify these dispositions; prior-round context is insufficient.
