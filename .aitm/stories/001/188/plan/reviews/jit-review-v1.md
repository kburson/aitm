# #188 Design, Plan and JIT review

Signed 2026-11-10 America/Chicago (2026-11-11 UTC) by Codex `/root/pickup186`, a separate same-provider reviewer. Reviewed all 33 lines of `pickup.md`, SHA-256 `494c0cfb418e6a43a593e52603255d8d51903f78d5de90a4cf21d58d7238a556`, against the accepted #181 design and A03, and the delivered #186 and #187 interfaces.

## Design verdict

Changes requested. Line 11 applies actor wait and idle exclusions across direct stories. An actor with an outstanding response on story A can have independently evidenced turn engagement on story B. Apply exclusions where the wait or idle is evidenced for that actor and direct story, honoring any known scope dimensions. Preserve the calendar union of waits across epic descendants separately.

Line 13 leaves a partial numeric zero possible. The parent contract requires complete coverage to report zero Owner wait. State that rule explicitly, including a pending request with a checkpoint equal to its start. A pending or incomplete observation can preserve its state and evidence even when the amount remains Unknown.

The independent measure interfaces, integer interval handling, direct and inclusive graph fold, historical seed verification, and fail-closed elapsed and calibration scope otherwise match A03. Confirmed the historical #111 Develop and Done evidence at 14:15:31Z and 14:28:25Z on the parity pin.

## Plan verdict

Changes requested. Add focused regressions for a story-specific owner wait overlapping the same actor's active turn in another story, and for an incomplete or pending wait that cannot establish numeric zero. The existing parallel fixture, real parity, estimate exclusions and exact candidate checks otherwise cover the accepted scope.

## JIT verdict

Accepted for scope. Verified #187 Done on the fetched planning ref, the sole predecessor in #188's record, and the clean `codex/aitm-188-timing-rollups` checkout at `e4701f2e89d34f93f13d717199254b66aa3f0457`, matching local `origin/trunk`. The new timing files are disjoint from #189's usage paths. The 3.75-hour estimate fits the four-hour cap including verification and review. Expected-head planning publication and live overlap checks stay with the coordinator. Exact candidate CI, independent source review, delivery verification and sign-off remain required. Develop is gated on the Design and Plan corrections.
