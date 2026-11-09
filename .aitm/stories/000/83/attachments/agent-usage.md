# #83 agent usage evidence

Evidence observed through November 09, 2026 10:36:15 CST. Measured model-token usage and API-equivalent standard text estimates are separate from invoiced spend and subscription limits. Actual spend and attributable quota burn are Unknown.

| Work scope and participant | Observed model / effort | Observed tokens | API-equivalent USD | Unpriced records | Coverage gaps |
| --- | --- | ---: | ---: | ---: | ---: |
| Builder check | gpt-6.1-sol / high | 266,105 | $0.1270 | 0 | 0 |
| Design SPR | gpt-6.1-sol / high | 611,312 | $0.2069 | 0 | 0 |
| Design XPR | claude-opus-5-5 / high | 1,132,258 | $1.0917 | 0 | 0 |
| Design and plan coordinator | gpt-6.1-sol / high | 32,789,051 | $7.7862 | 0 | 0 |
| Implementation and delivery coordinator | gpt-6.1-sol / high | 39,487,055 | $5.3712 | 0 | 0 |
| Mixed #73 and #83 coordinator work | gpt-6.1-sol / high | 4,092,966 | $0.5920 | 0 | 0 |
| Plan SPR | gpt-6.1-sol / high | 1,197,965 | $0.3542 | 0 | 0 |
| Plan XPR | claude-opus-5-5 / high | 3,788,771 | $3.9364 | 0 | 0 |
| Plan finalization and delivery coordinator | gpt-6.1-sol / high | 22,143,186 | $5.3197 | 0 | 0 |
| Replan SPR | gpt-6.1-sol / high | 1,741,411 | $0.3267 | 0 | 0 |
| Replan XPR | claude-opus-5-5 / high | 1,547,243 | $2.0892 | 0 | 0 |
| Replan coordinator | gpt-6.1-sol / high | 7,899,731 | $1.3052 | 0 | 0 |
| U01 implementation | gpt-6.1-sol / high | 7,037,303 | $1.7579 | 0 | 0 |
| U01 pickup review | gpt-6.1-sol / high | 597,208 | $0.1186 | 0 | 0 |
| U01 source review | gpt-6.1-sol / high | 3,738,517 | $0.7955 | 0 | 0 |
| U02 implementation | gpt-6.1-sol / high | 9,746,915 | $1.9942 | 0 | 0 |
| U02 pickup review | gpt-6.1-sol / high | 1,183,551 | $0.2169 | 0 | 0 |
| U02 source review | gpt-6.1-sol / high | 2,331,650 | $0.5824 | 0 | 0 |
| U13 implementation | gpt-6.1-sol / high | 3,090,956 | $0.7513 | 0 | 0 |
| U13 pickup review | gpt-6.1-sol / high | 2,975,988 | $0.4726 | 0 | 0 |
| U13 source review | gpt-6.1-sol / high | 1,586,321 | $0.4150 | 0 | 0 |

**Attributed #83 observed subtotal** 144,892,497 tokens and $35.0190 API-equivalent. The earlier mixed #73/#83 scope is kept separate. Rows with unpriced records report their priced subtotal. Effort is observed context and standard API pricing uses the model and token categories.

The coordinator is scoped by observed cutoff, so any ambiguous boundary remains approximate. Codex repeated cumulative counters are deduplicated and reconciled to last-request values. Claude streamed usage is grouped by request. Prompt text, private handles, raw traces and personal account details stay local. Work after the observation cutoff and provider usage absent from the retained sources remain outside these figures.

[Rate basis and attribution methods from the #73 spike](../../73/attachments/report.md#how-the-figures-were-recovered). The estimate applies versioned public rates as a standard API comparison. It records known model usage without assigning a provider-wide quota delta to an agent.
