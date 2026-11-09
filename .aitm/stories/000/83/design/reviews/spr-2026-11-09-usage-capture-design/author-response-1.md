---
schema: "aitm.review-response/v0"
level: "spr"
story: 83
role: "author"
round: 1
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_base_commit: "350ba4b8f7d2d178b9837785b8659b5d0014cfdf"
artifact_digest: "sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"}
start_basis: "unknown"
submitted_at: "2026-11-09T14:20:25+00:00"
finding_ids: []
answered_finding_ids: ["SPR-D01", "SPR-D02", "SPR-D03", "SPR-D04", "SPR-D05"]
patch: "patch-001.diff"
---

Accepted SPR-D01 through SPR-D05. The revised design defines cutoff baselines, both marker arrival orders, archive and epoch continuity, account-level quota and per-key import dispositions. Added the optional redaction, restore identity and separate lag diagnostics.
