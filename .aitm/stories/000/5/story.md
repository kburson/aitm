---
schema: "aitm.story/v0"
id: 5
title: "[Core C03] Canonical authored content and metadata ownership"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/5"
parent: 2
children: []
blocking: [6, 12, 16, 29, 53, 70]
blocked-by: [3]
created: "2026-11-09T07:59:45Z"
updated: "2026-11-09T08:17:42Z"
last-branch: "planning"
last-worktree: "/Users/kpburson/projects/aitm-workspace/planning"
estimate: {"agent-hours": 3.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/2/plan/core-implementation-plan.md#c03-canonical-authored-content-and-metadata-ownership"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 2, "key": "C03", "path": ".aitm/stories/000/2/plan/core-implementation-plan.md", "publication": "55b94bbe77a19002ff077c122560cf185652d25c", "raw-sha256": "2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd", "section-sha256": "6d0a283214b51c039ea59182d36996d5e5bbbd9a0612b38fb913de9196968ce5"}
---

# [Core C03] Canonical authored content and metadata ownership

**GitHub issue:** [kburson/aitm#5](https://github.com/kburson/aitm/issues/5) · **Parent:** [#2](../2/story.md) · **State:** Backlog.

**Review-procedure decision before implementation:** native XPR accepted the parent decomposition, but later rounds reused earlier full-file context with targeted rereads instead of the requested fresh full-file reread. The [published manifest](../2/plan/reviews/xpr-2026-11-09-core-plan/review-manifest.md) retains this limitation and the question of additional explicitly authorized full-file validation. No sixth round or policy waiver is implied.

## User story

As a developer delivering aitm-core, I want the bounded C03 capability and proof described below so the accepted core design can be delivered with auditable dependencies and acceptance evidence.

## Scope and estimate rationale

This is the 3 implementation agent-hour, P1/S leaf from the [accepted parent plan](../2/plan/core-implementation-plan.md#c03-canonical-authored-content-and-metadata-ownership), publication `55b94bbe77a19002ff077c122560cf185652d25c`. The estimate includes local verification and source-review engagement; it is not measured actuals or a calendar promise. S means this scoped deliverable is estimated at no more than four hours; P1 follows the core's foundational priority. Prerequisite interfaces and fixtures are reused as stated in the plan. At JIT, resplit/review if current evidence makes the cap implausible; expansion is not planned overflow.

**Blocked by:** [C01 / #3](../3/story.md).

**Blocking:** [C54 / #6](../6/story.md), [C07 / #12](../12/story.md), [C15 / #16](../16/story.md), [C24 / #29](../29/story.md), [C46 / #53](../53/story.md), [C53 / #70](../70/story.md).

Dependencies include shared-file serialization, not only functional dependencies. A closed issue without delivered required interfaces is insufficient. This is an ordinary child, not an expansion. [Execution order and independent work](../2/plan/leaf-stories.md).

## Accepted decomposition excerpt

The exact parent-plan section follows. C-keys are stable plan identities; the actual issue dependencies are mapped above. The excerpt is parent decomposition evidence, not this leaf's own Design/Plan/JIT acceptance.

**Estimate:** 3 h · **Depends on:** C01 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** packages/aitm-core/pyproject.toml; uv.lock; src/aitm_core/models/documents.py; src/aitm_core/documents.py; packages/aitm-core/tests/unit/test_c03.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `canonicalize(raw: bytes, schema: DocumentSchema) -> ContentIdentity; rewrite_metadata(raw: bytes, generated: Metadata) -> bytes`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_canonical_vectors: RFC8785 vectors; semantic title/source/body change changes digest; generated updated/status changes do not; duplicate YAML keys, aliases/tags and unsupported fields fail. Body Unicode/whitespace remains exact. Prove the selected YAML loader rejects duplicate keys, aliases and tags explicitly; library defaults are not sufficient. Keep the package manifest and root lock consistent, with dependency selection serialized after C01. No later leaf silently adds another library.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c03.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Dependency/library selection must prove RFC8785 rather than calling ordinary sorted JSON canonical.

## JIT reminders and likely defects

Likely defects are the refusal, identity, timing, omission or recovery failures named in **Test first**; retain each corresponding negative assertion, not just the nominal path. Risk boundary: Dependency/library selection must prove RFC8785 rather than calling ordinary sorted JSON canonical.

Pin current source and prerequisite delivery evidence before Develop. Keep the common plan verification/review/delivery cycle and exact touched-path ownership.

## Bootstrap provenance

Created from accepted epic decomposition under the owner's 2026-11-09 planning assignment. GitHub issue creation occurred at `2026-11-09T07:59:45Z`; this local record was written at `2026-11-09T08:17:42Z`. Events are explicitly manual bootstrap v0 records. No unavailable core command, runtime guard, leaf review, JIT, Develop clock or implementation delivery is claimed. The original epic Refine estimate remains unchanged.
