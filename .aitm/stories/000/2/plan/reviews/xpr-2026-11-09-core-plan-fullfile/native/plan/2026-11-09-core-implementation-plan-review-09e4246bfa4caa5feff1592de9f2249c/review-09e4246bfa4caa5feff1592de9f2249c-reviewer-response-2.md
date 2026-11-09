<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-09e4246bfa4caa5feff1592de9f2249c"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_commit: "b80d0fb9bd63cecbc9665a295c98119a24ec2440"
artifact_blob: "97cae59d57a60358b642c91c9d14d6e2eca78879"
artifact_digest: "sha256:d586d85b2988f24c60a8a5a43497b00ac54316fc17963fe29955e16aa4f03219"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:00278e43df2c8f02eef7ab5892e8a19c3d1097a8b1ee6e0e18436dcf006ca043"
  identity_source: "runtime"
started_at: "2026-11-09T13:20:53.276Z"
submitted_at: "2026-11-09T13:33:09.472Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is round 2 of the independent full-file validation of the revised plan (`b80d0fb9bd63cecbc9665a295c98119a24ec2440`, 78 leaves / 255.5 h). I read author response 1 and my own round-1 response in full. I also freshly reread the whole revised FUR against the accepted core design.

All five round-1 required findings (F1–F5) and the three optional suggestions are resolved. Their disposition is verified below.

The revision introduces one new ordering gap, R2-F001. Two Gate C qualification suites exercise story/defect promotion past Develop and Test, including dispatch-admission prerequisites. They are ordered before C76, so they would run before the production StoryExitGuards evaluator exists. Their refusal assertions could then pass for the wrong reason.

### Fresh full-file reread

- **Method:** Read in contiguous chunks of ≤30 lines, this round only, restarted at line 1 because the file changed.
- **Ranges:** 1–30, 31–60, 61–90, 91–120, 121–150, 151–180, 181–210, 211–240, 241–270, 271–300, 301–330, 331–360, 361–390, 391–420, 421–450, 451–480, 481–510, 511–540, 541–570, 571–600, 601–630, 631–660, 661–690, 691–720, 721–750, 751–780, 781–810, 811–840, 841–870, 871–900, 901–930, 931–960, 961–990, 991–1020, 1021–1050, 1051–1080, 1081–1110, 1111–1140, 1141–1170, 1171–1200, 1201–1230, 1231–1260, 1261–1290, 1291–1320, 1321–1350, 1351–1380, 1381–1410, 1411–1440, 1441–1470, 1471–1500, 1501–1530, 1531–1559.
- **EOF:** The final request (offset 1531, limit 30) returned 29 lines ending at 1559, so 1559 is EOF.
- **Observed line count:** 1559. Grep for `$` also counts 1559.
- **Long lines:** Grep `^.{2001,}` returns 0 matches. The wrapped long paragraphs (62–63, 100–101, 223–224, 312, 584–585, 761–762, 810–811, 827–828, 1050–1051, 1097–1098 and 1336–1338) came back in full with their continuation lines. No output was truncated, so no recovery was needed.
- **Native input artifact digest:** `sha256:d586d85b2988f24c60a8a5a43497b00ac54316fc17963fe29955e16aa4f03219`. This value comes from this response's protected `artifact_digest` (blob `97cae59d57a60358b642c91c9d14d6e2eca78879`). Shell hashing is unavailable to this reviewer session, so I could not recompute it, and the author audit should confirm it.

### Disposition verification of round-1 findings

| Finding | Status | Evidence in the revised FUR |
| --- | --- | --- |
| F1 source-commit, Test-exit and Review-exit guards | Resolved | C76 (lines 1222–1236) covers the exact `[#<id>] ` prefix with its trailing space, rejects `[#12]` and embedded, nondecimal, zero and negative IDs, and rejects commits off-branch or before the baseline and empty or merge-only deltas. It also covers retained commits/head/tree, the current-receipt Test exit, the same-source Review composite, squash/rebase through source mapping, the signoff.py rewire without a prior-signoff cycle, and an unregistered-evaluator negative. Coverage row 1411 and scenario row 1455 are updated. |
| F2 kind-guard and finalizer production wiring | Resolved | C01 now declares KindRequirements, AggregateEvidence and StoryExitGuards slots (line 224), and C28 declares their ports (line 762). C29 touches guards.py, transitions.py and services.py and adds `test_kind_registration` (line 794). C62 registers AggregateEvidence from services.py (line 1200). C30 registers its finalizer during explicit composition, not as an import side effect, and adds `test_expansion_finalizer_registration` (line 811). New edges include C71→C29→C30→C31 and C43→C62→C63→C76→C75. |
| F3 `sync --reconcile` and `--push` | Resolved | C17 owns both adapters, with `test_sync_reconcile_cli` (supersession lineage, unpublished original retained, a single lost-ACK reconcile) and `test_sync_push_cli` (line 512). The CLI map (line 118), the C67 ledger (line 1294) and scenario row 1456 are updated. |
| F4 v0 kind mapping | Resolved | C77 provides a pure mapping with unresolved/no-default/no-split vectors (line 1036). C46 adds `test_actual_v0_kind` (lines 1050–1051), C48 blocks an unresolved kind before CAS (line 1083), and C51 adds `test_migrated_kinds`, with epics exempt from the leaf rule (lines 1097–1098). Coverage rows 1411/1422 and scenario row 1458 are updated. |
| F5 installed `explain` | Resolved | C78 owns cli/read.py after C18 (C18→C78 edge at line 1554). It covers the next kind edge, per-guard pass/fail/unknown, freshness-unknown, pending effects and the exact command. C18 reports explain unavailable until then (line 526), and C52 times the full path (line 1322). |
| Optional 1 (C71 wording) | Adopted | Line 778 now says Plan/JIT→Backlog, then Backlog→Refine. |
| Optional 2 (C49→C48) | Retained with rationale | Line 1266 gives the reason: the composed final history validator. This is acceptable. |
| Optional 3 (explain budget) | Adopted | Line 1322. |

### Structural checks independently re-verified

- **Totals:** I re-added the leaf table: 78 leaves, 255.5 h, every leaf 2.5–4 h. The round-1 deltas sum correctly: C76 4 + C77 2.5 + C78 3 = 9.5, plus C17/C29/C30/C51/C62 adding +1, +1, +0.5, +0.5 and +0.5 = 3.5.
- **Order:** the backlog table (lines 134–213) is topological. Every predecessor of C77, C62, C63, C76, C78, C49 and C75 appears earlier.
- **`services.py`:** it has 23 writers, which matches the 23-link chain in the shared-file table (C01→C06→C07→C08→C14→C09→C10→C11→C12→C17→C74→C21→C28→C71→C29→C30→C31→C35→C43→C62→C63→C76→C75).
- **Other new shared-path edges:** each is listed and present in Depends-on: guards.py C28→C71→C29→C76; transitions.py C28→C71→C29→C31→C76; signoff.py C42→C76; kinds.py C29→C62; cli/read.py C18→C78.

## Findings

R2-F001: required, moderate. The C65 and C66 qualification suites run before the production story/defect exit evaluator (C76), so their refusal assertions can pass because the evaluator is missing rather than because the intended guard fired.

- **The new port:** after this revision, story/defect Develop, Test and Review exits dispatch to the StoryExitGuards port. C29 (line 794) says an "absent port is unknown/unavailable until C76", and enforce refuses in that state (C28, line 762).
- **What C65 exercises (Depends on C64, C30, C31, C32, C35, C38, C42, C61; ordered at line 199, before C76 at line 203):**
  - `test_expansion_completion_fence`: a pending expansion versus actual test, promote and signoff.
  - `test_trip_before_sync_and_pass`: a trip before completion and before an effective pass.
  - `test_reservation_and_review_rebuild`: an early verdict later activated in Review, which requires a story that has already passed its Develop and Test exits.
- **What C66 exercises (Depends on C64, C41, C42; line 200):** `test_local_delivery_admission` needs a core-run delivery admission. Under core-design line 411 that admission requires an effective passing review, so the story must already have crossed the Develop and Test exits.
- **Failure scenario:** these suites run against a composition with no production StoryExitGuards. Then:
  - a promote or signoff refusal asserted as the "pending expansion blocks" or "trip before pass" outcome would also occur purely because the exit evaluator is unavailable, so the scenarios pass vacuously;
  - alternatively, the suites inject a fixture evaluator, so the Gate C qualification no longer exercises the real production exit-guard composition. C70 sets the precedent here: it asserts that no fixture preflight is installed.

  Either way, Gate C (line 1425) and the scenario rows at 1469–1472 claim production qualification of these paths without the C76 evaluator in place.
- **Not affected:** C49 and C68 already follow C76, via C49→C76. C50 and C70 do not cross story Develop, Test or Review exits.

## Required changes

1. **R2-F001:**
   - Add C76 to the Depends on lists of C65 and C66, and move both rows after C76 in the topological table. No cycle results: C76 does not depend on C64–C66, and C52/C59 already follow both.
   - In each suite, assert the specific refusal cause, such as `expansion-pending`, `trip`, `admission-fenced` or `stale-generation`, and assert that the production StoryExitGuards (not a fixture) is resolved. A refusal for `evaluator-unavailable` must not satisfy those scenarios.
   - Update the C65/C66 scenario rows (1469–1472) to name C76 as a prerequisite owner.

## Optional suggestions

1. C38, C41, C42 and C61 test real promote, activation or signoff between C28 and C76. Their test text could state explicitly that they inject a typed StoryExitGuards fixture through an explicit test composition, with the unregistered slot refusing, mirroring the wording used for AttemptPreflight. C28 line 762 states this only generically. The production re-proof is already covered after C76 by C49, C68 and the revised C65/C66.
2. C76 sits at the 4 h cap with 11 predecessors, roughly a dozen vector groups and a signoff.py rewire. Consider pre-splitting it now into a source-commit guard leaf and a Test/Review composite plus signoff-wiring leaf, rather than relying on a JIT split. This would keep Gate C's critical path less exposed to a single overrun. This is optional because the plan already mandates a re-estimate or split at JIT.

## Decision

revisions-requested
