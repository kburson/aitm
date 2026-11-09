---
schema: "aitm.review-manifest/v0"
level: "spr"
story: 83
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_base_commit: "350ba4b8f7d2d178b9837785b8659b5d0014cfdf"
base_digest: "sha256:96c27b0b983d962df6ec3387339c682970cd12205d6eb52a454b41e0abdce050"
final_digest: "sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de"
rounds: 2
outcome: "exhausted"
execution: "manual"
authority_assurance: "declared-manual"
author: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"}
reviewer: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:6980827636d662a6ffd050a210da18005fadd512151d1fa868fb3348a46b460d"}
verified_at: "2026-11-09T14:20:25+00:00"
---

# SPR review record

Independent same-provider session using manual SPR transport. Both rounds report fresh untruncated full-file reads and the same observed Codex model and effort. The required IDs and outcomes were retained from the reviewer. This is scoped manual evidence for #83.

Each response binds exact input or output bytes. Apply the numbered patches from empty storage. Turn starts were unavailable for this portable record.

| Patch | Resulting SHA-256 | Source commit |
| --- | --- | --- |
| [patch-000.diff](patch-000.diff) | `sha256:96c27b0b983d962df6ec3387339c682970cd12205d6eb52a454b41e0abdce050` | `350ba4b8f7d2d178b9837785b8659b5d0014cfdf` |
| [patch-001.diff](patch-001.diff) | `sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de` | `281b57876071de97c9734dd3e89f0cd89fbc2b7a` |
| [patch-002.diff](patch-002.diff) | `sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de` | `281b57876071de97c9734dd3e89f0cd89fbc2b7a` |
