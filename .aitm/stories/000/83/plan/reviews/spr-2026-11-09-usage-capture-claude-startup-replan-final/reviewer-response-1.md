---
schema: "aitm.review-response/v0"
level: "spr"
story: 83
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/83/plan/usage-capture-claude-startup-replan.md"
artifact_base_commit: "42beb1af5893a401eaaa91150a2b4d66be07251b"
artifact_digest: "sha256:a8237e85e214701c19207290d6de46eb4bcd8736c6c0a4342246069f0f70e39f"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287"}
start_basis: "unknown"
submitted_at: "2026-11-09T22:43:21+00:00"
finding_ids: ["SPR-CS01"]
answered_finding_ids: []
---

I reviewed all 19 lines of the current artifact at `sha256:a8237e85e214701c19207290d6de46eb4bcd8736c6c0a4342246069f0f70e39f`.

Protected source and initial owner/caps were correct. Tighten the rule to the exact observed startup chain.

## Required changes

- **SPR-CS01** Require exact native queue keys, non-sidechain SessionStart hook-success with null parent, additional-context child, and first user origin linked to it. Add wrong-event, sidechain and unrelated parent tests.

## Decision

**changes-requested**
