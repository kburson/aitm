# #181 local delivery and production scope transfer

The owner authorized closing #181 for A/B and completed read-only C01, with unfinished Slice C production work transferred to its dependency owners. The original [reviewed plan](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md) remains an immutable source. Use its acceptance details when refining the successor work. Completed [#227 qualification](https://github.com/kburson/aitm/blob/c794b1b0be8b7bb67ba7bb1d530fe8a80296f95b/.aitm/stories/002/227/attachments/qualification.md) remains under #181 as delivered evidence and is available to every successor.

| Scope | Production owner and tracking record | Pickup gate |
| --- | --- | --- |
| C02 legacy replay | Core #2 · [#228](https://github.com/kburson/aitm/issues/228) | Core pinned read #23, applicable legacy adoption #53–#56, release #72. Authorize a production cutover separately. |
| C03 native Actual | Core #2 · [#229](https://github.com/kburson/aitm/issues/229) | #23, #28, #34, #36 and release #72. Require host/provider proof for each claim. |
| C04 Cost and ingress | Usage Monitor #100 · [#230](https://github.com/kburson/aitm/issues/230) | #123/#124 production and Core #51 receiver compatibility. |
| C05 board projection | #1 M2 · [GitHub extension draft](../../../../drafts/2026-11/20261108-1310-github-extension/draft.md#c05-intake-from-181) | Qualified timing from #228 or #229, authorized writer and production readback. Cost has the additional #230 gate. |
| C06 shared view and hosting | #1 M6 · [Viewer draft](../../../../drafts/2026-11/20261108-1310-viewer/draft.md#c06-intake-from-181) | Versioned view and freshness, appropriate timing and usage proof, and M2 board parity. |
| C07 comparable estimates | #1 M8 · [Rubric draft](../../../../drafts/2026-11/20261108-1310-rubric/draft.md#c07-intake-from-181) | #51 outcome and estimate lineage plus matching complete Actual from #228 or #229. Usage can be absent. |

M2, M6 and M8 have existing drafts rather than graduated epics. Their intake records are indexed in [#1 planning](../../../000/1/story.md#story-dashboard-production-intake-from-181) and carry forward at the owning milestone's refinement. The six work items total 19.0 preliminary agent-hours, derived from the reviewed 21.25 h Slice C estimate less C01's 2.25 h. The new issues remain in Backlog.

## Epic delivery and sign-off

- A/B delivery and scoped Actual are recorded in the [local handoff](2026-11-10-local-dashboard-handoff.md). All nine children #186–#193 and #227 were read back as GitHub Closed Completed and AITM-PY Done. Their own review and sign-off evidence remains in their planning records.
- [Renderer PR #221](https://github.com/kburson/aitm/pull/221) merged to trunk at fec3d8f685fd1d133bb9797d47c02552805e6bc1. [Quick-start PR #222](https://github.com/kburson/aitm/pull/222) merged to trunk at bc8063b66522ed3a27c95d1bb0546f1e73249612 after its [signed CI run](https://github.com/kburson/aitm/actions/runs/42965457517/attempts/1) and [independent source review](../../193/plan/post-ci-source-review.md). The verified trunk b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5 contains the delivered dashboard tree byte for byte. A fresh Python 3.13.1 suite from that tree ran 61 tests, with 60 passing and one skipped.
- [Coordinating agent retrospective and sign-off](../retro/2026-11-11-181-epic-signoff.md). The pre-close Project measurement was 2.946 hours with Cost blank.
