<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9a11494429336f06db1d427236d5aa0e"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_commit: "e6411995f65df61da29fa737bcfcfa722a8a9265"
artifact_blob: "913cf7e4702c87f79f37ef4e8e9b2bb002bf9396"
artifact_digest: "sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
  identity_source: "runtime"
started_at: "2026-11-09T14:20:35.970Z"
submitted_at: "2026-11-09T14:23:49.291Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revised the lifetime measurement design after the complete independent read.

## Finding dispositions

- Accepted design finding 1. Explicit owner enrollment replaces checkout inference. A marked same-story reviewer remains a separate participant. Unproven sessions and contradictory claims stay unassigned.
- Accepted design finding 2. Persist keyed locators and anchors, rediscover only within approved roots, and exclude raw paths and branches from exports and diagnostics.
- Accepted design finding 3. Version the observed source and expose parser drift and missing usage as coverage gaps even when the service is alive.
- Accepted design finding 4. Qualify nested and retry paths, model changes and evidence gaps. The plan will preserve an explicit unsupported case where provider evidence is absent.

## Changes made

The writer lease, dedicated environment, retention diagnostics and versioned activation receipt incorporate the optional operational improvements.

## Declined changes and rationale

None.

## Verification

Read the updated full file. Confirmed distinct scope and provider records, durable source identities, safe export and continuing operation after Core adoption.
