# #431 independent evidence review

A separate headless Claude Code session used Sonnet 5.5 and reviewed the sanitized results and receipt. This was an off-platform evidence review.

Report SHA-256 `776b659823a365dfb8db4e5838d78b4c60339aa71ea04b7115ea56048a4b2533`. Receipt SHA-256 `2c619fd05f64d8b61cae75ec4e9dcdc60893a0dbcee808d434938758d352abd6`.

PASS

**Recomputed (all match the doc and receipt):**
- Claude settled: 255,871 + 221,297 = 477,168 tokens, and $0.1577910 + $0.0662874 = $0.2240784.
- Grok settled: 257,418 + 159,356 = 416,774 tokens, and 1,429,196,800 + 617,222,400 = 2,046,419,200 ticks.
- Completed reviewer subtotal is 893,942 tokens.
- Interrupted reviewers: 103,367 + 114,066 = 217,433 tokens.
- Each per-attempt token total equals the sum of its native counters.
- Codex orchestrator: 5,372,133 input + 12,343 output = 5,384,476 tokens.

**Verified:**
- **Author decision:** The round-1 `author_used_decision_before_usage_delivery` is true for both providers, and the revisions were sealed (20:29:22.610 and 20:29:33.343) before the round-2 decisions. The round-2 fields are null, which matches the prose.
- **Ordering:**
  - Each decision's stream line precedes its terminal line in all four native streams.
  - `delivery_order` matches the `delivered_at` timestamps, with round 2 before round 1 for both providers.
  - The 151.9–177.8 s decision-to-delivery gaps match "about 152–178 seconds".
- **Interruptions:**
  - Claude ended `aborted_streaming` and Grok ended `cancelled`, both with no sealed decision and `partial` status.
  - Claude's usage matches the retained request sum.
  - Grok has five usage frames, no numeric final usage and no retained turn, as the doc says.
- **Codex checkpoint:** 20:32:17.925Z, about 23 ms before the first delivery at 20:32:17.9487. It is correctly labeled partial and active, with no billed or API-equivalent figure.
- **Reviewer gap:** `codex_aipr_reviewer` is "not qualified", and the doc points to #430 for the lock and #434 for the follow-up.
- **Replay:** The before and after digests are identical (`b40be6da…0150`) with 6 rows each. All six receipts return `replayed`, `refused-assignment` (wrong review) and `refused-conflict` (changed outcome).

**Optional fixes, not blocking:**
- "Both attempts preserved a pending AIPR review state" is not shown in the receipt. It records only `sealed_decision_observed: false`, and Claude's launcher status is `failed`. Soften the wording or add the field.
- "All four brokers reported offline" is also absent from the receipt.
