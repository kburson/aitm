# #83 agent usage evidence

Evidence observed through November 09, 2026 11:27:24 CST. Measured model-token usage and API-equivalent standard text estimates are separate from invoiced spend and subscription limits. Actual spend and attributable quota burn are Unknown.

| Work scope and participant | Observed model / effort | Observed tokens | API-equivalent USD | Unpriced records | Coverage gaps |
| --- | --- | ---: | ---: | ---: | ---: |
| Builder check | gpt-6.1-sol / high | 266,105 | $0.1270 | 0 | 0 |
| Design SPR | gpt-6.1-sol / high | 611,312 | $0.2069 | 0 | 0 |
| Design XPR | claude-opus-5-5 / high | 1,132,258 | $1.0917 | 0 | 0 |
| Design and plan coordinator | gpt-6.1-sol / high | 32,789,051 | $7.7862 | 0 | 0 |
| Implementation and delivery coordinator | gpt-6.1-sol / high | 72,619,337 | $13.5921 | 0 | 0 |
| Mixed #73 and #83 coordinator work | gpt-6.1-sol / high | 4,092,966 | $0.5920 | 0 | 0 |
| Plan SPR | gpt-6.1-sol / high | 1,197,965 | $0.3542 | 0 | 0 |
| Plan XPR | claude-opus-5-5 / high | 1,873,902 | $1.8174 | 0 | 0 |
| Plan finalization and delivery coordinator | gpt-6.1-sol / high | 22,143,186 | $5.3197 | 0 | 0 |
| Relationship amendment SPR | gpt-6.1-sol / high | 1,786,331 | $0.2671 | 0 | 0 |
| Relationship amendment XPR | claude-opus-5-5 / high | 1,914,869 | $2.1190 | 0 | 0 |
| Relationship amendment coordinator | gpt-6.1-sol / high | 8,651,385 | $1.4852 | 0 | 0 |
| Replan SPR | gpt-6.1-sol / high | 1,741,411 | $0.3267 | 0 | 0 |
| Replan XPR | claude-opus-5-5 / high | 1,547,243 | $2.0892 | 0 | 0 |
| Replan coordinator | gpt-6.1-sol / high | 7,899,731 | $1.3052 | 0 | 0 |
| U01 implementation | gpt-6.1-sol / high | 7,037,303 | $1.7579 | 0 | 0 |
| U01 pickup review | gpt-6.1-sol / high | 597,208 | $0.1186 | 0 | 0 |
| U01 source review | gpt-6.1-sol / high | 3,738,517 | $0.7955 | 0 | 0 |
| U02 implementation | gpt-6.1-sol / high | 9,746,915 | $1.9942 | 0 | 0 |
| U02 pickup review | gpt-6.1-sol / high | 1,183,551 | $0.2169 | 0 | 0 |
| U02 source review | gpt-6.1-sol / high | 2,331,650 | $0.5824 | 0 | 0 |
| U03 Claude sideband pickup review | gpt-6.1-sol / high | 1,464,772 | $0.3651 | 0 | 0 |
| U03 implementation | gpt-6.1-sol / high | 9,515,298 | $1.9222 | 0 | 0 |
| U03 pickup review | gpt-6.1-sol / high | 1,225,550 | $0.1931 | 0 | 0 |
| U03 source review | gpt-6.1-sol / high | 2,696,508 | $0.6229 | 0 | 0 |
| U04 implementation | gpt-6.1-sol / high | 2,994,615 | $0.7604 | 0 | 0 |
| U04 pickup review | gpt-6.1-sol / high | 2,739,300 | $0.6307 | 0 | 0 |
| U13 implementation | gpt-6.1-sol / high | 7,268,418 | $1.5609 | 0 | 0 |
| U13 pickup review | gpt-6.1-sol / high | 1,189,657 | $0.2055 | 0 | 0 |
| U13 source review | gpt-6.1-sol / high | 2,621,623 | $0.6105 | 0 | 0 |

**Attributed #83 observed subtotal** 212,524,971 tokens and $50.2246 API-equivalent. The earlier mixed #73/#83 scope is kept separate. Rows with unpriced records report their priced subtotal. Effort is observed context and standard API pricing uses the model and token categories.

The coordinator is scoped by observed cutoff, so any ambiguous boundary remains approximate. Codex repeated cumulative counters are deduplicated and reconciled to last-request values. Claude streamed usage is grouped by request. Prompt text, private handles, raw traces and personal account details stay local. Work after the observation cutoff and provider usage absent from the retained sources remain outside these figures.

[Rate basis and attribution methods from the #73 spike](../../73/attachments/report.md#how-the-figures-were-recovered). The estimate applies versioned public rates as a standard API comparison. It records known model usage without assigning a provider-wide quota delta to an agent.
