# #433 independent evidence review

A separate headless Claude Code session used Sonnet 5.5 and reviewed the sanitized results and receipt. This was an off-platform evidence review.

Report SHA-256 `8edca7598e7fbcbb94f354ae0800b9485574814a8fb4a5b446d1508ba9be2782`. Receipt SHA-256 `1984612f1d02b18f7126d89fcf01d5ca519ff25e852c9af19b615cffeb55ddd7`.

## Full evidence review before the final one-field correction

REVISE

**Blocking issue: stale epic elapsed in the receipt**
- `late_attribution.after_epic.workflow_elapsed_ms` is 141755. The headline, `rollup.epic_inclusive` and `epic_workflow_markers` say 142028 (1795556824481 − 1795556682453).
- 141755 equals the last close minus the first native turn start (1795556682726). That is the old basis, not the first assignment marker.
- Fix: recompute that field from the marker, or drop it.

**Checked and passing**
- **Epic elapsed:** the first assignment marker is `claude-seq-shared` start 1795556682453. The last child close is `live-b` end 1795556824481. The result is 142.028 s, matching the headline and `rollup.epic_inclusive`.
- **Turn references:** the 34 `native_turn_ref` values are all unique. `native_turn_refs_are_session_scoped` is true, and each ref sits under a single `session_ref`.
- **Observation count:** 21 observations have a null `exclusion_kind`.
- **Token totals:** by session, by role and by scope, the 21 observations all sum to 443,354.
- **Engaged time:** by session and by role, the sum is 75.776 s.
- **Child scopes:** the epic direct work, parallel child A, parallel child B and the eight sequential and live children add up to the epic totals.
- **Mixed-label turns:** there are three. Each has a null effective scope and a `scope_gap`, and none overlaps its adjacent child's marker window. They total 41,655 tokens and 4.956 s, matching the text.
- **Unmarked controls:** nine turns, 125,098 tokens. The unrelated account control is 2,743 tokens.
- **Late-source provenance:** the brainstorm session has `original_scope` null and `original_exclusion_kind` "unattached-pool". It has an explicit attribution event and moved 19,265 tokens and 7.820 s once. Its interval is covered by `orch-a`, so wall time is unchanged. Replay and conflicting-link refusal are recorded.
- **Handoff and nested figures:** the handoff and nested figures match the receipt. The 2.064 s parallel intersection and 2.002 s owner wait recompute correctly.

## Final review of the elapsed-field correction

PASS

The delta resolves the blocking issue. `late_attribution.after_epic.workflow_elapsed_ms` is now 142028, which matches `rollup.epic_inclusive` and the marker arithmetic (1795556824481 − 1795556682453 = 142028).

The rest of the changed section is consistent:
- `after_epic` totals match `epic_inclusive`: 21 observations, 443,354 tokens, 75,776 ms engaged, 57,186 ms working wall.
- Moving 19,265 tokens and 7,820 ms reconciles `before_epic` to `after_epic` (424,089 + 19,265 = 443,354; 67,956 + 7,820 = 75,776).
- Working wall is unchanged at 57,186, as expected since `orch-a` already covers the interval.
- `after_child` is internally consistent: 235,091 + 19,265 = 254,356, and 40,253 + 7,820 = 48,073.

I did not re-verify the unchanged fields; I relied on the prior review's checks and your statement that they are byte-identical.
