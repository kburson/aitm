# #83 agent usage evidence

Evidence observed through November 09, 2026 08:45:57 CST. Measured model-token usage and API-equivalent standard text estimates are separate from invoiced spend and subscription limits. Actual spend and attributable quota burn are Unknown.

| Work scope and participant | Observed tokens | API-equivalent USD | Unpriced records | Coverage gaps |
| --- | ---: | ---: | ---: | ---: |
| Builder check | 266,105 | $0.1270 | 0 | 0 |
| Design SPR | 611,312 | $0.2069 | 0 | 0 |
| Design XPR | 1,132,258 | $1.0917 | 0 | 0 |
| Design and plan coordinator | 32,789,051 | $7.7862 | 0 | 0 |
| Mixed #73 and #83 coordinator work | 4,092,966 | $0.5920 | 0 | 0 |
| Plan SPR | 1,795,173 | $0.4727 | 0 | 0 |
| Plan XPR | 1,873,902 | $1.8174 | 0 | 0 |
| Plan finalization and delivery coordinator | 9,751,449 | $2.3561 | 0 | 0 |

**Attributed #83 observed subtotal** 48,219,250 tokens and $13.8581 API-equivalent. The earlier mixed #73/#83 scope is kept separate. Rows with unpriced records report their priced subtotal.

The coordinator is scoped by observed cutoff, so any ambiguous boundary remains approximate. Codex repeated cumulative counters are deduplicated and reconciled to last-request values. Claude streamed usage is grouped by request. Prompt text, private handles, raw traces and personal account details stay local. Work after the observation cutoff and provider usage absent from the retained sources remain outside these figures.

[Rate basis and attribution methods from the #73 spike](../../73/attachments/report.md#how-the-figures-were-recovered). The estimate applies versioned public rates as a standard API comparison. It records known model usage without assigning a provider-wide quota delta to an agent.
