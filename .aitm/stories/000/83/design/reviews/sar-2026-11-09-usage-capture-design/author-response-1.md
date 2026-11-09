---
schema: "aitm.review-response/v0"
level: "sar"
story: 83
role: "author"
round: 1
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_base_commit: "4028322593971d7bbf605582a0695b25d849ec7e"
artifact_digest: "sha256:96c27b0b983d962df6ec3387339c682970cd12205d6eb52a454b41e0abdce050"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"}
start_basis: "unknown"
submitted_at: "2026-11-09T14:17:20+00:00"
finding_ids: []
answered_finding_ids: ["SAR-D01", "SAR-D02", "SAR-D03", "SAR-D04", "SAR-D05", "SAR-D06"]
patch: "patch-001.diff"
---

Accepted SAR-D01 through SAR-D06. The revision uses provider-observed boundaries and a durable inbox, scope-level enrollment, a capture cutoff, partial terminal status, a reproducible export and qualified aggregate handling. See the numbered revision patch.
