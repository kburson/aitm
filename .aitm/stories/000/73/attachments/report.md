# Core review cost measurement spike

November 9, 2026 · [Spike #73](https://github.com/kburson/aitm/issues/73) · [Core #2](../../2/story.md) · [C44 / #51](../../51/story.md)

**Recovered $19.83 in API-equivalent token cost across the four participant records** from Core's implementation plan SPR and XPR. The two reviewer sessions can be priced from their retained model usage. The Codex author shared one session across phases, so the author costs use audited time and tool-action boundaries. Actual billed spend and task-level subscription burn remain unknown.

## Recovered model usage

| Review | Participant | Model / effort | Usage increments or requests | Uncached input | Cache reads | Cache writes | Output | API-equivalent USD |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SPR | Author, Codex | GPT-6 Astra / xhigh | 17 | 11,589 | 3,815,040 | 0 | 19,495 | $4.905680 |
| SPR | Reviewer, Codex | GPT-6.1 Sol / high | 31 | 164,654 | 3,494,912 | 0 | 12,790 | $0.806699 |
| XPR | Author, Codex | GPT-6 Astra / xhigh | 41 | 127,449 | 5,355,520 | 0 | 44,520 | $8.856010 |
| XPR | Reviewer, Claude Code | Claude Opus 5.5 / high | 45 | 90 | 8,545,714 | 294,663 | 59,787 | $5.262547 |

SPR totaled **$5.71** and XPR totaled **$14.12**. Combined observed volume was **21,946,223 tokens**, dominated by cache reads. Output includes the reported reasoning or thinking subset, which was 9,953, 2,424, 12,732 and 28,502 tokens respectively. The estimate counts that subset once.

The scope is the recorded implementation plan review pair. Earlier brainstorming, design review and SAR, post-publication cleanup, leaf creation and delivery are outside the totals. Two mixed author increments during the handoff between review phases were kept separate at **$0.51**. Four increments in the XPR author envelope also touched leaf administration. Removing those four drops that row to **$7.82** and the combined total to **$18.80**. This sensitivity check shows the effect of those specific mixed increments. Historical logs do not support finer allocation within a model request.

## How the figures were recovered

- **Codex identity and deduplication.** Match the SPR logs to the [portable manifest](../../2/plan/reviews/spr-2026-11-09-core-plan-manual/review-manifest.md) by session ID. The same author's session hashes to the openai participant fingerprint in the [native XPR record](../../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md). Use successive cumulative `token_count` differences, drop zero differences, and verify each positive increment against `last_token_usage`. Take model and effort from the retained turn context. Subtract cached input from total input for pricing. All included increments were below the 272K long-context threshold and reported zero cache writes.
- **Codex boundaries.** In UTC on November 9, the SPR author slice runs from the first SPR-only setup increment at `07:12:08.103` through the SPR publication increment at `07:27:51.117`. The dedicated SPR reviewer has two completed turns and its full 31-increment session is included. The XPR author slice runs from the XPR setup increment at `07:28:18.503` through the publication increment at `07:57:25.177`. These slices include coordination and publication work where observed. Earlier mixed SAR publication work and later archive handling are outside them. The author slices are qualified estimates of attribution within a shared session.
- **Claude identity and deduplication.** The retained reviewer session hashes to the anthropic participant fingerprint in the native XPR record using ai-peer-review's provider-qualified session fingerprint. The transcript has 92 usage-bearing assistant rows for 45 distinct request and message pairs. Input categories stayed constant within each pair and output counts were nondecreasing. Retaining the last row for each pair reconciled the request-derived token totals and computed USD with all five of the CLI's cumulative cost checkpoints. All 294,663 cache-write tokens had one-hour TTL. The rows record standard speed and global inference. The local CLI's final `totalCostUSD` was approximately **$5.262547** and agreed with the independent estimate.
- **Rate basis.** Standard public text API rates in USD per million tokens, checked November 9, 2026. Astra uncached/cache-read/output rates were $10/$1/$50, Sol $2/$0.10/$10, and Opus $4/$0.20/$20 with $5 five-minute and $8 one-hour writes. Effort is retained for analysis. The rate calculation uses observed token categories, including thinking within output. This is a reproducible list-price comparison under Standard API processing. The source logs cannot establish coverage of every upstream attempt or separate charges outside the observed model usage. [Astra pricing](https://developers.openai.com/api/docs/models/gpt-6-astra#pricing) · [Sol pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol#pricing) · [OpenAI reasoning tokens](https://developers.openai.com/api/docs/guides/reasoning#how-reasoning-works) · [Opus pricing](https://platform.claude.com/docs/en/models/opus-5-5/overview#pricing)

## Actual spend and subscription limits

| Provider | Actual billed USD | Subscription evidence |
| --- | --- | --- |
| OpenAI | Unknown. The credit balance snapshot was stable across the author slices. A balance snapshot alone cannot reconcile charges. | One seven-day Codex bucket was retained. The SPR author saw the account reading rise by **1 percentage point** within the same reset window. The SPR reviewer and XPR author each saw a flat reading while their usage counters rose. Account-level updates, sampling cadence and overlapping work prevent assigning a task or role a quota delta. |
| Anthropic | Unknown. Claude Code's recorded cost agrees with public token pricing. The recovered evidence establishes an estimate. | No weekly or other subscription-limit readings were retained in the reviewer transcript. Claude Code documents conditional five-hour and seven-day status-line fields, which future runs would need to capture separately. |

Neither provider record exposes a monthly subscription allowance for these runs. We can bucket observed task usage by calendar month. A monthly share requires the provider's actual denominator. The experiment used historical evidence. It did not perform a fresh isolated quota test or retrieve account billing records. [Codex rate limit schema](https://learn.chatgpt.com/docs/app-server#6-rate-limits-chatgpt) · [Claude Code quota fields](https://code.claude.com/docs/en/statusline#rate-limit-usage) · [Claude Code estimated request cost](https://code.claude.com/docs/en/monitoring-usage#api-request-event)

The review manifests also yield response timing. From the first recorded response start to the last submission, SPR spanned **15m 09s** and XPR **24m 57s**. XPR includes claim and prior-submission time proxies. These spans can contain waiting and exclude work outside the recorded bounds. Continuous agent engagement is unknown.

## What AITM should capture

1. Bind each agent to a draft or task, phase, attempt, review level, round and role before work starts. Carry the draft identity through issue graduation. Preserve actual provider/model, effective effort, speed and account alias. In a mixed-purpose session, keep unallocated usage visible. Give child agents their own bindings and avoid adding child usage again if a parent counter already includes it.
2. Retain normalized usage and provenance with a deduplication key per request or cumulative-counter epoch. Keep raw transcripts and account identifiers local. Record billing evidence, subscription bucket observations and their observation times, and versioned pricing as separate data. Report provider/account/window quota independently, with task attribution only where the evidence supports it.
3. Roll a feature up from its own work and each unique descendant. Preserve unsuccessful attempts, incomplete capture and shared-work allocation explicitly. For Buy a Feature, show measured API-equivalent planning cost and a range for remaining delivery cost, with coverage and assumptions. Core's 220.5-hour implementation estimate cannot be converted into a credible dollar forecast from two planning reviews alone. [Core planning estimate](../../2/story.md#accepted-implementation-decomposition)
4. Use C44's [planned ingestion and reporting seam](../../2/plan/core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes) for normalized usage. Have the harness adapters prove collection on the actual surfaces used for reviews, including retries, model changes, subprocesses and overlapping quota usage. Verify per-task attribution before treating data as forecast calibration.

The spike deliverable is this report. The analysis code is disposable.
