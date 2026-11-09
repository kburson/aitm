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

Neither provider record exposes a monthly subscription allowance for these runs. We can bucket observed task usage by calendar month. A monthly share requires the provider's actual denominator. These retrospective figures use historical evidence. The live follow-up below samples subscription readings separately. Invoiced spend remains unknown. [Codex rate limit schema](https://learn.chatgpt.com/docs/app-server#6-rate-limits-chatgpt) · [Claude Code quota fields](https://code.claude.com/docs/en/statusline#rate-limit-usage) · [Claude Code estimated request cost](https://code.claude.com/docs/en/monitoring-usage#api-request-event)

The review manifests also yield response timing. From the first recorded response start to the last submission, SPR spanned **15m 09s** and XPR **24m 57s**. XPR includes claim and prior-submission time proxies. These spans can contain waiting and exclude work outside the recorded bounds. Continuous agent engagement is unknown.

## Live follow-up on subscription limits

November 9, 2026, Central Standard Time. Codex CLI 0.167.0-alpha.3.2 used ChatGPT sign-in. Claude Code 2.1.318 used Claude subscription sign-in. The test used the existing subscriptions and five disposable model calls with tools disabled or unused. The probes requested GPT-6 Astra and used Claude Opus 5.5, with low effort and a fixed synthetic output task. The original probes requested 100 lines and a shorter Codex repeat requested 20.

### The live XPR

I observed the separate [Core plan full-file validation XPR](../../2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/review-manifest.md) from about 7:20 to 7:36 a.m. without intervening in the review. Both local participant records matched the review's provider-qualified fingerprints. This is an observation slice of that validation and is separate from the retrospective dollar total above.

| Live participant | Observed model usage in the slice | Subscription evidence |
| --- | --- | --- |
| Codex author, GPT-6 Astra / xhigh | 31 positive counter increments, 3,223,717 tokens | The inline seven-day account reading moved from 5% to 6% in one reset window. The account endpoint then returned 6% on all 21 polls from 7:33:32 to 7:37:01 a.m. |
| Claude Code reviewer, Opus 5.5 / high | 47 distinct requests, 8,079,952 tokens | The retained reviewer transcript contained request usage but no subscription readings. Account-level Claude readings were available from a separate CLI process. |

Thirteen Codex token observations fell between the recorded start and last usage row of a matched Claude request. This establishes overlapping observed work across the two providers. The Codex account change lacks a per-request attribution key. The separate Claude account readings lack a historical baseline for the review and cannot isolate that reviewer.

### Controlled probes

Before and after each trial, I read Codex's `account/rateLimits/read` and ran Claude Code's local `/usage` command through print-mode JSON. The Claude result counters for those snapshots reported zero input, cache and output tokens. I checked reset-window identity and repeated the account reads 12 seconds after the overlap. The controlled model calls reported the following token totals, including cached input.

| Trial | Per-agent usage | What the account readings showed |
| --- | --- | --- |
| Serial Codex | 19,089 tokens | Codex stayed at 6% weekly. The XPR author and the measurement chat also recorded Codex usage during the trial. |
| Serial Claude Code | 4,647 tokens | Claude's `/usage` display stayed at 68% in the five-hour window and 21% in the seven-day window. The monitored reviewer logged no requests during this probe. |
| Concurrent Codex and Claude Code | Codex 17,567 tokens, Claude 4,647 tokens | About 15 seconds of Claude response streaming overlapped an open Codex turn. Both account displays held at their preceding readings, including the delayed check. Neither XPR participant recorded usage inside the probe interval. |
| Short serial Codex repeat | 18,118 tokens | Codex stayed at 6% weekly. The monitored XPR author had two usage increments within the full before-to-delayed-check bracket, so the repeat also lacked a clean Codex baseline. |

The serial runs isolated the probes from each other. The live author and measurement chat prevented verified same-account isolation for the serial Codex trials. Two subsequent waits for a 35-second quiet period in the monitored logs expired without launching another request. Other devices and unmonitored sessions were outside the observation. The cross-provider overlap kept the two subscription readings separate, with no concurrent usage observed in the monitored XPR logs during the model calls.

The standalone Claude model calls also emitted a session-associated `rate_limit_event` after each response. In this version the payload exposed account window utilization and reset timestamps. It reported five-hour utilization of **67%** in the serial probe and **68%** in the concurrent probe, with **20%** weekly both times. The surrounding `/usage` displays read **68% / 21%** for the same reset windows. The display later moved to **69% / 21%** before the short Codex repeat, between Claude probe calls. The spike could not distinguish update lag from differences in how the two surfaces report utilization. Both events reported `isUsingOverage: false`. The overage reset field provided neither a monthly included-use reading nor a billing receipt. [Codex App Server rate limits](https://learn.chatgpt.com/docs/app-server#6-rate-limits-chatgpt) · [Claude Code stream event and local command reference](https://code.claude.com/docs/en/agent-sdk/typescript#sdkratelimitevent) · [Claude Code status-line rate limits](https://code.claude.com/docs/en/statusline#rate-limit-usage)

### Codex-only rerun after the author went idle

On November 9, 2026, the Codex app reported the XPR author's turn complete at 7:57:33 a.m. CST. The collector waited for the author and measurement logs to be quiet for at least 35 seconds and took two agreeing baseline reads. It then ran the same 100-line Codex-only task through the subscription path, requesting GPT-6 Astra at low effort. The probe recorded **19,078 tokens**, including 17,874 input tokens (12,160 cached) and 1,204 output tokens.

| Observation | Time (CST) | Codex seven-day reading |
| --- | --- | ---: |
| Baseline 1 | 7:58:43 a.m. | 7% |
| Baseline 2 | 7:58:52 a.m. | 7% |
| About 2 seconds after turn completion | 7:59:21 a.m. | 7% |
| About 15 seconds after turn completion | 7:59:34 a.m. | 7% |
| About 51 seconds after turn completion | 8:00:10 a.m. | 7% |

All five readings reported the same reset. The author remained idle through the immediate check, and the monitored local Codex logs showed no other positive usage increments during that bracket. The author's new turn began at 7:59:28 a.m. and produced two increments during the delayed observation bracket. Other devices and unmonitored sessions were outside the observation.

**The locally quiet bracket showed zero percentage-point movement at the available precision.** It yielded no usable per-agent quota delta. The delayed readings were also flat, with concurrent activity by that point. The result leaves the probe's actual share of the weekly allowance unknown.

### What the spike establishes

AITM can tie observed model usage to individual agents, even during XPR overlap. The subscription APIs and CLI surfaces tested return **account-window observations**. A session-associated event tells us where the observation was seen. It does not identify how much that session contributed to the account window. Flat readings leave a small probe's burn unresolved. Changes during concurrent same-provider work are shared account movements. Cross-provider overlap can be reported as two separate observations, one per provider and reset window. Actual billed spend remained unverified.

For capture, keep the agent's model usage and the quota observation as separate records. Store the provider, account alias, bucket, reset, observation source and timestamp. For Codex, use the account endpoint and retain inline observations where available. For Claude Code, capture structured rate-limit events when the launch surface emits them, or sample the local `/usage` command. Label a same-window delta from a verified isolated test as an observed account change at the available display precision. In ordinary operation, mark per-agent quota attribution unknown and preserve API-equivalent USD for the feature rollup.

## What AITM should capture

1. Bind each agent to a draft or task, phase, attempt, review level, round and role before work starts. Carry the draft identity through issue graduation. Preserve actual provider/model, effective effort, speed and account alias. In a mixed-purpose session, keep unallocated usage visible. Give child agents their own bindings and avoid adding child usage again if a parent counter already includes it.
2. Retain normalized usage and provenance with a deduplication key per request or cumulative-counter epoch. Keep raw transcripts and account identifiers local. Record billing evidence, subscription bucket observations and their observation times, and versioned pricing as separate data. Report provider/account/window quota independently, with task attribution only where the evidence supports it.
3. Roll a feature up from its own work and each unique descendant. Preserve unsuccessful attempts, incomplete capture and shared-work allocation explicitly. For Buy a Feature, show measured API-equivalent planning cost and a range for remaining delivery cost, with coverage and assumptions. Core's 220.5-hour implementation estimate cannot be converted into a credible dollar forecast from two planning reviews alone. [Core planning estimate](../../2/story.md#accepted-implementation-decomposition)
4. Use C44's [planned ingestion and reporting seam](../../2/plan/core-implementation-plan.md#c44-estimate-lineage-usage-and-learning-outcomes) for normalized usage. Have the harness adapters prove collection on the actual surfaces used for reviews, including retries, model changes, subprocesses and overlapping quota usage. Verify per-task attribution before treating data as forecast calibration.

The spike deliverable is this report. The analysis code is disposable.
