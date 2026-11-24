# #432 independent evidence review

2026-11-24. A separately launched headless Claude Code reviewer used `claude-sonnet-5-5` and received the full sanitized report and JSON receipt. This was an off-platform evidence review.

Report SHA-256 `f7dc848ad6c0d2df594ba116914bdf1ccfa1ddc6487b98ea6c963cfc7720f03d`. Receipt SHA-256 `ae329da07065ebe86e97cd6dd9c336b1fc1fbc4025802bbc4b88d7529c3fb921`.

PASS

**Confirmed**
- **Totals:** I recomputed all three providers and they match the receipt exactly.
  - Codex: 129,682 for work turns, 174,549 with the report.
  - Claude: 228,996 for work turns, 307,695 with the report.
  - Grok: 116,440 for work turns, 157,173 with the report.
- **Codex cross-check:** the cumulative native totals (63,917, 107,133, 150,856, 195,723) are consistent with the per-turn values. The turn 1 baseline of 21,174 is correctly excluded.
- **Storage comparisons:** the three cells are labeled consistently between report and receipt.
  - Repo-local log: exact for all three, with 4 replay rows collapsing to 3 unique turns and turn 99 creating no entry.
  - Session context: exact after resume and compaction for all three.
  - Native memory: Claude passes. Codex and Grok are "not demonstrated" and the report calls them inconclusive. This is acceptable because both cells are clearly labeled.
- **Attribution:** `agent_initiated_self_query` is true for all three. The report states the agents were instructed each turn and that autonomous triggering was not tested. That is the right limit.
- **Compaction and handoff controls:** all flags are true for all three providers, including `no_tools_in_recall` and `fresh_repo_handoff_exact`.

**Limitations to keep attached to the result**
1. **Claude turn 5 settlement:** the receipt's corrected callback record (turn 9, value 41,765, ordinal 11) is a separate later control. It is not the turn 5 value. The 78,699 figure comes from native ancestry reconciliation, not from the callback. The report's wording is accurate, but it should not be read as the callback capturing turn 5.
2. **Grok settlement:** turn 5 was read through a one-shot exact-turn lookup, and no completion hook was tested. The report says so.
3. **Reporting-turn scope:** the in-turn report contained only the three work turns, and turn 5's own usage is settled afterward. The "total including report" therefore reflects a post-hoc settlement, not what the agent itself reported.
4. **Overhead claim:** the "two requests or calls versus one" comparison uses an unrelated baseline prompt. Token differences between baseline and work turns are confounded by prompt content, so the overhead evidence is only the tool-loop count.
5. **Cost:** Grok cost ticks vary widely between turns (about 340M, 140M, 143M, 342M) without explanation, likely a cache effect. The report correctly makes no billing or cross-provider price claim.
6. **Evidence base:** this is one run per provider, and the receipt is sanitized. Native trace sources are not included, so the exactness claims rest on the author's reconciliation. This review cannot independently verify them.
7. **Claude memory isolation:** the result shows directory isolation only, not per-story access control. The report says this.
8. **Disposition wording:** "only tested mechanism" is fair for the combination of dedup and fresh-agent handoff. Session context was also exact, but it does not provide fresh-agent handoff.

No material overclaims found. The report is well scoped and the inconclusive cells are labeled as such.
