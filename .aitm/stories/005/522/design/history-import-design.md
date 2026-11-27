# M7 design draft — Validated history import

Issue [#522](https://github.com/kburson/aitm/issues/522) · Parent #1

## Goal and boundary

Import a reusable legacy AITM corpus with reproducible provenance for estimation and planning research. M7 owns source inventory, evidence normalization, repeatable import, and a validation report. It consumes Core’s released story, estimate, outcome, and v0 read/validation contracts. M7 owns the legacy source adapter and the separate corpus export envelope. This dependency supplies schemas and a qualified read/validation path. M7 exercises that path on disposable fixtures and does not require production cutover or native state writes. The importer runs with the rubric absent. Historical closure is retained as source data, with imported stories distinguishable from native workflow records.

M7 waits for [Core release #72](https://github.com/kburson/aitm/issues/72), including the versioned Core story/estimate/outcome schema, source identities and v0 reader or adapter contracts, and the M2 source-access capability or a separately approved equivalent read-only adapter. The source-access requirement needs a scoped authenticated readback against the legacy repository. Link the owning M2 source-access issue once it exists. M7 supplies the validated corpus required by [#523](https://github.com/kburson/aitm/issues/523).

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
- Resolve the storage and publication route, allowed legacy evidence fields, exact M2 source-access proof, trusted Timing Log formats, and exception policy before implementation pickup.
