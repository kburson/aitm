---
schema: "aitm.story/v0"
id: 114
title: "[M04] Adapter contract and existing providers"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/114"
parent: 100
children: []
blocking: [115, 116, 134, 135]
blocked-by: [113]
created: "2026-11-10T13:57:53Z"
updated: "2026-11-10T16:24:24+00:00"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/jit.md", "plan/jit-review.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M04", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "d5f5b6b75b4a42e6a7101ffa3d388c2eae603ea11e00d88bc65ab874efe27499"}
---

# [M04] Adapter contract and existing providers

[GitHub issue #114](https://github.com/kburson/aitm/issues/114) · [Parent #100](../100/story.md) · [Accepted plan leaf M04](../100/plan/multi-project-usage-monitor-implementation-plan.md#m04-adapter-contract-and-codex-or-claude-bridge)

**Required predecessors** [M03 #113](../113/story.md).

Use the completed [Grok #101](https://github.com/kburson/aitm/issues/101) and [Linux #102](https://github.com/kburson/aitm/issues/102) reports as applicable. They are evidence inputs carried by the parent.

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M04. Adapter contract and Codex or Claude bridge

**Files** Create `S/sources/adapter.py` and `T/test_monitor_adapters.py`. Adapt `S/sources/{scan,codex,claude}.py` without rewriting proven token and marker logic.

**Contract** `ProviderAdapter.discover(root: SourceRoot) -> Iterable[SourceLocator]` and `ProviderAdapter.read_delta(locator: SourceLocator, cursor: StreamCursor | None) -> AdapterBatch`. `AdapterBatch` contains verified native lineage, boundary, time basis, usage revision, project context and diagnostics. The adapter declares a qualified host, client version and format tuple. Derive keyed service identity from verified lineage before choosing a project key. Keep transcript content transient and discard anything outside the field allowlist.

- [ ] Write `test_desktop_and_cli_in_shared_root_admit_only_qualified_surface`, `test_codex_archive_counter_epoch_replays_once`, and `test_claude_streamed_revision_and_nested_overlap`. Assert an unqualified macOS CLI rollout contributes zero with a sanitized coverage reason. Retain Desktop native receipt and Claude linked-request proof.
- [ ] Before fixing the interface or enabling a host surface, obtain a controlled native receipt, its adjoining request and durable cursor evidence for that surface. Explicitly prove the Linux Codex CLI carrier independently of Desktop and the Linux Claude Code request link. Record exact client and format. If a carrier is unavailable, split its M04 adapter slice at JIT, keep that surface disabled, and make the corresponding M19 qualification depend on the accepted slice. Run red. Implement the contract around the current collectors and add the verified receipts as sanitized fixtures. Run green with `test_scan.py`, `test_codex.py` and `test_claude.py`. Commit M04.

The [reviewed M04 pickup](plan/jit.md) covers the macOS bridge. [#134 M04-LC](../134/story.md) and [#135 M04-LA](../135/story.md) track the Linux carrier work. The new leaves depend on this contract and both block #129.
