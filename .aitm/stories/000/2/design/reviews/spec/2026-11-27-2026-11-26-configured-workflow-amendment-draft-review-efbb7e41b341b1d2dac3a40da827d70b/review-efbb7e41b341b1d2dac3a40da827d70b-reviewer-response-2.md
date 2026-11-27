<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-efbb7e41b341b1d2dac3a40da827d70b"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md"
artifact_commit: "c25f0562b1ba64785c960118396403ef8ebfb95d"
artifact_blob: "5a81dcba27f16370b2428262095fd409d6b091d8"
artifact_digest: "sha256:3a1ce63175d7eb446fc9514b394c3c4916ef7a0adc22234ac6e62170fc70f004"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:4a404e4d685336b447771b3d5eceaa0ba37b0cc7a6f54d991bd8e177c503acc6"
  identity_source: "runtime"
started_at: "2026-11-27T03:30:37.750Z"
submitted_at: "2026-11-27T03:34:47.710Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised artifact (blob `5a81dcba`) against my turn-1 findings and the author's dispositions in author-response-1. Every required change is resolved in the artifact text, not only in the response:

1. **Terminal and recovery bindings (F1).** A `[lifecycle]` table declares `terminal`, `non_delivery`, `reopen_design` and `reopen_plan`. The validator refuses ordinary or rework exits from the declared terminal state "even if the file contains later definitions", and the prose now says lifecycle meaning comes from typed operations and bindings rather than position. Resolved.
2. **Integration-story provisioning (F2).** `core.dev.prepare-integration-resource` is a resource-only action in Plan. It excludes child deliveries from the provisioning dependency set and leaves the integration story in Plan with no attempt or clock. Ordinary Dev pickup reuses the verified resource incarnation. An installed-path proof was added. Resolved.
3. **Superseded Core contracts (F3).** The new section "Core design contracts amended by this profile" covers each item I listed: the chain and Backlog design acceptance, the design-rework destination, the split route (now Refine → Design, with oversize found in Plan or JIT routed through Design rework), the Develop and Test exit checks (story-tagged or composed source and expansion resolution now in `core.dev.review-candidate-current`), the rework edges, and graduation provisioning. Resolved.
4. **Advisory mode (F4).** A dedicated paragraph says how both modes treat blocked and unavailable results. Integrity, edges, identity and storage are mandatory in both modes. Missing evidence can never authorize a managed effect, an effective review, or a delivered disposition, and advisory closes go through the unverified terminal route. A matching proof was added. Resolved.
5. **Target movement during Review (F5).** A three-row table now separates a target-tip advance (fresh CI; the existing XPR carries over only on positive, recorded equivalence), source or retarget changes (fresh CI and XPR, with findings preserved), and approved delivery transformations (bound before dispatch and verified after). It also points to a merge queue or an ordered check-and-admit path for moving targets, and `core.pr.observe-ci` was added to Review. Proofs were added. Resolved.
6. **Post-delivery Review (F6).** Once delivery is verified, only observation, reconciliation, closeout and finalization are allowed. Rework, trip demotion, pivot, design rework and non-delivery closure are refused. Proofs were added. Resolved.
7. **Cutover (F7).** Mappings now cover Backlog, the pre-Plan states with existing design acceptance, Develop and Test, and pre- and post-delivery Review. Resolved.
8. **Naming nit (F8).** The author declined because the owner specified the slot names. That is acceptable, since a nit does not block acceptance.

I found no new blocking defects in the revision.

## Findings

1. **Nit: the rework guard does not name the failed target-equivalence trigger.** The Review revalidation table says that when equivalence cannot be proved after a same-target tip advance, the story should "take Review → Dev". The `core.review.rework-authorized` contract still lists only "a recorded changes-requested verdict or explicit source invalidation before delivery". A failed equivalence comparison is arguably an "explicit source invalidation", but an implementer could read the guard narrowly and block the route the table requires.
2. **Nit: capability namespace and state placement.** `core.dev.prepare-integration-resource` sits in Plan's `action[]` but uses the `core.dev.*` prefix. Rule IDs are permanent, so the prefix will outlive any rename of the state. This is harmless but slightly misleading.

## Required changes

None.

## Optional suggestions

1. Extend the `core.review.rework-authorized` contract to name failed target-equivalence or retarget invalidation as an accepted trigger (Finding 1).
2. Consider naming the capability for its function rather than a state, for example `core.resource.prepare-integration` (Finding 2).
3. In the resource-only Plan action, state the fencing and admission key used without an attempt generation, for example the integration resource intent and its role scope. That keeps it aligned with Core's managed-start admission contract, which is otherwise keyed by attempt or binding generation.

## Decision

accepted
