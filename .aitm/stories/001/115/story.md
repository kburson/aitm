---
schema: "aitm.story/v0"
id: 115
title: "[M05] Grok evidence adapter"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/115"
parent: 100
children: []
blocking: [120, 121, 137]
blocked-by: [114]
created: "2026-11-10T13:57:54Z"
updated: "2026-11-10T17:49:45+00:00"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/carrier-capture.md", "plan/jit.md", "plan/jit-review.md", "plan/linux-carrier-split.json", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M05", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "ec3fe35d7eda1c6ab8b87f266a2dcd28fb97c00d37563551ae3036771983bb06"}
---

# [M05] Grok evidence adapter

[GitHub issue #115](https://github.com/kburson/aitm/issues/115) · [Parent #100](../100/story.md) · [Accepted plan leaf M05](../100/plan/multi-project-usage-monitor-implementation-plan.md#m05-grok-whole-turn-adapter)

**Required predecessors** [M04 #114](../114/story.md).

Use the completed [Grok #101](https://github.com/kburson/aitm/issues/101) and [Linux #102](https://github.com/kburson/aitm/issues/102) reports as applicable. They are evidence inputs carried by the parent.

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M05. Grok whole-turn adapter

**Files** Create `S/sources/grok.py`, `T/test_grok.py` and allowlisted fixtures under `T/fixtures/grok/`. Extend the monitor-only provider/model enums and Grok payload in `S/monitor_types.py` with provider ticks and normalized cache categories. Generalize provider-specific rate validation in `S/pricing.py` and add a versioned monitor rate resource under `S/rates/`. Keep legacy decoder types, `2026-11-09.json`, its default and RateBasis digest unchanged. Grok fields enter only the versioned monitor export.

**Contract** `GrokAdapter.read_delta(locator: SourceLocator, cursor: StreamCursor | None) -> AdapterBatch`. Match a durable native `turn_completed` to a verified prompt lineage. Use completion time, validate persisted and headless token semantics separately, and use the snapshot for corroboration. A snapshot-only row, an incomparable native revision and unresolved overlap cannot create an attributable charge. Preserve Unknown API-equivalent pricing when the rate basis is missing.

- [ ] Write `test_resume_and_snapshot_replay_count_two_distinct_turns`, `test_hookless_eligible_completion_keeps_native_interval`, `test_fork_excludes_inherited_turns`, `test_late_folded_parent_never_adds_to_child`, and `test_snapshot_conflict_and_cache_categories`. Also add `test_complete_native_only_counts_with_corroboration_gap` and `test_snapshot_only_does_not_charge`. Add `test_grok_rate_classes_do_not_use_claude_defaults`, `test_unknown_grok_rate_and_provider_ticks_remain_separate`, and `test_grok_preserves_legacy_rate_digest_and_fixed_export`. Verify the v1 decoder refuses a Grok provider value. Cover cancellation, concurrent prompts, rewind, later append and copied history as gated fixture cases.
- [ ] Pin the approved production scope-marker carrier with a controlled native capture before finalizing the Grok contract. #101 is the macOS feasibility baseline. If the Linux carrier is unavailable, assign the remaining implementation to an explicit M05 slice required by M19 and keep that surface disabled. Run red. Implement versioned native decoding and separate rate provenance. Run green with `test_accounting.py`. Commit M05. Later qualification proves actual receipt authority on every advertised host.

[Controlled macOS Grok marker capture](plan/carrier-capture.md). Pickup review and native Linux carrier evidence remain open.

The exact macOS pickup passed independent review. [#137 M05-LG](../137/story.md) owns the Linux carrier, and #129 requires its delivery. [Reviewed pickup](plan/jit.md) · [Review](plan/jit-review.md).
