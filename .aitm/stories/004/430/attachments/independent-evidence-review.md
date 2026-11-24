# #430 independent evidence review

A separate headless Claude Code session used Sonnet 5.5 and reviewed the sanitized results and receipt. This was an off-platform evidence review.

Report SHA-256 `a0d930ad1d8b6b6a4ab13ab64b2cb827604259e44fe96bb3446d52dcaa24c237`. Receipt SHA-256 `e460dc115dc358e07198dcc6f81b93caaebd5df4f61b6a628d960914cdef5fd1`.

PASS

**Recomputed, all consistent:**
- **Claude:** the cumulative cost 0.1541551 + 0.0558075 = 0.2099626 matches. Per-result tokens equal the retained request sums in both rounds and in the interruption.
- **Grok:**
  - Round 1: 43,796 + 183,936 = 227,732 input and +2,143 output = 229,875 total.
  - Round 2: 4,546 + 184,448 = 188,994 input and +1,177 output = 190,171 total.
  - Frame sums equal final usage in both rounds, and the frame counts (9, 6, 4) match.
- **Codex XPR:**
  - Attempt 1 is 91,428 + 516 = 91,944.
  - Attempt 2 delta, from cumulative minus the prior turn: input 50,125, cached 49,152, output 235, reasoning 0 and total 50,360. Input + output = 50,360, and 142,304 − 91,944 = 50,360.
- **Codex lightweight:** 19,656 + 104 = 19,760, and the round 2 delta is 20,008 + 99 = 20,107. Both match the cumulative differences.

**Correlation:** The AIPR event, actor fingerprint and response digest come from the broker and were joined to the provider stream by session ID plus a distinct prompt root (Claude) or turn ordinal and request ID (Grok). That is separate source evidence, and the submit-before-terminal ordering is recorded. Two limits apply. First, both rounds share one session, so the fingerprint alone does not separate them. The separation rests on prompt root or ordinal, which the receipt does record. Second, Grok's AIPR identity is `declared`, so the binding is adapter-verified rather than broker-verified. The text already says this. The receipt holds only booleans and pseudonymous refs, so these claims can't be rechecked from it, which is consistent with the raw traces being withheld.

**Round types:** The artifacts keep these distinct:
- **Completed Claude/Grok rounds:** sealed, with exact usage.
- **Interrupted Claude:** partial usage of 77,200 cache read, 24,899 cache write and 682 output, aborted, no seal.
- **Interrupted Grok:** `cancelled` with an incomplete flag and no numeric turn. Frame counters are kept as partial observations only.
- **Failed Codex XPR:** two refusal turns with tokens but no join, plus an aborted third turn with null usage.
- **Codex lightweight:** native only, with no AIPR claims and no savings ratio.

**Billing and scope:** `verified_billed_spend` is null, the Claude figures are labeled list-price estimates, and the text says billed spend is out of scope. Sample size and the single-OS, single-build limits are stated.

**Minor revisions to consider (not blocking):**
1. The Disposition says "Each route also demonstrated a joined, interrupted attempt," but Codex had no join. Say "Claude and Grok."
2. The list-price dollar figures can't be recomputed without the price table. Cite it, or say they are provider-reported.
3. The Grok `native_cost_usd_ticks` has no price-basis or tick-to-USD note, unlike the Claude fields. Add one.
4. The receipt's `native_cumulative_usd` could be misread as spend. Rename it to something like `native_list_cumulative_usd`.
5. Two claims are unsupported in the receipt. One is that Claude assistant-block output counts run lower than the final request values. The other is the #429 reference. Add supporting numbers or mark them as not in this receipt.
6. I did not check the external source links.
