---
schema: "aitm.story/v0"
id: 128
title: "[M18] Native macOS qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/128"
parent: 100
children: []
blocking: [129]
blocked-by: [127, 304]
created: "2026-11-10T13:58:16Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M18", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "55abe2713c8afd7be798361def16c6c27bdafdc41e155fbd7ca932569f8cbcb7"}
---

# [M18] Native macOS qualification

[GitHub issue #128](https://github.com/kburson/aitm/issues/128) · [Parent #100](../100/story.md) · [Accepted plan leaf M18](../100/plan/multi-project-usage-monitor-implementation-plan.md#m18-controlled-macos-qualification)

**Required predecessors** [M17 #127](../127/story.md).

Apply the accepted plan’s [legacy command surface after adoption](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#legacy-command-surface-after-adoption).

Use the complete [NA-1 acceptance case](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#native-acceptance-case-na-1).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M18. Controlled macOS qualification

**Files** Extend `S/qualification.py`, `T/test_activation_receipt.py` and `README.md`. Retain sanitized evidence outside the product checkout until the declared delivery step.

- [ ] Add receipt validation `test_monitor_mac_receipt_requires_exact_provider_and_service_proof`. It rejects wrong builds, insufficient overlap, a stale heartbeat, missing production scope-carrier proof or any missing NA-1 outcome. Run red, implement and run green with the activation and installer tests.
- [ ] Run on an isolated candidate with actual Codex Desktop and Grok Build CLI with the separately observed negative Claude source. Run NA-1 and the exact legacy marker invocation against adopted state. Verify a parked resume with two distinctly story-bound Grok turns through production admission, late writes, a separately eligible hookless Grok completion counted once in its interval without a story, fork overlap and the exact excluded Claude target case from amended NA-1, one LaunchAgent, crash catch-up and fixed #83 export parity. Keep private raw traces and publish only a sanitized receipt. Commit M18.

Require the exact-build sanitized negative Claude refusal and isolation evidence in the macOS receipt. The admitted allowlist has no Claude tuple. Preserve all other controlled macOS qualification requirements.

#304 supplies the isolated issuer's host executable and current authorization evidence. #128 owns the final native macOS installation, target acceptance and signed catalog. [Qualified-cost R2](https://github.com/kburson/aitm/blob/47228b4bdace19f25627814cd50b1664342bcca8/.aitm/stories/001/100/plan/2026-11-14-100-qualified-cost-acceptance-r2.md) governs the controlled qualification matrix. [Issuer amendment](https://github.com/kburson/aitm/blob/79aecafe17c5dc0417fd00c2ecd37cdfe3651d58/.aitm/stories/003/303/plan/2026-11-14-303-isolated-source-issuer-amendment.md).
