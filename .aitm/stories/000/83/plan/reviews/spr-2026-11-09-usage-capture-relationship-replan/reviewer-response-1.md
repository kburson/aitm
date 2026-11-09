---
schema: "aitm.review-response/v0"
level: "spr"
story: 83
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md"
artifact_base_commit: "c6553b7150c6ff51f6e8dd826f1dc750071316cd"
artifact_digest: "sha256:2e2d9eea1be6e7402408420f1fb2c3c703cca3f41189c2bd0e7e11bfb2eb85c1"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287"}
start_basis: "unknown"
submitted_at: "2026-11-09T16:29:30+00:00"
finding_ids: ["SPR-REL01", "SPR-REL02"]
answered_finding_ids: []
---

I reviewed all 25 lines of the current artifact at `sha256:2e2d9eea1be6e7402408420f1fb2c3c703cca3f41189c2bd0e7e11bfb2eb85c1`.

Read all lines 1–20 and 21–25. Two required gaps in commit authority and interleaved publication ordering. The scope, estimate and Core exclusion hold.

## Required changes

- **SPR-REL01** Require the exact authoritative graph validator effect tuple, including revision keys and ordinals, at the guarded expected sequence.
- **SPR-REL02** Snapshot the relationship queue under the same pinned mutex as publication and release before commits and acknowledgments.

## Decision

**changes-requested**
