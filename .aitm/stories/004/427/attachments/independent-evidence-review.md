# #427 independent evidence review

2026-11-24. Reviewer model `claude-sonnet-5-5`, launched in a separate headless Claude Code session. Route is off-platform evidence inspection. The payload was the full sanitized report and JSON receipt.

## Round one

Report SHA-256 `6b1ab355ba7e38f35a3995ec4fb2a4a129d4229b869c9fa9812bb1620949a13c` and receipt SHA-256 `1076b16b88aa59d9e6d1077b494c8558fca38b8dc8173520a8ae8f4d0c65b89a`. A separate headless Grok review of this earlier pair returned **PASS**.

HOLD

**Numeric consistency.** Codex totals check out: 25,058+11 = 25,069 and 25,112+11 = 25,123, with the baseline 25,015 excluded as stated. Grok totals for turns 2 and 3 (18,902; 19,015) and ticks (34,979,200; 34,102,000) match the receipt, and input+output = total. Reasoning tokens appear to be included in output, which is not stated. Claude's receipt holds per-request observations but no per-turn totals or summed figure. The cumulative counts 1, 2, 3 are supported, but the claim that the final assigned turn was included rests on the count only. The 55 cache-creation delta in the third observation is plausible but not tied to a prompt. The write-up gives no Claude token conclusion, which is acceptable, but the Claude surface is not comparable to the others.

**Attribution and surfaces.** The receipt doesn't contradict the text claims that Codex used a callback plus a retained rollout, and that Grok used `grok usage <session> <turn>`. However, the Codex receipt shows only callback metadata and settled usage, with no rollout path, turn-ID match record, or "single matching" evidence. The Codex "initial_observation_counts" of 0,0,0 is unexplained. The Claude "armed: false" on turn 1 and "armed: true" on turns 2 and 3 match the described enrollment. In the Claude receipt, the first synchronous run (counts 0,1,2) and the settled run (1,2,3) appear to be different sessions, but the "settled" observations in the receipt show identical turn-1 and turn-2 values across them. Session identity isn't shown, so the claim that these are separate sessions rests on prose. Timestamps differ by about 2 minutes between Grok and the others, so Grok ran separately, which is consistent with the prose.

**Final-turn timing and enrollment.** Claude's settle result is the clearest support: the final Stop saw 3 observations after a one-second wait. This is correctly limited to one sample. For Codex, the final turn at 15:33:15 has settled usage, which supports final-turn capture, but the settle latency isn't reported. For Grok, the driver queries after each answer; no hook evidence exists, and the write-up says so. Externally driven enrollment ("armed" set by the driver) is consistent, and the limitation on self-enrollment is explicit.

**Retained usage vs. billed cost.** The write-up correctly says no billed dollar amount was verified. "costUsdTicks" is a native indicator only. No conversion of ticks to dollars is given, which is appropriate. Claude Pro and ChatGPT sign-in are subscription-based, so token counts there are not cost evidence either. Grok's turn-1 cost (118,211,200) is 3.4x turn 2 with far less cache read, which suggests cache effects but isn't analyzed.

**Why HOLD.** The conclusions are mostly bounded and honest, but the receipt lacks the evidence for a few specific claims: Codex rollout matching and the 3/3 terminal usage claim (only the callbacks are shown), session separation for the two Claude runs, and the 0,0,0 initial Codex counts. Also, the "Grok updated mid-run" note and the use of a disposable directory versus the trusted workspace for Claude introduce configuration differences that aren't reflected in the receipt. Adding the rollout match identifiers, session IDs per run, and the settle latency would move this to PASS. Residual limits already stated (no dynamic callback install, no self-enrollment, no delegation coverage, no billed verification, one sequential Claude sample) are fair and should stay.

## Round two

Report SHA-256 `4e1f185394cd6333cd88a4c50be074948f274f52e93b820ba370aa6eb39ddf1d` and receipt SHA-256 `66d2b477f8ad93bbf35f205568bc8ca9bfaf3fb8bbc64d8ed80f1c2f15296b83`. Revised evidence supplies pseudonymous identities, native parent or turn links, the controlled assignment boundary and the raw cumulative counter basis where applicable.

**PASS**

I checked the text against the receipt and found no blocking inconsistencies.

**Identity**
- Codex: the second run ties the callback's thread and turn IDs to a single retained rollout (`source_matches: 1`, `source_session_match: true`). Start and completion refs are pseudonymous and differ per turn.
- Claude: the async session ref (`a8ff…`) is distinct from the synchronous one (`dae4…`). Each turn resolves its prompt ref to the native parent ref, so the binding matches the text's "serial order" caveat.
- Grok: one live session ref, version 1.0.92, model `grok-4.7-build` on every turn.

**Assignment boundaries**
- All three providers mark turn 1 `unassigned-baseline` and turns 2 and 3 `assigned`.
- Codex and Claude callbacks show `armed: false, true, true`, which matches arming after turn 1.
- Baseline values are excluded from the assigned figures.

**Arithmetic**
- Codex:
  - Per turn, input plus output equals total (25,004+11=25,015; 25,058+11=25,069; 25,112+11=25,123).
  - Cumulative totals reconcile with the per-turn "last" values (25,015+25,069=50,084; +25,123=75,207).
  - Cached and input sums also reconcile.
  - The stated timings of 27, 27 and 34 ms match the receipt timestamps (27.2, 26.8 and 34.1 ms).
- Claude: observation counts are 0/1/2 for the synchronous run and 1/2/3 for the async run. The async callback usage matches the retained per-request usage exactly.
- Grok:
  - Per turn, input plus output equals total (18,638+126, 18,821+81, 18,959+56).
  - The stated turn 2 and 3 totals (18,902 and 19,015) and ticks (34,979,200 and 34,102,000) match the receipt.

**Final-turn proof**
- Codex captured turn 3 with completion-to-callback timing, so that is solid.
- Claude's async callback read observation 3, matching the retained final request, and the final request ended before the callback.
- Grok's final-turn evidence is the per-turn `grok usage` result with `modelCalls: 1`. The receipt does not timestamp the query or show that no later request occurred, so this is the weakest of the three.

**Limitations and cost**
- The text separates native usage and `costUsdTicks` from billed cost, and states that no billed dollar amount was verified. It does not convert ticks to USD.
- The caveats are stated: no dynamic callback install in the Desktop chat, no self-enrollment, direct-only root-agent scope, and a fixed Claude wait with no guaranteed flush latency.

**Minor, non-blocking**
- The Claude `settled_callbacks` and Codex callbacks are not labeled with which session or run they belong to. The Codex initial run also has no session ref. This is inferable from the counts but should be made explicit.
- "Tools and delegation unused" is supported only indirectly, for example by Grok `modelCalls: 1`. The receipt has no explicit tool-call counts.
- `local_command_user_rows` is an odd field name for the native user-row count of 3.
- The Claude and Codex turn 1 start times (15:33:03.335Z and 15:33:03.334Z) differ by 1 ms, which suggests the two ran concurrently. This is fine, but worth noting if shared-load effects matter.
