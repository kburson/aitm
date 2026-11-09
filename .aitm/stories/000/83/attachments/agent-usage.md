# #83 agent usage evidence

Evidence observed through November 09, 2026 09:35:15 CST. Measured model-token usage and API-equivalent standard text estimates are separate from invoiced spend and subscription limits. Actual spend and attributable quota burn are Unknown.

| Work scope and participant | Observed tokens | API-equivalent USD | Unpriced records | Coverage gaps |
| --- | ---: | ---: | ---: | ---: |
| Builder check | 266,105 | $0.1270 | 0 | 0 |
| Design SPR | 611,312 | $0.2069 | 0 | 0 |
| Design XPR | 1,132,258 | $1.0917 | 0 | 0 |
| Design and plan coordinator | 32,789,051 | $7.7862 | 0 | 0 |
| Mixed #73 and #83 coordinator work | 4,092,966 | $0.5920 | 0 | 0 |
| Plan SPR | 1,197,965 | $0.3542 | 0 | 0 |
| Plan XPR | 1,873,902 | $1.8174 | 0 | 0 |
| Plan finalization and delivery coordinator | 22,143,186 | $5.3197 | 0 | 0 |
| Replan SPR | 2,053,941 | $0.3920 | 0 | 0 |
| Replan XPR | 1,547,243 | $2.0892 | 0 | 0 |
| Replan coordinator | 14,321,528 | $2.1562 | 0 | 0 |
| U01 implementation | 7,037,303 | $1.7579 | 0 | 0 |
| U01 pickup review | 597,208 | $0.1186 | 0 | 0 |
| U01 source review | 3,738,517 | $0.7955 | 0 | 0 |

**Attributed #83 observed subtotal** 89,309,519 tokens and $24.0126 API-equivalent. The earlier mixed #73/#83 scope is kept separate. Rows with unpriced records report their priced subtotal.

The coordinator is scoped by observed cutoff, so any ambiguous boundary remains approximate. Codex repeated cumulative counters are deduplicated and reconciled to last-request values. Claude streamed usage is grouped by request. Prompt text, private handles, raw traces and personal account details stay local. Work after the observation cutoff and provider usage absent from the retained sources remain outside these figures.

[Rate basis and attribution methods from the #73 spike](../../73/attachments/report.md#how-the-figures-were-recovered). The estimate applies versioned public rates as a standard API comparison. It records known model usage without assigning a provider-wide quota delta to an agent.
