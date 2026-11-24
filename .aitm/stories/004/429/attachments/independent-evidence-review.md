# #429 independent evidence review

A separate headless Claude Code session used Sonnet 5.5 and reviewed the sanitized results and receipt. This was an off-platform evidence review.

Report SHA-256 `3afdf1f7a42ca44d03f16ed8e3e155490f7cbf09d78e0eb46cba71a7c9a5010a`. Receipt SHA-256 `23b8b0bcb963fa000efc4e6be733aec3f0c390f71aaeaa0909297f46dbc3275d`.

PASS

I recomputed every total from the receipt and each matches the report.

**Codex**
- Primary cumulative usage runs 19,481 → 38,993 → 58,618, giving deltas of 19,481, 19,512 and 19,625.
- Primary input (58,589), cached input (52,608) and output (29) sum correctly.
- Stdout cumulative counters (38,974 and 58,589 input) equal the running sums of the per-turn usage.
- The control retry totals 18,453 (17,850 + 603).
- Stdout fields and retained cumulative/last fields are labeled separately.

**Claude**
- The four primary list costs sum to 0.0142264 (0.0083798 + 0.0040349 + 0.0008823 + 0.0009294).
- Token sums are 8 input, 3,248 cache-creation, 8,084 cache-read and 41 output.
- The aborted top-level cost of 0.0132970 equals 0.0124147 + 0.0008823.
- The final top-level 0.0133441 equals 0.0124147 + 0.0009294, so it dropped the aborted 0.0008823 as claimed.
- The control pair sums to 0.0146283, with tokens 4 / 2,045 / 3,503 / 609.
- Per-result `model_usage_since_last_result` is distinct from top-level usage, which is zeroed on both aborted results.
- Request IDs match the retained records on every attempt.

**Grok**
- Primary ticks sum to 305,986,400, equal to the retained session total.
- Total tokens sum to 56,699, with input 10,263, cache-read 46,208, output 228 and reasoning 209.
- Each turn's total equals uncached input + cache-read + output, with reasoning inside output.
- Each retained input equals uncached input + cache-read.
- The cancelled attempts have null usage and are absent from the retained summaries.
- The report describes the control's ordinal 4 (session turnCount 1) as an opaque session+ordinal pair, which fits the receipt.

**Replay and billing**
- Deliveries and unique observations are 4/3 for Codex, 5/4 for Claude and 4/3 for Grok on the primary path, and 2/1, 3/2 and 2/1 on the control.
- Only the successful retry was replayed, as the report says.
- Every `billing` field is null, and the report makes no billing inference.
