---
schema: "aitm.review-response/v0"
level: "spr"
story: 83
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_base_commit: "350ba4b8f7d2d178b9837785b8659b5d0014cfdf"
artifact_digest: "sha256:96c27b0b983d962df6ec3387339c682970cd12205d6eb52a454b41e0abdce050"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:6980827636d662a6ffd050a210da18005fadd512151d1fa868fb3348a46b460d"}
start_basis: "unknown"
submitted_at: "2026-11-09T14:20:25+00:00"
finding_ids: ["SPR-D01", "SPR-D02", "SPR-D03", "SPR-D04", "SPR-D05"]
answered_finding_ids: []
---

I reviewed all 49 lines of the current artifact at `sha256:96c27b0b983d962df6ec3387339c682970cd12205d6eb52a454b41e0abdce050`.

The reviewer retrieved all 49 lines and 11,594 bytes. It requested exact cutoff and scope boundaries, stable identities, account-only quota semantics and durable handoff decisions.

## Required changes

- **SPR-D01** Separate delayed first scans, in-flight cutoff and late revisions. Advance excluded baselines without retaining their usage.
- **SPR-D02** Order proven scope markers before the first child request and on return to the epic, even when the scan sees the boundary first. Test both arrival orders and owner-only defaults.
- **SPR-D03** Separate logical identity from file incarnation. Require archive and reset continuity, quarantine overlap and specify conflicting Claude identities.
- **SPR-D04** Keep changing same-window readings account-wide and require provider debit evidence for any per-agent attribution.
- **SPR-D05** Track per-key pending and reconciliation state across the export watermark. Verify replay, finalization after withholding, correction and conflicting keys.

## Decision

**changes-requested**
