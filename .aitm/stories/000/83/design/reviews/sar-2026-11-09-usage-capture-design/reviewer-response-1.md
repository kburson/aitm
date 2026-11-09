---
schema: "aitm.review-response/v0"
level: "sar"
story: 83
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_base_commit: "4028322593971d7bbf605582a0695b25d849ec7e"
artifact_digest: "sha256:c85df19d73b37d42123c537f696a0182b68e69add61768e4101c73e9d5227c13"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"}
start_basis: "unknown"
submitted_at: "2026-11-09T14:17:20+00:00"
finding_ids: ["SAR-D01", "SAR-D02", "SAR-D03", "SAR-D04", "SAR-D05", "SAR-D06"]
answered_finding_ids: []
---

I reviewed all 49 lines of the current artifact at `sha256:c85df19d73b37d42123c537f696a0182b68e69add61768e4101c73e9d5227c13`.

Read the initial design with the #73 evidence and #51 ingestion seam. The builder check exposed gaps in trusted attribution, cutoff, export and terminal proof. Overlapping parent and child usage also needs an explicit rule.

## Required changes

- **SAR-D01** Define trustworthy scope markers and behavior when a development default conflicts.
- **SAR-D02** Filter eligibility by session segment and state the checkout and explicit-binding enrollment rules.
- **SAR-D03** Define activation cut-off, first baseline and catch-up coverage.
- **SAR-D04** Define provider terminal evidence and the treatment of partial Claude observations.
- **SAR-D05** Fix the export cut-off and separate observation revisions from immutable Core intake.
- **SAR-D06** Specify treatment of nested totals when parent and child usage overlap.

## Decision

**changes-requested**
