---
schema: "aitm.story/v0"
id: 426
title: "[Research Epic] Session-scoped agent cost for story runs"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/426"
parent: null
children: [427, 428, 429, 430, 431, 432, 433, 434]
blocking: []
blocked-by: []
created: "2026-11-24T15:08:19Z"
updated: "2026-11-25T01:26:49Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/cost-management-master-plan.md"], "attachments": ["attachments/native-harness-cost-findings.md"]}
expansions: []
trips: []
---

# [Research Epic] Session-scoped agent cost for story runs

[GitHub issue #426](https://github.com/kburson/aitm/issues/426)

## Research question

Which tactics let AITM measure agent usage and cost for assigned story runs and multi-story epic trails, including the orchestrator’s own work, delegated workers, and each headless XPR reviewer turn, without a persistent host monitor?

Related to [Epic #100](../../001/100/story.md). This is a separate top-level research epic. Complete these spikes and present the research decision before revisiting #100.

## Experiment rules

Use disposable, bounded workloads on Codex, Claude Code, and Grok Build. Record exact harness, version, surface, authentication/billing mode, session and turn boundaries, supported fields, and evidence provenance. Use the actual XPR headless route for cross-provider probes. Keep raw traces private and retain sanitized receipts. Distinguish measured tokens or credits, provider-reported charges, API-equivalent estimates, and gaps. Record each tactic as demonstrated, unsupported, or inconclusive for each tested surface.

Use each provider’s existing harness for interactive and headless execution. Capture provider-reported usage through structured results, supported events, or exact session and turn lookups. Adapters use portable code and remain small and session-scoped. Linux and macOS are the first targets, with Windows support planned. The suite ships no project-built native binaries, compiled extensions, or OS-specific capture code.

Run the spikes in order, one at a time. Close each with evidence and hand forward the limits and unanswered questions. A negative result still completes a spike when the tested boundary and evidence are clear. Use only the session in scope and disposable helpers that exit with the experiment.

## Research exit

Compare the tactics on existing-chat support, autonomous assignment, own-orchestrator coverage, per-turn XPR fidelity, delayed recovery, billing comparability, permissions, multi-story assignment and handoff fidelity, unattached-work attribution, and maintenance burden. Recommend the smallest evidence-supported strategy and quantify its gaps. Present the options and recommendation for a decision before changing the delivery plan in #100.

## Investigation ladder

1. #427 Measure the orchestrator from its existing interactive chat
2. #428 Retrieve cost later for an explicitly named session
3. #432 Self-report per-turn agent usage and retain a story cost log
4. #429 Measure usage from an orchestrator-launched headless run
5. #430 Qualify a callable result-and-usage turn for each XPR provider
6. #431 Deliver a usage receipt with every headless XPR turn
7. #433 Measure usage and time across epic trails
8. #434 Qualify the Codex headless AIPR review-lock path

## Follow-up experiments and controls

- After [#427](../427/story.md) and [#428](../428/story.md), use their findings to decide whether to open a run-scoped native telemetry spike. If interactive assignment or later lookup leaves a material gap, test whether each harness can enable native telemetry for one assigned session, compare it with the harness result by request identity, and end the receiver with the run. Start from the documented Claude control in [#282](../../001/282/story.md).
- [#433](../433/story.md) owns the concurrent attribution control and extends it to sequential assignment boundaries, agent detach and handoff, and later attribution of previously unattached work.
- [#434](../434/story.md) follows up on the Codex macOS review-lock gap from #430 and #431. It found no qualifying route in the tested configurations. Codex usage capture still worked on both failed reviewer attempts.
- Where available, use a bounded API-backed billing comparison to check receipt totals and reporting lag. Record what can be verified for subscription-backed runs separately. Repeat the same small workload across a harness version change when practical and record any capability or coverage drift.

## Research results and delivery recommendation

[Cost management master plan](plan/cost-management-master-plan.md) tracks the results of all eight spikes, open capabilities, the proposed delivery sequence, and lessons for later AIPR design. [Public examples and early evidence](attachments/native-harness-cost-findings.md) retain the original research comparison.

- Move forward with session-scoped usage capture and story attribution across Codex, Claude Code, and Grok Build. Use portable adapters around existing harness interfaces. Keep the receipt, assignment, deduplication and rollup rules in AITM.
- Headless capture worked on all three tested harnesses. Epic-trail tests reconciled sequential assignments, parallel and nested work, agent handoffs, and late attribution. Keep engaged agent time, working wall time, and elapsed time separate.
- Claude and Grok demonstrated two sealed review rounds, interrupted attempts, and idempotent receipt delivery. Codex remains a qualified usage source for observed turns and a coverage gap for sealed AIPR reviews on the tested route. Show reviewer and orchestrator usage separately.
- Report measured units, provider pricing indicators and labeled estimates with provenance. Per-story subscription charges remain unverified.
- For the later AIPR redesign, test a smaller reviewer interaction with an immutable attempt envelope, scoped join and submit authority, and independently settled usage receipts. Preserve native reviewer identity, ownership checks and fail-closed handling of ambiguity. Keep this qualification separate from the first cost-management slice.

Use this recommendation to reconcile scope with #100’s accepted plan. The research update changes no delivery commitments in #100.
