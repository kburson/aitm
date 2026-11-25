# #426 independent research closeout review

2026-11-25. Separate headless Claude Code reviewer `claude-sonnet-5-5`. Off-platform evidence inspection. The closeout author separately verified live issue, board, PR and planning readback.

## Round 1

Artifact SHA-256 `fabdc14adc284cb56050fbdbc3b5f6fa3d3cba982ba01eeb354c21b4511de19f`.

HOLD

**1. The decision's status is unclear, and #100's authority is only partly protected.**
- The research brief asks for a decision before the #100 plan changes. The implementation plan is still labeled "Proposed" and says to keep it "beside #100's accepted plan until the owner decides".
- The closeout states "Use small portable… adapters" as settled and notes #435 is in Dev. It omits that PR #446 is already a draft for #436/#437.
- Add one sentence saying the strategy is a recommendation, naming who accepted it for #426, and stating that #435 is not accepted as a replacement for #100's open work.
- That work covers #121, #123/#124, #125–#129, #137, and the Core #2, #123, #124 and #230 dependencies. The closing sentence on #100 is good but too general.

**2. Deferred and unqualified conditions have no tracked owner.**
- Several items are listed as "release or follow-up controls where applicable" or "unqualified" without a link: billing calibration, harness-upgrade drift checks, remote lookup and retention, overnight/restart recovery, and the Codex sealed-review route.
- Link each to a specific story, such as #445 or a follow-up, or label it explicitly as unowned. Otherwise closing #426 hides the gaps.

**3. Some exit dimensions are thinner than the evidence calls for.**
- The brief's follow-ups were a bounded API-backed billing comparison and a repeat across a harness version change. Neither is reported as done. The closeout should say plainly that they were not run.
- Maintenance burden is only a deferral, with no assessment. The brief also asks to "quantify its gaps". The self-report overhead of about 34–35% appears in the plan but not here.

**4. Visible bounds are missing a few items.**
- Windows live support is unqualified and absent from the closeout.
- Codex resume counters need a verified baseline.
- The Linux container could not start the Codex sandbox, and #434's macOS result is specific to the tested configuration.

**5. The evidence anchors don't match.** The closeout verifies against commit `878ab167`. #435 cites plan commit `65951b8f`. Confirm both contain the same plan text. #426's own frontmatter still reads `backlog`, so the closure needs a matching state transition.

## Round 2

Artifact SHA-256 `8f8cde54e559b2862cb80968d3ae046d987d997f2d8ed188fe7f8fc46953db84`.

HOLD

**Material findings**

1. **The owner's direction for #435 is asserted, not evidenced.** The closeout says "the repository owner directed creation and pickup of #435." It gives no link to the comment, decision record or event. #426's own text requires the decision to be presented before #100's delivery plan changes. #435 is already in Dev with merged implementation (PR #446, #436–#439 closed). That makes this claim the sole support for keeping #100's authority with its owner. Link the direction record, and state that #435 is separate from #100 and decides nothing about #100's scope.

2. **The #100 reconciliation has no tracked item after closure.** Master-plan step 4 and the implementation plan ("Keep this proposal beside #100's accepted plan until the owner decides…") leave the retain, defer or replace decision open. That plan is still labeled "Proposed." The closeout says the owner "still holds" the decision but names no issue, comment or checkpoint on #100 where it is carried. Closing #426 removes the only place that tracks it. Add a pointer on #100 to the plan and findings, or record the decision as explicitly pending the owner, so it stays visible.

3. **"Reopen focused qualification if a required surface has a remaining coverage gap" has no owner or trigger.** The closeout correctly says billing calibration, cross-version drift, remote lookup, long retention, overnight or restart recovery, and a new sealed Codex route have no research owner. It then points to #444 and #445 for related delivery work, which could read as covering those gaps. Say plainly that #444 and #445 do not qualify those gaps. Also name who decides whether to reopen a spike.

4. **Minor staleness.** #435 still says PR #446 is "open as a draft," and #426 is still Backlog. The closeout acknowledges both, but the stale #435 text should be fixed before publishing.

The research bounds otherwise match the cited evidence: the 34–35% overhead, 443,354 tokens, Codex limits and the Linux control are all stated within their tested scope.

## Round 3

Artifact SHA-256 `15db103f2d4786e17ac3c7f619aa1fe8a2dfa8fd3327573821eb55bd3044d352`.

HOLD

**Material findings**

1. **Unowned gaps contradict "research complete."** The closeout says billing calibration, cross-version drift, remote lookup, long retention, overnight/restart recovery, and a sealed Codex reviewer route "have no assigned research owner in the #426 ladder," and that this list "remains outside the current acceptance criteria of #444 and #445." The story file's follow-up section still lists the billing comparison and version-repeat as intended experiments. These are either deliberately dropped or still owed, and the closeout does not say which. Closing leaves them visible only as prose, with no tracked owner or explicit owner-accepted deferral. Fix: file a follow-up or record an explicit deferral decision for each.

2. **The "owner decides" conditions are not tied to an owner action.** Native telemetry is "deferred," and reopening qualification depends on "the owner," yet no recorded decision is cited. Only the #435 creation direction (events.jsonl line 15) is cited, and that covers the delivery epic, not these deferrals.

3. **Bounds exceed the evidence in places.**
   - "Exact local recovery is demonstrated on three harnesses" and "all three self-queried" are fine. "Existing chats" is bounded only by "arbitrary attachment unqualified," which is acceptable, but the headline "research is complete" is broader than that.
   - The 443,354-token reconciliation is a bounded fixture. The closeout flags this, but the recommendation to use it for epic reporting should carry the same limit.
   - The 34–35% overhead comes from short #432 trials. It appears twice without the sample-size caveat in the decision section.

4. **#100 authority is mostly preserved but ambiguous.** The decision is correctly marked pending and #435 is stated to have no authority over #100. However, the story file says "Use this recommendation to reconcile scope with #100's accepted plan," and the plan says the proposal sits "beside #100's accepted plan." Closing #426 should state that it makes no change to #100 and that the pending decision stays with its owner. The closeout also asks to "close #426 on the strength of... handoff," which could be read as discharging the #100 decision. Reword it.

5. **Stale evidence.** The #426 story still shows `state: backlog`, "children" without #435, and #435 draft text ("PR #446 is open as a draft"). Reconcile these before sign-off. The planning commit pin `878ab167` differs from the plan's audit commit `45db935a`. State that the latter was taken at a different time.

## Round 4

Artifact SHA-256 `a001bb8c9b62ea42203627e2bc776b91eb78e961278794d0ad4952b9e6c3ec28`.

PASS

The artifact meets the #426 research exit on the evidence it presents.

**Deliverables present.** Every comparison dimension in the exit is addressed:
- existing-chat support, autonomy, and own-orchestrator coverage
- per-turn XPR fidelity and delayed recovery
- billing comparability and permissions
- multi-story handoff and unattached-work attribution (the 443,354 tokens, 75.776 engaged seconds, and 57.186 working wall seconds reconciled in the bounded fixture)
- maintenance burden, with the measured 34–35% reporting-turn overhead

It gives a smallest-slice recommendation (small session-scoped adapters, structured completion first, bounded exact lookup) and a decision section. The eight spikes carry closure timestamps and signed retro links.

**Claims are bounded.** The artifact states several limits plainly:
- Arbitrary attachment and fully autonomous enrollment are unqualified.
- Sealed Codex review is unqualified.
- Actual subscription charges and API billing are unverified, with no API claim made.
- Windows, remote lookup, long retention, and restart recovery are unqualified.

The optional telemetry, billing, and upgrade items are correctly shown as non-gates.

**#100 authority unchanged.** The closeout explicitly makes no change to #100 and leaves the continuous-service decision with its owner. #435 is treated as a separate epic, with the owner direction cited at 35ff1dcc.

**Residual notes (not holds):**
- Gaps without a research owner (billing calibration, cross-version drift, remote lookup, retention, overnight recovery, new Codex reviewer route) remain visible. They fall outside #444 and #445 acceptance criteria, so someone should assign them during delivery.
- I could not independently verify the GitHub, Project 24, PR #446, or byte-identity claims. This environment has no repo or network access, so I took them as stated.
