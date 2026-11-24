# #428 independent evidence review

2026-11-24. Reviewer model `claude-sonnet-5-5`, launched in a separate headless Claude Code session. Route is off-platform evidence inspection. The payload was the full sanitized report and JSON receipt.

## Round one

Report SHA-256 `9e7d14829b2d5c06aa4e3baa85a51bbf4bce910dd95d06798a7122a534605326` and receipt SHA-256 `a630ed12eaf378fdc5ba962983024fa7c26ed6482232b492897330fad3018391`. A separate headless Grok review of this earlier pair returned **HOLD**.

HOLD

**Numeric support.** The receipt supports the core recovery claim: the first three turns are byte-identical in every field across all four checkpoints for all three providers, and the unknown-UUID control returns a gap on every route at every checkpoint. Codex per-turn totals check out (24991, 25045, 25099, 25143 are consistent with input plus output). The prose says Codex records were differenced from cumulative counters, but the receipt contains only per-turn values, so the differencing step is not auditable. Claude turn 7 is the post-resume turn, yet the prose says four request records and "preceding user turn" association. Turns 4-6 are absent without explanation, and the gap is not reconciled with the "serial sample" claim. Grok totals are not simply input plus output (turn 1: 18638+126=18764 matches, turn 2: 18821+81=18902 matches), so those hold. Grok `costUsdTicks` is native retained usage only. No tick-to-USD conversion is given, and billed cost was explicitly not tested, which the text states correctly.

**Attribution and enrollment.** The text says the unrelated first turn was present without an assignment and could not be attributed, and that separation relied on the known experiment boundary. That is honest. However, the receipt has no assignment/interval data at all, so the claim that assigned and post-resume turns "can be separated" is asserted, not shown. Externally driven enrollment is likewise only implicit: identities were known to the experiment, which is stated, but no evidence shows enrollment occurring from an external record. The final-turn timing claim is weaker still. The post-resume turn is described as outside the assigned interval, but no timestamps for turns or intervals are in the receipt, only checkpoint observation times.

**Surfaces and retention.** Exact surfaces are reasonably scoped: Codex App Server read APIs returned history with empty `usage_paths` (a valid negative), Claude and Codex needed the retained file, and Grok has the native command. The retention window is correctly limited, but note the actual span is about 1h37m... more precisely, from first read (15:31:56) to last (15:33:33) is under two minutes, so the "within three minutes" statement holds and "delayed" and "later" are effectively the same short window. Nothing supports durability claims. The ambiguity control (two candidates, zero opened) supports the Codex resolver refusing, for that one disposable case only. The `desktop_identity_probe` appears in the receipt but is not discussed in the prose.

**Required before PASS.** (1) Explain the Claude turn numbering jump to 7 and reconcile it with the four-record claim. (2) Include turn timestamps and the assignment boundary in the receipt, or soften the separability and final-turn claims to untested. (3) Show cumulative counters for Codex, or drop the differencing description. (4) Clarify the Grok "cost ticks" unit and keep it labeled retained usage, not billed cost. Residual limits: one-shot local macOS, single session per provider, serial workload, no remote, cross-user, long-term, mixed-request, subagent, or billing validation.

## Round two

Report SHA-256 `1e0a77349804fedb85ff69ba57e838e800ad1d8cf3f7a502de91828b8da19907` and receipt SHA-256 `48fec9536d439e0ce4c186148ff1764b4172f982c82a2f54ad5ff3aaa5f3604f`. Revised evidence supplies pseudonymous identities, native parent or turn links, the controlled assignment boundary and the raw cumulative counter basis where applicable.

PASS

**Identity**
- Each provider has one session ref, and the exact-identity lookup was verified (`identity_verified: true`) at all four checkpoints.
- The unknown-UUID control returned a coverage gap for every route at every checkpoint.
- The ambiguity control (2 matches, 0 opened) agrees with the prose.
- Source hashes change once between closed-first and after-resume, then stay stable at delayed and later for all three providers. Initial turns 1-3 are identical across checkpoints.
- The models (`claude-opus-5-5`, `grok-4.7-build`) and the Codex client version are recorded. I can't check them against #427's pins because that file wasn't supplied.

**Assignment boundaries**
- Turn 1 is `unassigned-baseline`, turns 2 and 3 are `assigned`, and turn 4 is `unassigned-after-resume` on all three providers, matching the prose.
- Codex start and completion refs match per turn. Claude's `resolved_parent_ref` equals `prompt_ref` on all four turns.
- Grok's boundary rests on the controlled driver ordinal plus end timestamps, which the receipt and prose both state. It has no native start ref.

**Arithmetic**
- Codex cumulative totals difference exactly to the per-turn values. For example, input goes 24980, 50014, 75102, 100234, giving deltas of 25034, 25088 and 25132. Cached, output and total deltas also reconcile.
- Each Codex per-turn total equals input plus output.
- Grok `totalTokens` equals input plus output on all four turns, and reasoning tokens never exceed output tokens.
- Claude records are direct request values with no sums to check.
- Grok `costUsdTicks` is kept in native units and is not presented as billed cost. The prose says provider billing was not tested, so native observed usage stays separate from independently billed cost.

**Final-turn proof**
- Turn 4 appears at after-resume (observed 15:32:09) on all three providers. Its end times (15:32:05.1 to 15:32:05.8) precede that read.
- Turn counts stay at 4 through delayed and later, consistent with the claim that queries started no model turns.

**Limits**
- The stated limits are supported. Short retention is shown by reads at roughly 2.4 to 4 minutes, and the Codex App Server calls returned empty `usage_paths`.
- Long-term expiry, cross-user or remote access, billing, sidechains and subagents are all declared untested.

**Minor, non-blocking**
- The prose says the first exit wrote three local-command rows, but the receipt's `local_command_user_rows` is 6. Ordinal 7 is consistent with three before the resume, and the other three plausibly came from the second exit. The receipt should say which rows came from which exit.
- The "within three minutes" claim can't be checked exactly because close times aren't recorded. Codex's last turn ended at 15:29:32 and the first read was at 15:31:56, about 2.4 minutes later.
- The prose names "after resume" and "later" reads but doesn't mention the delayed checkpoint. It is harmless, since the data is identical to after-resume.
