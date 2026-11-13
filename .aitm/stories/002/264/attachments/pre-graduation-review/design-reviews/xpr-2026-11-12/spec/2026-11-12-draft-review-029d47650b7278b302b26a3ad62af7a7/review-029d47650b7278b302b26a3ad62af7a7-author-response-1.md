<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-029d47650b7278b302b26a3ad62af7a7"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md"
artifact_commit: "ad20083299fc1ea449b39e8d5a3024580e144944"
artifact_blob: "f3ed42891b5c4fca7322414c46f4c612f586565b"
artifact_digest: "sha256:f2ce1a217e971ccbeff3ad119725c672a8b8c0af2a104d6d61c6a26ce8726030"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
  identity_source: "runtime"
started_at: "2026-11-12T14:34:45.378Z"
submitted_at: "2026-11-12T14:39:42.910Z"
finding_ids: []
answered_finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The author accepted all five required findings. The full 67-line revision has raw SHA-256 `0adca6f338bbda55f98b17708bcd6d932b0ca87b6ca6965a0994bc2151e78abd`.

## Finding dispositions

- R1-F001 accepted. Preserve the actual declared boundary edge between a direct child and a descendant of a child epic. Identify the admitted descendant and its containing child epic. Edges entirely below the selected layer belong to their own maps. The nested fixture exercises both directions.
- R1-F002 accepted. A layer is one hop on admitted declared edges. If filtering hides an intermediate on an undeclared shortcut, show that paths are hidden and let detail expose the admitted path. The drawn map continues to use declared edges. Added a fixture for an absent declared shortcut.
- R1-F003 accepted. The Python command belongs under `tools/story_dashboard/`. The TypeScript viewer feature belongs in `aitm-viewer`, which is the meaning of the package field. Shared expected graph and audit fixtures establish conformance for the two implementations.
- R1-F004 accepted. The output path includes the exact source planning commit and the versioned visibility profile. The commit's committer timestamp fixes the lifecycle cutoff. Record the authorized destination.
- R1-F005 accepted. Only final displayed child-to-child arrows can witness an omitted direct child edge. Boundary links and epic gates stay visible and cannot enter a witness.

## Changes made

Specified numeric witness tie-breaking, deterministic Markdown and audit bytes, and fixture coverage for profile provenance, nested boundaries, hidden intermediates, and cross-implementation parity. The linked follow-on and the accepted M6 release scope are stated in the design.

## Declined changes and rationale

None for the five required findings. The Plan can select presentation controls and any supported release vehicle within the accepted follow-on scope.

## Verification

Checked the complete revised artifact, its SHA-256, and its whitespace. Verified the current planning worktree has the same #247, #258, and #260 source files as the M6 reference pin. The two #133 pins and expected graph counts remain the qualification fixtures.
