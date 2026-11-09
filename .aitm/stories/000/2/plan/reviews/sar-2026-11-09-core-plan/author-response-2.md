---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "author"
round: 2
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "f86dd7c1954215585dcbdbcc9bac0e7e490a1956"
artifact_digest: "sha256:54577b157af8c35296ceeb85d19b7d75af5a684bba79c45daeef493977b234e2"
patch: "patch-002.diff"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  effort: "xhigh"
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T07:02:10Z"
submitted_at: "2026-11-09T07:08:33Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R2-F001", "R2-F002", "R2-F003", "R2-F004", "R2-F005"]
---

## Summary

Accepted all five round-2 findings. The bounded leaf count and Plan total remain 62 / 194.5 h; original Refine remains 180 h. Production and qualification contracts now identify the remaining shared call sites and exact operation boundaries.

## Finding dispositions

- R2-F001 accepted: C49 now explicitly depends on local authority C21 and the registration owners C10/C41/C48; C51 depends on C18 index. CLI surface checks are registration/options/JSON checks; operational positive proof is the collected C49/C50/C51/C59 scenario union. The nominal walk invokes installed local graduate, not a helper or external-only finalizer. Dependencies, table order and body fields were synchronized.
- R2-F002 accepted: C04 defines RelatedWriteSet; C22's pure constructor accepts it; C13/C21 local authority signatures carry it into the same child-number/story CAS. C30 depends on C21 and supplies exact origin reservation/attempt preconditions plus block/expansion/clock changes. Its actual local-only/shared expand tests retain the earlier reservation pause and prove no permanent child/number before authority, no unblock gap and one child after races/lost ACK. External uncertain issuance stays separate.
- R2-F003 accepted: C09 owns default bounded publication in CommandService/dispatch, tested with real describe and later real promote without --push. C31 wires the preflight port before normal sync/mutation and every CAS retry; C32/C38 invoke it after retained result ingestion before effective success. C42 itself constructs Close outcome and atomically commits it with closure/session/retro/relations; C44 only reports it and ingests usage. Shared files, dependencies and actual-entry-point tests are named, including crash/refusal and no half-close.
- R2-F004 accepted: C46 early dry-run reports inventory/transformations and explicit unbound outputs. C48 supplies one pure CutoverBuilder for bound preview and apply, with pinned declaration/build context; actual execution/publication observations are separate receipt data. C51 compares predicted facts/snapshots/views/receipt-excluded payload hash to actual apply and retains no-mutation tests. No second transformation implementation or invented output hash.
- R2-F005 accepted: C60 checker fixture tests and implementation precede a separately authorized once-per-release operation outside pytest. Lost publication result is observed by exact version/source/artifact identity before any retry. Post-publication tests only observe/install/check that already-published artifact, with an explicit observed-release manifest; no test failure can dispatch or republish its own job. C5 stays pending until both-platform evidence succeeds.

## Changes made

Updated actual FUR directly, preserving round-1 changes. Reordered the table/sections from the explicit DAG after dependency additions; stable C-keys retained. Added specific trip-before-sync/CAS/completion qualification and clarified runtime composition ownership.

## Declined changes and rationale

None. No policy choice, production release/adoption or implementation is authorized by these revisions.

## Verification

Parsed table and sections to confirm identical estimates/dependencies, 62 unique keys, 194.5 h total and every estimate ≤4 h; explicit graph is acyclic/topologically ordered. Checked signature consistency for RelatedWriteSet/local authority, qualification call-site prerequisites and whitespace. Full-file round 3 is required; no runtime tests are claimed.
