<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-baca25051170651fc4512589bc73be80"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
artifact_commit: "7d3d1a57db05abdc97cace136fdda3e847f8c64b"
artifact_blob: "2cd3746caae2f1148605fcb9548b304356430be9"
artifact_digest: "sha256:4500099ac8f04148f1f0f6ee8c2fc31c5e53cbdc16707bcc0fb16f931c97bd59"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:1acdf73fcbb80586e286552155f58ea364355a0fa6bf788f441a1f726bf2e2ee"
  identity_source: "runtime"
started_at: "2026-11-10T16:39:35.636Z"
submitted_at: "2026-11-10T16:47:16.963Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the round 2 independent cross-provider review of
`.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md`.
The revised artifact is blob `2cd3746caae2f1148605fcb9548b304356430be9`,
commit `7d3d1a57db05abdc97cace136fdda3e847f8c64b`, and is 859 lines
long.

Coverage: I freshly retrieved the complete current artifact from the
exact invitation path in contiguous numbered Read calls of at most 40
lines:

- 1–40, 41–80, 81–120, 121–160, 161–200, 201–240, 241–280;
- 281–320, 321–360, 361–400, 401–440, 441–480, 481–520;
- 521–560, 561–600, 601–640, 641–680, 681–720, 721–760;
- 761–800, 801–840, and 841–859 (EOF).

No range was abbreviated. I also read the author response
`review-baca25051170651fc4512589bc73be80-author-response-1.md` in full,
lines 1–83. For requirements I relied on my round 1 reading of the
accepted design. That covered §4 lines 198–235, §5 lines 248–291, §6
lines 292–463, and §§7–8 lines 464–489.

### Verification of round 1 dispositions against the new file

1. **Four-hour limit: resolved, with a regression.**
   - Former T34 is now three leaves: T36 (3.5h, lines 761–771), T37
     (4h, lines 773–785) and T38 (4h, lines 787–799). Each has its own
     receipt and consumer.
   - Former T19 is now T19 (3h, health ingress, lines 469–483) and T20
     (3.5h, workspace and incident authority, lines 485–505).
   - Every leaf states a time of 4h or less.
   - Renumbered cross-references are consistent. I checked lines
     79–85, 332, 346, 525, 563, 609, 626–627, 656, 669, 685, 704,
     716, 721–722 and 839–857.
   - The split dropped one piece of required acceptance evidence. See
     Finding 1.
2. **Timing recipe: resolved.** Lines 132–168 now fix:
   - two consecutive non-overlapping seven-day windows;
   - 20 cohorts per window (5 classes × 2 cache profiles × 2);
   - all three modes run on the same exact candidate;
   - definitions of the five representative classes and of cold and
     warm runs;
   - a proposed cap of 900 runner-minutes per window, subject to owner
     approval;
   - p50 and p95 per mode and per window for the 3, 6 and 10 minute
     envelopes, with no-test lanes shown as N/A;
   - plan review before any change to the recipe;
   - a cutover rule tied to complete reports, sustained sharded-full
     p95 misses, and at least 20% better p95 feedback.

   T35 (lines 747–759) asserts each mode, window and lane.
3. **Restart rehearsal across harnesses: resolved.** T39 (lines
   801–819) uses three clones: Codex Desktop on the affected base,
   Claude Code on an earlier base, and a third native session that
   disconnects before notification. It runs the invalid-conflict,
   stale-generation, withdrawal and older-incident refusals. Release
   must refuse while any current acknowledgment is missing or invalid.
4. **Probe ownership: resolved.**
   - The new `IncidentProbe` record (line 113) and the probe digest
     in `WorkspaceReceipt` (line 114) carry the probe.
   - T26 (lines 596–609) owns it. It binds authority approval, the
     incident version, the repaired revision, and every verified
     failing ID. It also unions selection over local changes and
     conflict resolutions, with full fallback.
   - T31 refuses stale or client-supplied probes (lines 684–689), and
     T32 checks the probe version and digest (lines 703–705).
5. **Selection assertions: resolved.** T05 (lines 241–248) adds named
   assertions for the direct and multi-hop witnesses, with exact
   paths and IDs. It also covers a declared cross-package fixture, a
   changed-test self witness, and a docs-only non-test disposition
   with an empty optional set. The cross-package subprocess case is
   kept (line 238).

All five optional suggestions from round 1 were also applied:

- the test rename (line 419);
- the clarified T25 wording (lines 593–594);
- dropping the timing dependency from the restart rehearsal (T39
  depends on T33/T38);
- the per-package coverage floor (lines 374–375);
- an owner for the delivery deferral (T20 line 502, T36 line 770).

### Remaining issue

Splitting former T34 left one gap. Nothing now rehearses end to end
how a merge-only hold is repaired and released. Design §7 requires
this evidence ("Merge-only holds" row, design line 475). Details are
in Finding 1. No other material issues remain.

## Findings

1. **No leaf rehearses repairing and releasing a merge-only hold
   (lines 773–799, 841–844; design lines 331, 357–359, 475).**
   - **What the design requires.** The §7 "Merge-only holds" row says
     to "Break the scheduled setup on trunk so it emits no test
     outcomes, then exercise the authorized exact full-passing repair
     with independent gate-change disposition and full recovery on
     current trunk". Design §6 adds two rules:
     - a merge-only hold is released "once all recorded causes are
       resolved", without the workspace-update phase (line 331);
     - the incident owner must first substantiate a trunk-source or
       control cause before a source repair is bound (lines 357–359).
   - **What the revised plan does.**
     - T37 (lines 783–785) stops after recording the broken-setup
       hold and the work it still permits.
     - T38 (lines 787–799) is wired only to T36's verified test-stop
       scenario. It ends in the workspace-update transition "for the
       test incident".
     - T40 consumes T37 only as hold results.
   - **What is missing.** No hosted trace covers any of the following:
     - owner substantiation of the control cause for the broken-setup
       hold;
     - binding the exact repair under that merge-only hold;
     - independent gate-change disposition at the hosted level (T23
       covers only the spike);
     - a full recovery run on current trunk that releases the merge
       hold with no workspace-update phase;
     - refusing release while any other recorded cause is unresolved.

     The round 1 T34 bundled broken-base repair with the hold
     scenarios. The split lost this path.
   - **Consequence.** The coverage table (line 844) and the cutover
     prerequisites (lines 855–857) present T36–T40 as covering §7, but
     the merge-only half of the "Merge-only holds" row has no
     executable proof. The release rules for merge-only and test-stop
     incidents also differ, and only the test-stop release is
     rehearsed.

## Required changes

1. Add a bounded leaf of 4h or less, depending on T37 and T38, or
   extend T37 if it can be re-estimated within the limit. In T37's
   isolated broken-scheduled-setup fixture, it must:
   - record the appointed owner's substantiation of the trunk control
     cause;
   - bind the single exact repair PR to the current hold version;
   - obtain independent gate-change disposition;
   - pass the exact repair through the T24 full route and the T22
     conditional merge;
   - run a fresh full suite on the confirmed current trunk;
   - retain the merge-hold release with no workspace-update phase,
     plus a refusal while a second recorded cause stays unresolved.

   Update T40's dependencies, the coverage table (lines 842 and 844)
   and the cutover trace list (lines 855–857) to match.

## Optional suggestions

1. T35's runner-minute cap (line 151) is reasonable as a proposal.
   Consider deriving its initial value from T01's measured serial
   cold and warm runner minutes, so a window is not left unqualified
   only because of the cap.

## Decision

revisions-requested
