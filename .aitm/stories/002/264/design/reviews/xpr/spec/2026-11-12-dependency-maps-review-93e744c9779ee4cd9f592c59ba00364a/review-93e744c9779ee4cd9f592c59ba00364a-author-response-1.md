<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-93e744c9779ee4cd9f592c59ba00364a"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/264/design/dependency-maps.md"
artifact_commit: "d5c1413a0658f904de7ed921bec872797a376f15"
artifact_blob: "06aabce1e95b449363555dc3dad4ce3a368ec7bb"
artifact_digest: "sha256:f8d229b076947ac00fae768ea4f0df566ecabb5e74fae50ce3c1192388724ddf"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
  identity_source: "runtime"
started_at: "2026-11-12T15:03:08.076Z"
submitted_at: "2026-11-12T15:07:08.801Z"
finding_ids: []
answered_finding_ids: ["R1-F001"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The 60-line #264 design now specifies profile selection and provenance. Revised SHA-256: `50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7`.

## Finding dispositions

R1-F001 accepted. Require a profile key, define private-local-v1, and resolve attachment profiles from an owner-approved allowlist pinned in the exact planning commit, following the M6 preview precedent. Put pin, UTC cutoff, key and profile digest on every output. Use the same profile input across parity fixtures.

## Changes made

Clarified selected-epic gates versus direct edges involving child epics, tightened the path tie-break, and updated the draft reference.

## Declined changes and rationale

None for required findings. The implementation plan owns the optional decisions about release and viewer presentation.

## Verification

Checked the complete revised design, exact digest, unchanged #247 release scope and correspondence with the pinned M6 preview precedent.
