# #83 agent usage evidence

Evidence observed through November 09, 2026 09:04:21 CST. Measured model-token usage and API-equivalent standard text estimates are separate from invoiced spend and subscription limits. Actual spend and attributable quota burn are Unknown.

| Work scope and participant | Observed tokens | API-equivalent USD | Unpriced records | Coverage gaps |
| --- | ---: | ---: | ---: | ---: |
| Builder check | 266,105 | $0.1270 | 0 | 0 |
| Design SPR | 611,312 | $0.2069 | 0 | 0 |
| Design XPR | 1,132,258 | $1.0917 | 0 | 0 |
| Design and plan coordinator | 32,789,051 | $7.7862 | 0 | 0 |
| Mixed #73 and #83 coordinator work | 4,092,966 | $0.5920 | 0 | 0 |
| Plan SPR | 1,795,173 | $0.4727 | 0 | 0 |
| Plan XPR | 1,873,902 | $1.8174 | 0 | 0 |
| Plan finalization and delivery coordinator | 22,561,331 | $5.4179 | 0 | 0 |
| U01 implementation | 2,216,794 | $0.7378 | 0 | 0 |
| U01 source review | 941,927 | $0.2977 | 0 | 0 |

**Attributed #83 observed subtotal** 64,187,853 tokens and $17.9554 API-equivalent. The earlier mixed #73/#83 scope is kept separate. Rows with unpriced records report their priced subtotal.

The coordinator is scoped by observed cutoff, so any ambiguous boundary remains approximate. Codex repeated cumulative counters are deduplicated and reconciled to last-request values. Claude streamed usage is grouped by request. Prompt text, private handles, raw traces and personal account details stay local. Work after the observation cutoff and provider usage absent from the retained sources remain outside these figures.

[Rate basis and attribution methods from the #73 spike](../../73/attachments/report.md#how-the-figures-were-recovered). The estimate applies versioned public rates as a standard API comparison. It records known model usage without assigning a provider-wide quota delta to an agent.
