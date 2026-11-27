<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-efbb7e41b341b1d2dac3a40da827d70b"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md"
artifact_commit: "27c54333856e11b8453b9f3a09b4458e89c99756"
artifact_blob: "c88410d3418c671cbd5a3f2f25b5f9526696db88"
artifact_digest: "sha256:330c2351403277f8845b6dd162472a7844ba0ac7e944ce60f7dae8f13589a1d5"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.2-sol"
  model_display: "gpt-6.2-sol"
  session_fingerprint: "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
  identity_source: "runtime"
started_at: "2026-11-27T03:30:02.221Z"
submitted_at: "2026-11-27T03:33:55.177Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Resolved the seven required findings in the configured workflow amendment. The owner-directed child JIT review threshold remains explicit.

## Finding dispositions

1. Accepted. Typed lifecycle bindings identify the terminal, non-delivery, and reopen destinations. The validator checks them and forbids ordinary or rework exits from the terminal state regardless of its position.
2. Accepted. The designated integration owner has a resource-only Plan action. Dependents may use the verified resource while the owner is still in Plan and has no open attempt or clock.
3. Accepted. Added an explicit replacement table for the fixed chain, Backlog design acceptance, design rework, split, Dev and Test checks, ordinary rework, and graduation provisioning. Dev exit retains tagged or composed source and expansion resolution.
4. Accepted. Enforce blocks failed or unavailable facts. Advisory may record unverified progress with mandatory integrity and attempt bookkeeping. Verified delivery and managed effects still require their own positive evidence.
5. Accepted. Same-head, same-target tip advance invalidates CI and admission. Positive review-input equivalence permits fresh CI in Review while retaining XPR provenance. Source movement, retarget or failed equivalence require fresh CI and XPR. Approved delivery transformations remain exact and separately verified.
6. Accepted. Post-delivery Review is limited to observation, reconciliation, and closeout or finalization. It refuses rework, trip demotion, pivot and non-delivery closure. Added installed-path coverage for that refusal.
7. Accepted. Added mappings for Develop and early states, including supported reuse of current design acceptance and explicit recovery when evidence is stale.
8. Retained the requested `onEnter[]`, `action[]`, and `onExit[]` spellings as the workflow interface.

## Changes made

Added required predecessor metadata and reachable-path validation, an Explain example for an unavailable provider, and installed-path vectors for integration provisioning, review evidence refresh, advisory behavior and post-delivery refusal.

## Declined changes and rationale

The optional naming normalization would change the state slots specified by the owner. The draft retains those slots.

## Verification

Parsed both TOML blocks, checked eight states, explicit transitions, terminal and recovery targets, resource-only and CI refresh action placement, and local document links. The Git whitespace check passed. These checks cover the design artifact.
