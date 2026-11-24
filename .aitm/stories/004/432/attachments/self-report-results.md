# #432 Per-turn self-reporting and story cost-log experiment

Observed on macOS on November 24, 2026. Three live, disposable, interactive sessions used Codex CLI 0.171.0-alpha.13 with ChatGPT sign-in, Claude Code 2.1.331 with Claude Pro, and Grok Build 1.0.92 with grok.com sign-in. The harnesses were instructed each turn. Autonomous triggering without a prompt was outside this sample.

## Method

For each provider, run an unrelated baseline (turn 1), three story work turns (2 through 4), and a reporting turn (5). In each next turn the active agent invokes a bounded local tool to query the previous completed turn of its own verified session. The driver supplies instructions and session identity where needed and supplies no measured values. It excludes the baseline, then repeats delivery of turn 4 and requests nonexistent turn 99. The tool-initiated measurement writes a normalized row in a disposable repository. The agent carries the entries in its answers, repeats them after resume and real compaction without calling tools, and reads the file from a fresh handoff chat. The test checked a missing measurement by replaying the same bounded tool separately and verifying the file was unchanged.

The verification recomputes the totals from native sources: Codex matched turn start/completion and cumulative-token differences, Claude followed provider-logged ancestry to the prompt and deduplicated request IDs, and Grok reread each turn using its native exact-turn command. Independent reconciliation compared every included story-work turn, the report, and the repo-log aggregate. Memory tests used a separate fresh chat and a disposable scope.

## Results

| Harness | Agent-initiated usage | Session context | Native harness memory | Repo-local log |
| --- | --- | --- | --- | --- |
| Codex | Passed. Local tool reads the agent's own exact rollout. A stale binding during setup correctly failed closed before the successful run. | Exact after resume and actual compaction. | Inconclusive. An isolated profile had no authenticated account. The documented store is profile-scoped and generated asynchronously. | Exact in a fresh handoff, with the replay counted once. |
| Claude Code | Passed. Local tool reads the active session’s own transcript. Per-turn values sum unique requests including the cache token categories. | Exact after resume and actual compaction. | Passed using a disposable native `autoMemoryDirectory`. The same session reread its stored entries. A fresh session recovered them without tools. A different story returned empty, and a different configured memory directory had no record. This proves the trial’s directory isolation, with no general per-story access control. | Exact in a fresh handoff, with the replay counted once. |
| Grok Build | Passed. Local tool calls native `grok usage` against the agent's own session. Native cost ticks were also available. | Exact after resume and actual compaction. | Inconclusive. The isolated Grok home could not authenticate. Its workspace memory documentation distinguishes global and workspace stores. An authenticated workspace-only write was not exercised on this installed build. | Exact in a fresh handoff, with the replay counted once. |

## Reconciliation and overhead

| Harness | Work turns 2 / 3 / 4 | Work subtotal | Reporting turn 5 | Total including report |
| --- | --- | ---: | ---: | ---: |
| Codex | 42,743 / 43,216 / 43,723 | 129,682 | 44,867 | 174,549 |
| Claude Code | 75,749 / 76,333 / 76,914 | 228,996 | 78,699 | 307,695 |
| Grok Build | 38,280 / 38,822 / 39,338 | 116,440 | 40,733 | 157,173 |

Values are native token counts or a sum of native input, output and cache categories for Claude. Cost ticks are in the receipt in their original units. No independently billed amount or cross-provider price comparison was verified. The baselines and all later recall, handoff, memory and settlement-control work are excluded. These short prompts exercised a real authenticated tool-assisted agent loop and included its context. They are not a production cost benchmark. Measuring a preceding turn used a shell call inside a substantive turn. Exact native traces show a tool loop for each ordinary capture. For Claude and Grok it produced two native requests or model calls per measured work turn versus one on the no-tool baseline. A separate reporting turn was used deliberately and its overhead is visible above.

The in-turn report contained the three settled work turns. The report's own turn can be added when its usage settles. Codex’s completion callback captured the exact reporting turn independently of any later inference. Claude’s first callback grouped the final pasted prompt into the previous turn. Exact native ancestry recovered turn 5 separately, and the corrected callback passed a later no-follow-up settlement control. Grok exposed turn 5 through a one-shot exact-turn measurement. This trial did not install a Grok completion callback.

## Disposition

The repo-local log is the only tested storage mechanism that gave all three harnesses exact deduplication and a fresh-agent handoff. Session context retained three records across one resume and one compaction per provider. Native Claude memory worked as an additional recall path in the isolated configuration. The two other memory cells remain inconclusive. A narrowly scoped tool running inside the active agent can capture completed turns, with the final reporting turn settled separately by a native completion route or exact-turn lookup. This evidence supports a repo-local record as the shared reference for future research, with context or native memory available for recall.

[Sanitized receipt](self-report-receipt.json) · [Codex local memories](https://learn.chatgpt.com/docs/customization/memories) · [Claude Code project memory](https://code.claude.com/docs/en/memory) · [Grok Build workspace memory](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/README.md#memory).
