<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-19d319c42ae6474b0b404114fd611a9c"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/1/design/architecture.md"
artifact_commit: "42c19d20382c324703e791390a6f8747640974b9"
artifact_blob: "53345663dd176a1c51703ad26ce34ae791ca83f8"
artifact_digest: "sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  model_display: "gpt-6-astra"
  session_fingerprint: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
  identity_source: "runtime"
started_at: "2026-11-09T03:52:36.704Z"
submitted_at: "2026-11-09T04:00:16.775Z"
finding_ids: []
answered_finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Accepted all five required findings after checking the owner decision record and the architecture/core/master-plan boundaries. Revised only architecture.md. None requires reversing an owner decision or resolving an existing owner choice. The canonical digest and effective-policy rules below are architecture refinements, not claims that the owner already specified their implementation.

The exact revised FUR digest before submission is sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93. The review tool owns the sealed metadata and commit; its resulting protected fields remain authoritative.

## Finding dispositions

- **R1-F001: accepted.** Chose a canonical authored-content digest rather than moving required frontmatter out of story documents. This preserves the explicit frontmatter decision in draft.md, Data store. Canonicalization covers authored body and semantically authored header fields and excludes only schema-defined generated metadata. Core and peer-review must share its versioned definition. Raw file digests and patches remain separate reconstruction evidence. Current v0 review snapshots stay unchanged; M1 migration must establish their authored-content binding before regenerating metadata. This avoids treating unreviewed content as accepted and avoids pretending the current tooling already implements canonicalization.
- **R1-F002: accepted.** Distinguished the pre-M1 planning checkout from the M1-to-M4 import route. M1 must import the FUR and review folder through the core compare-and-swap writer, scoped to the story, before retiring the checkout. Review branches derived from planning are distinct refs, so guard layers must permit them while continuing to protect the configured planning ref. This follows the agreed plumbing-writer direction in draft.md, Data store, and the master plan's M1 retirement; it does not move a milestone or edit the core/master-plan files.
- **R1-F003: accepted.** Assigned delivery/merge evidence to the git-host provider and defined delivery as a verified mapping from reviewed source to the declared target result, independent of equal SHAs. Core must also support verifiable core-only/offline local delivery. An unverifiable remote target stays pending; an issue's closed state is not evidence. Section designs retain mechanism and merge-strategy choices and must prevent unreviewed changes being attributed to a reviewed version. The original after-delivery sign-off and review-ended implementation clock remain intact.
- **R1-F004: accepted.** Named the committed default-branch config, read locally from its fetched ref, as workflow-policy authority. Story-branch edits to policy take effect after delivery to that branch. Transitions record policy revision and effective settings; bootstrap, ref selection and freshness/offline rules remain core-design obligations. This refines the agreed/default-branch config direction without changing current advisory mode or any numerical limit.
- **R1-F005: accepted.** Applied the workflow-ref constraint to the Pages build as well as the audit. The viewer may use a suitable scheduled, dispatched or other trigger with disclosed snapshot freshness; its design chooses the mechanism. The independent every-push audit requirement remains unchanged. Verified the factual constraint against primary GitHub documentation rather than relying on the reviewer's unverified recollection.

## Changes made

Added authoritative-policy, delivered-version, canonical-acceptance and M1-import contracts; extended the viewer constraint and core reconciliation obligations. Updated only the FUR's timestamp and last working branch as part of this reviewed revision.

Optional suggestions:

1. Adopted the clearer event-union wording: the current proposal is not accepted as an exception; core review must demonstrate compliance or replace it.
2. Added the proposed root README allowance to core reconciliation, without granting a new planning-path exception.
3. The final XPR export will map the native ai-peer-review.response/v1 responses into the same aitm.review-response/v0 format as SAR/SPR, preserving native originals and provenance. Native protected records will not be edited to impersonate the export schema. This is collateral work after the native cycle, not a FUR policy change.

No context document, decision record, SAR/SPR record, story state or trunk content was revised. Existing open decisions remain open. SAR/SPR still describe their original accepted bytes; XPR's new raw digest does not retroactively replace those results.

## Declined changes and rationale

None. All required findings are accepted. No owner decision is requested for this round. The alternative of removing required frontmatter was not selected because canonicalization preserves the owner's stated file-metadata requirement.

## Verification

- Checked all five findings against draft.md and the context-only core design/master plan. The existing expansion interpretation/cap, package name, audit mechanism and review-depth/refactor choices remain unresolved.
- Verified every relative Markdown link in the revised FUR resolves and git diff --check passes.
- Verified architecture.md is the only changed tracked file. All current native review output is under story 1; isolated tool setup remains untracked and will not be imported into planning.
- Primary-source checks: GitHub locates workflows at the event-associated ref ([workflow triggers](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows#workflow-triggers)); branch-based Pages publishing uses the root or docs directory, while custom Actions is a separate route ([publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)). No live workflow or Pages configuration was changed.
- No implementation tests apply to this document-only turn. Exact per-turn patches, response metadata and byte-for-byte reconstruction will be verified after the native review completes and before planning publication.
