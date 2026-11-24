---
schema: "aitm.story/v0"
id: 432
title: "[Spike] Self-report per-turn agent usage and retain a story cost log"
kind: "spike"
state: "review"
issue: "https://github.com/kburson/aitm/issues/432"
parent: 426
children: []
blocking: [429]
blocked-by: [428]
created: "2026-11-24T18:31:30Z"
updated: "2026-11-24T18:46:40Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/2026-11-24-codex-self-query-pilot.json", "attachments/self-report-results.md", "attachments/self-report-receipt.json", "attachments/independent-evidence-review.md"]}
expansions: []
trips: []
---

# [Spike] Self-report per-turn agent usage and retain a story cost log

[GitHub issue #432](https://github.com/kburson/aitm/issues/432)

Research parent: #426. Builds on the interactive and exact-session evidence from #427 and #428, before #429's headless comparison.

## Question

Can the active agent read its own completed-turn usage, keep a story-scoped log across turns, and compute an auditable total at story close? Which storage mechanisms preserve the log when the session resumes, context compacts, or the agent hands off the story?

## Test the reporting boundary

Use disposable interactive sessions on Codex, Claude Code, and Grok Build. Start with one unrelated turn, then assign a story and run at least three known turns. On each subsequent turn, have the active agent invoke a provider-supported command or tool against its own verified session to read the previous completed turn. An in-session tool can read native evidence. Use a separate ground-truth lookup only to verify what the active agent reported. An externally supplied counter or an automatic callback does not prove agent-initiated self-reporting. Record the exact surfaces, whether any operator action is needed, and whether a position in the session can be bound to the right story and turn.

At story close, have the agent aggregate the settled entries. Verify whether its closeout turn can be finalized by its own harness and incorporated without another model turn. Record any coverage gap for the reporting turn or other late usage that never settles. Measure any tool or extra model turns required for capture.

## Compare three ways to store the same entries

1. **Session context.** Maintain a structured log through the conversation. Test exact recall at the next turn, after stopping and resuming the same session, and after actual compaction if supported. Check whether the agent can distinguish retained records from reconstructed values.
2. **Harness memory.** Try a supported writable, project-scoped memory mechanism in an isolated disposable project. Verify readback from the same session and a fresh session for the same story. Exercise a different story as a negative control. Record unsupported surfaces or unavailable memory operations. Keep user-wide memory and unrelated project memory outside this trial.
3. **Repo-local file.** Have the active agent append sanitized structured per-turn records to a disposable repository's local log, with one stable key per story/run/session/turn. Read it back after resume and from a handoff session. Verify deterministic aggregation and deduplication when one turn is delivered twice. Keep raw provider identifiers, prompt text, and credentials out of the log.

## Evidence and decision

For each provider and storage mechanism, independently reconcile the agent-reported records against the same native evidence, including the final turn where it settles. Exercise an unavailable measurement, a duplicate, and an unrelated baseline. Keep measured usage units, native cost indicators, API-equivalent estimates, and coverage gaps distinct. Record exact recovery and handoff results, operational overhead, and the smallest supported mechanism. Use bounded inconclusive results where compaction, project memory, or a self-query interface cannot be demonstrated. Deliver a three-provider comparison and an end-of-story total that can be reproduced without counting a turn twice.

## Initial pilot

The active Codex Desktop agent invoked a local tool against its own exact session and recovered its previous completed turn's token delta, excluding the ongoing turn. A disposable Git workspace log contained two copies of one entry. A fresh process counted it once and reproduced the measured total. This pilot covers one previous completed turn and repo-local readback. It leaves the full test matrix open. [Sanitized pilot receipt](attachments/2026-11-24-codex-self-query-pilot.json).

## Results

[Findings](attachments/self-report-results.md) · [Sanitized receipt](attachments/self-report-receipt.json) · [Independent evidence review](attachments/independent-evidence-review.md).
