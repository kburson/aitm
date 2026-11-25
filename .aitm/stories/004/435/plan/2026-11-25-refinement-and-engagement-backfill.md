# Epic #435 refinement and engagement backfill

Project 24 records Estimate and Actual in agent-hours. #435 is a Feature and its estimate sums the ten leaf estimates. Each leaf stays within the four-hour limit.

The estimates for #436 and #437 already existed on planning. Estimates for delivered #438–#441 are retrospective scope estimates. Estimates for #442–#445 use the approved scope for each story, including #442, which was already in development. This backfill records the sizing review on its actual date.

| Issue | Size | Estimate (h) | Sizing basis |
| --- | --- | ---: | --- |
| [#435](https://github.com/kburson/aitm/issues/435) | Feature | 27.5 | Sum of the child estimates. |
| [#436](https://github.com/kburson/aitm/issues/436) | M | 2 | Versioned receipt types, transactional SQLite ingestion, rollback, replay, and conflict isolation. Existing planning estimate. |
| [#437](https://github.com/kburson/aitm/issues/437) | S | 1.5 | Immutable assignment, exact turn ownership, and one authorized late link with refusal cases. Existing planning estimate. |
| [#438](https://github.com/kburson/aitm/issues/438) | M | 2.5 | Shared adapter contract, bounded capture, and exact recovery with cancellation, timeout, and terminal-state fixtures. |
| [#439](https://github.com/kburson/aitm/issues/439) | M | 3 | Exact Codex rollout recovery, trusted resume deltas, interruption, and configured TUI qualification. |
| [#440](https://github.com/kburson/aitm/issues/440) | M | 2.5 | Per-result and finalized-request normalization, cache fields, cancellation, and configured Stop recovery. |
| [#441](https://github.com/kburson/aitm/issues/441) | M | 3 | Exact retained turn and ordinal matching, native ticks, wire compatibility, and interactive qualification. |
| [#442](https://github.com/kburson/aitm/issues/442) | L | 3.5 | Exact scope and handoff boundaries, disjoint nested usage, per-actor engagement, interval-union wall time, and parity with the #433 fixture. Exercise a delayed worker and a mixed turn. |
| [#443](https://github.com/kburson/aitm/issues/443) | M | 3 | Deterministic story, epic, and unattached CLI views with provenance and coverage. Prove the read-only legacy adapter preserves snapshot identity, sequence, and published export bytes. |
| [#444](https://github.com/kburson/aitm/issues/444) | M | 3 | Link usage to sealed review identity and digests. Verify mismatches, reversed delivery, interruption, and replay, preserving the failed Codex attempt and its decision gap. |
| [#445](https://github.com/kburson/aitm/issues/445) | L | 3.5 | Qualify Linux and macOS installation and Windows fixtures. Reconcile a same-provider story and a cross-provider trail, document overhead and privacy, and preserve capability gaps. |

## Done story delivery and Actual

Actual is partial observed engagement reconstructed from timestamped, completed Codex items. The dashboard unions overlapping intervals per agent and sums independent agents. It excludes explicit waits, passive hosted CI watches, unbound gaps, and shared work that could not be assigned to one leaf. #436 and #437 share PR #446. Their receipts cover only attributable store and attribution commands, respectively. #437 covers the command that moved the late-attribution tests into the portable suite and verified the change. The shared implementation and review time has no verified per-story split. The limited totals are unsuitable for estimate calibration.

| Story | Merged PR | Observed ms | Actual (h) | Evidence through (UTC) |
| --- | --- | ---: | ---: | --- |
| [#436](../../436/story.md) | [#446](https://github.com/kburson/aitm/pull/446) | 2,348 | 0.0007 | [2026-11-25T03:21:39.668Z](../../436/attachments/timing/435-native-engagement-backfill-20261125-436.json) |
| [#437](../../437/story.md) | [#446](https://github.com/kburson/aitm/pull/446) | 301 | 0.0001 | [2026-11-25T03:19:11.455Z](../../437/attachments/timing/435-native-engagement-backfill-20261125-437.json) |
| [#438](../../438/story.md) | [#447](https://github.com/kburson/aitm/pull/447) | 436,886 | 0.1214 | [2026-11-25T04:35:03.863Z](../../438/attachments/timing/435-native-engagement-backfill-20261125-438.json) |
| [#439](../../439/story.md) | [#448](https://github.com/kburson/aitm/pull/448) | 530,500 | 0.1474 | [2026-11-25T04:55:30.137Z](../../439/attachments/timing/435-native-engagement-backfill-20261125-439.json) |
| [#440](../../440/story.md) | [#449](https://github.com/kburson/aitm/pull/449) | 501,368 | 0.1393 | [2026-11-25T12:44:16.190Z](../../440/attachments/timing/435-native-engagement-backfill-20261125-440.json) |
| [#441](../../441/story.md) | [#450](https://github.com/kburson/aitm/pull/450) | 298,944 | 0.0830 | [2026-11-25T12:59:40.616Z](../../441/attachments/timing/435-native-engagement-backfill-20261125-441.json) |
