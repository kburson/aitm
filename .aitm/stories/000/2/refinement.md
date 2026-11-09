---
schema: aitm.doc/v0
story: 2
role: refinement
title: Core initial refinement
created: 2026-11-09T06:37:02Z
updated: 2026-11-09T06:37:02Z
last-branch: planning
---

# Core initial refinement

Initial estimate: **180 implementation agent-hours**, size **XL (epic)**, priority **P1 / high foundational dependency**. Recorded before implementation-plan decomposition; this original estimate is immutable history, not a four-hour leaf estimate or calendar promise.

The accepted core design at publication `1f4d4a354a10dfd173c70cc8421dafd28c25a57a` has raw SHA-256 `1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d`. It covers durable multi-clone persistence, policy/init, lifecycle and evidence recovery, verification isolation, review ingestion, migration and package qualification. Rough sizing is 45–60 independently testable leaves averaging about 3–3.5 engaged hours, including tests and source review; 180 h is the initial central estimate. Confidence is low-to-medium: concurrency, platform containment and legacy provenance have no implementation baseline yet. An uncertainty band of roughly 130–250 h describes epic forecasting, never permission for a leaf attempt to exceed four hours. Planning/review time is separate and unbounded.

XL means a multi-subsystem epic that must decompose; this assignment does not impose a global size vocabulary. P1 means it blocks all usable extension slices and the safe bootstrap replacement; it is not an operational emergency. No priority labels are assumed to exist on GitHub.

The implementation plan will record a separate bottom-up Plan estimate and source lineage. JIT must resplit any leaf that cannot fit the limit before Develop. No clock starts from this Refine record, and no elapsed response span is claimed as measured engagement.

Bootstrap record: authored by Codex gpt-6-astra/xhigh in session `01a1be2f-9c32-79b1-9385-b18044d32156` under the owner's autonomous planning assignment. The v0 event is manual provenance, not a command emitted by the unavailable core. The existing historical Backlog state is retained; this record supplies the requested Refine facts without inventing runtime guard evaluations, state transitions or current exact-content policy acceptance. Later migration/planning reconciliation must preserve that distinction.

Open owner choices remain those in the accepted design/master plan. Production review policy and GitHub provider readiness gate later adoption; they do not block this authorized planning assignment.
