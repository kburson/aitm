# Native harness usage and cost research findings

## Demonstrated so far

- [#427 interactive capture](../../427/attachments/interactive-results.md) obtained usage for assigned turns from a configured Codex TUI completion callback and exact rollout lookup, a Claude Code Stop callback with transcript settlement, and Grok Build's exact-session/turn usage command. Arbitrary already-open chat attachment and autonomous enrollment remain unproven. The workload covered the root agent only.
- [#428 delayed recovery](../../428/attachments/retrospective-results.md) recovered exact local observations on all three tested surfaces after closure and resume. Codex required retained rollout counters and exact turn IDs, Claude required native request identity and parent links, and Grok returned native per-turn usage and cost ticks. The artifacts can recover usage by identity, while story ownership requires a retained assignment boundary. Long-term retention and remote lookup were outside the trial.
- [#432 self-report and handoff](../../432/attachments/self-report-results.md) demonstrated agent-initiated capture of a prior completed turn and exact deduplication and fresh-agent handoff through a repo-local log across all three harnesses. A dedicated reporting turn added about 34–35% of the measured work-turn token subtotal in those short trials. The in-turn tool call also added model requests in sampled Claude and Grok work turns. Prefer a native completion event or one-shot exact lookup outside the model loop where available. Keep agent-initiated capture as a fallback. These trials did not verify billed dollars or actual headless XPR coverage.

## Public examples and transferable tactics

| Example | Tactic to test in #426 |
| --- | --- |
| [Paperclip Costs API](https://docs.paperclip.ing/reference/api/costs/) | Bind a usage event to both a work item and an execution identity. Preserve pricing provenance and unknown price. Keep assignment durable across handoffs and reassignment. |
| [OpenCode Swarm delegation accounting](https://github.com/ZaxbyHub/opencode-swarm/pull/1557) and [commands](https://github.com/ZaxbyHub/opencode-swarm/blob/main/docs/commands.md#swarm-costs) | Account for each delegation and attempt, including failed attempts where evidence exists. Keep review, rework and orchestrator contributions visible. |
| [Cursor SDK usage](https://cursor.com/docs/sdk/typescript#agentgetusage) | Correlate the work result and delayed cost by identity. Declare the measurement's coverage, especially whether a native aggregate includes subagents or side chats. |
| [Claude Code telemetry](https://code.claude.com/docs/en/monitoring-usage#cost-counter), [Token Cost](https://github.com/peiris/token-cost#how-the-numbers-are-produced), and [Gaia skill-cost](https://github.com/gaia-research/skill-cost#run-reports-separate-measured-tokens-from-estimates) | Prefer native identifiers, deduplicate request observations, retain cache categories and report incomplete coverage. Native skill and role tags can aid diagnosis. Subscription API-equivalent estimates need their own provenance. |
| [SkillsBench](https://arxiv.org/html/2602.12670v4#A12) and [FinOps Foundation](https://www.finops.org/wg/finops-for-ai-overview/#kpis-and-metrics) | Pair task cost with outcome and include retry and rework costs when comparing cost per accepted result. |

## Candidate boundary

Keep each provider's native harness as the interactive and headless execution surface. Keep adapters small and session-scoped. An adapter captures structured native evidence or performs an exact lookup, records its coverage and exits. AITM owns assignment identity, provenance and rollup. AIPR can attach a usage receipt to the existing XPR result, including a separately correlated completion when the usage settles later. The same receipt should work for single-provider and cross-provider delivery.

Evaluate reuse of the existing usage package's types, scope markers, pricing and rollups independently of the monitor lifecycle. Prefer a common receipt and adapter contract grounded in the remaining spike evidence. If exposed over MCP, use narrow typed operations and enforce scope in the backing tools and credentials. Treat raw transcript access as a narrowly scoped adapter capability. Keep raw evidence private and retain sanitized references.

These are research inputs. Revisit the #100 delivery decision after #426 completes its spikes and presents the measured coverage and tradeoffs.
