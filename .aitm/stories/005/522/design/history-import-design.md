# M7 design draft — Validated history import

Issue [#522](https://github.com/kburson/aitm/issues/522) · Parent #1

## Goal and boundary

Import a reusable legacy AITM corpus with reproducible provenance for estimation and planning research. M7 owns source inventory, evidence normalization, repeatable import, and a validation report. It consumes Core’s released story, estimate, outcome, and v0 read/validation contracts. M7 owns the legacy source adapter and the separate corpus export envelope. This dependency supplies schemas and a qualified read/validation path. M7 exercises that path on disposable fixtures and does not require production cutover or native state writes. The importer runs with the rubric absent. Historical closure is retained as source data, with imported stories distinguishable from native workflow records.

M7 waits for [Core release #72](https://github.com/kburson/aitm/issues/72), including the versioned Core story/estimate/outcome schema, source identities and v0 reader or adapter contracts, and qualified read-only source access from [#525](https://github.com/kburson/aitm/issues/525), a child of M2 [#524](https://github.com/kburson/aitm/issues/524). The handoff must include a versioned installable adapter, scoped authenticated readback against the legacy repository, and a sanitized capability receipt. The M7 intake verifies that proof independently of the rest of M2. M7 supplies the validated corpus required by [#523](https://github.com/kburson/aitm/issues/523).

## Source inventory and extraction

- Inventory the legacy repository and publish the exact source pin, cutoff, issue count, supported sources, and known gaps. Enumerate all intended issues and source sections with explicit pagination and stable identities. The historical count around 2,165 is a planning hint.
- Capture issue bodies, reviewed phase estimates, Timing Log comments, and supported commit or approval evidence. Bind each item to the exact source issue, revision and content digest, capture cutoff, parser version and schema version. Raw evidence storage requires an authorized retention boundary.
- Use read-only source access and bounded retries. Audit paging completeness and distinguish unavailable content from empty content. Incomplete enumeration or fetch blocks promotion unless the narrower scope is explicitly approved and recorded. Fully enumerated records with missing or unqualified historical evidence can be published with explicit dispositions.
- Normalize from pinned inputs. Identity keys bind source repository, original issue, evidence kind, and revision. Identical imports reconcile to one record. Differing evidence for the same identity requires explicit resolution or an append-only correction.

## Corpus contract

The draft uses a separately versioned corpus export with a manifest and records. A derived local index can be rebuilt from the export. This gives M8 a stable input without introducing imported states into Core’s transition history. Before adoption, decide whether an approved archive, an owned planning namespace, or a separate Git repository carries the export. Keep bulk raw logs and excluded sensitive material outside the default publishable view.

| Record | Minimum contents |
| --- | --- |
| Corpus manifest | Source repository, source pin and cutoff, schema and adapter revisions, file digests, counts by disposition, exception and hold counts, and validation proof pointer. |
| Story history | Stable external issue ID, permitted title and scope fields, issue and evidence references, imported status, and identifiable Refine, Plan and Close evidence or documented legacy equivalents when substantiated. Retain the estimate revision and time, closing outcome, and attempt and phase bindings. Mark any missing link explicitly. |
| Measurement evidence | Units, role/actor scope, attempt, phase, basis, provenance, verified boundaries, and complete, partial, unknown, or disputed qualification. |
| Validation disposition | Accepted bytes, quarantined or ambiguous records, replay outcomes, fixture and source references, reason codes, and eligibility signals. |

Preserve missing Actual as missing. Corrupt timing, overlapping intervals with unproved actor attribution, and unproved estimate chronology stay visible without creating numeric labels. Quarantine unknown units and conflicting identities. The consumer decides whether a complete record qualifies for a specific training objective.

## Import and recovery

1. Build a preview from pinned inputs. Show counts, expected changes, rejected records, and manifest digest.
2. Independently verify representative fixtures and source references. Match exact hashes and counts on repeated extraction and fresh checkout. Include missing pages, edited sources, duplicates, invalid Timing Logs, and refused access.
3. Publish the validated manifest and permitted corpus via the approved archive or owner-scoped writer. Verify the exact result before replaying an interrupted publication.
4. Ship a versioned reader contract and validation receipt consumable by [#523](https://github.com/kburson/aitm/issues/523). Corpus validation can pass while quarantined or incomplete rows remain visible. Training sufficiency is an M8 decision.

## Acceptance, decomposition and decisions

- A second reader reproduces import identity, counts, digests, and dispositions from the manifest and permitted evidence.
- Verify missing evidence, unsupported timestamps, conflicts, retries, and corrections. Exercise a complete pair if supported and prove unqualified rows stay excluded from eligibility.
- Qualify the scoped M2 source handoff and manifest readback independently of M8.
- Refine into four to six bounded children for source access and inventory, schema and fixtures, normalization and validation, replay and promotion, and publication. Keep each implementation child within four agent-hours.
- Resolve the storage and publication route, allowed legacy evidence fields, exact [#525](https://github.com/kburson/aitm/issues/525) source-access proof, trusted Timing Log formats, and exception policy before implementation pickup.

## Handoff receipts

Consume the exact [M2 #525 source handoff](../524/design/github-extension-design.md#delivery-handoff-and-sequencing). Pin the read capability and schema, compatible wheel version/digest/source revision, authorized canonical source, scope and cutoff, fixture revision, and sanitized live qualification receipt. Validate that its allowed evidence and acquisition semantics cover the requested corpus. Refuse an incompatible or insufficient handoff with a specific missing-capability result. Full M2 completion has no role in this check.

Publish a sealed corpus transition to [M8 #523](../523/design/rubric-design.md#validated-history-handoff). The delivery consists of the manifest and schema revision, immutable manifest location and digest, exact source and cutoff, record digests, counts by qualification/disposition, recorded scope exceptions and held rows, and the validation receipt and read fixture. The receipt must show independent replay and preserve estimate, phase, completed attempt/outcome and Actual lineage where substantiated. M7 validates provenance and reproducibility. M8 decides comparability and corpus sufficiency.

## Refinement estimate and rank

**Rank 260 · Feature · 18.5 implementation agent-hours.** Scope is one independently consumable corpus capability. It excludes the #525 adapter and M8 model work. Estimates include verification and review.

| Work | Agent-hours |
| --- | ---: |
| Pinned intake and bounded source inventory | 3.5 |
| Corpus schema, qualification dispositions and fixtures | 4 |
| Legacy field and evidence normalization | 4 |
| Replay, corrections and refusal behavior | 3.5 |
| Sealed export, validation and consumer handoff | 3.5 |
| **Total** | **18.5** |

This is a five-child-sized initial decomposition. Actual story definitions and JIT estimates require separate refinement. Native prerequisites are #72 and #525. Rank expresses the proposed sequence and adds no dependency on M2’s hosted delivery.
