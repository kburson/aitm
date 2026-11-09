---
schema: "aitm.review-response/v0"
level: "spr"
story: 83
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
artifact_base_commit: "51d88fd6b246a717420d8ebdc30102c1aa912088"
artifact_digest: "sha256:22eba0e6fb1fb5f83b196348d42d7bdb2dd9186818e794a642028a6dfaede55b"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high", "session_fingerprint": "sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287"}
start_basis: "unknown"
submitted_at: "2026-11-09T14:33:32+00:00"
finding_ids: ["SPR-P01", "SPR-P02", "SPR-P03", "SPR-P04", "SPR-P05", "SPR-P06", "SPR-P07"]
answered_finding_ids: []
---

I reviewed all 145 lines of the current artifact at `sha256:22eba0e6fb1fb5f83b196348d42d7bdb2dd9186818e794a642028a6dfaede55b`.

The reviewer read all 145 lines and the full accepted design. It identified seven required gaps in the plan contracts, resilience, privacy and production proof.

## Required changes

- **SPR-P01** Own shared contracts upstream and prove segment eligibility and pre-enrollment boundary evidence without retaining unbound usage.
- **SPR-P02** Distinguish late ingestion from retroactive scope claims with monotonic scope sequence and verifiable causal order.
- **SPR-P03** Commit the minimum provider resume state atomically with source progress and observations.
- **SPR-P04** Qualify protected key and database backup/restore, failed launch rollback and canary scans of durable inputs and outputs.
- **SPR-P05** Bind C01 to observed startup, current watermarks, on-host recovery rehearsal and verified shared-chat rollup evidence.
- **SPR-P06** Pin export scope and pricing provenance and prove durable receiver restart with withheld records and immutable accepted keys.
- **SPR-P07** Wire the accounting and rollup contract into the actual service and CLI path.

## Decision

**changes-requested**
