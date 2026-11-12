---
schema: "aitm.story/v0"
id: 141
title: "[#133 T04] Derive Python and package edges"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/141"
parent: 133
children: []
blocking: [142]
blocked-by: [139, 140]
created: "2026-11-10T16:51:04Z"
updated: "2026-11-12T03:35:50Z"
last-branch: "codex/aitm-wave30-141"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/derive-python-package-edges-design.md", "design/reviews/spr-2026-11-11-wave30-design/review-manifest.md"], "plan": ["plan/2026-11-11-141-refinement.md", "plan/2026-11-11-141-python-package-edges.md", "plan/2026-11-11-141-jit.md", "plan/reviews/spr-2026-11-11-wave30-jit/review-manifest.md", "plan/2026-11-11-141-local-validation.md", "plan/delivery-checklist.md", "plan/hosted-readback-be8f5bff9311.json", "plan/verifier-hold-be8f5bff9311.json", "plan/reviews/2026-11-11-141-source-assessment-r1.md", "plan/reviews/2026-11-11-141-source-assessment-r2.md", "plan/hosted-signature-be8f5bff9311.json", "plan/owner-disposition-be8f5bff9311.json", "plan/verifier-pass-be8f5bff9311.json", "plan/review-entry-signature-be8f5bff9311.json", "plan/reviews/141-formal-sar-r1.md", "plan/2026-11-11-141-local-validation-sar-r1.md", "plan/2026-11-11-141-focused-nodeids-sar-r1.txt", "plan/owner-disposition-8a4d9d5ee81a.json", "plan/verifier-pass-8a4d9d5ee81a.json", "plan/review-entry-signature-8a4d9d5ee81a.json"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T04", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "8834c6ab0466869c48e118e34b3064ff1ef86a362aaecc5e4db66a6f6c0b6165"}
---

# [#133 T04] Derive Python and package edges

[GitHub issue #141](https://github.com/kburson/aitm/issues/141) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L217)

**Required predecessors** [T02 #139](../139/story.md), [T03 #140](../140/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T04. Derive Python and package edges — 3.5h, P1, T02/T03

**Owns** `tools/ci/tia/python_graph.py`, `test_tia_python_graph.py`.
**Interface** `build_graph(snapshot, provider_policy) -> Graph` with
directed consumer/input edges and unresolved scope records.

- [ ] `test_import_alias_relative_reexport_cycle` preserves exact
  edges through initializers and module owners. `test_dynamic_scope`
  records unknown readers and package reachability.
- [ ] Resolve static imports with Python AST and trusted package-root
  mapping. Include pytest fixture and configuration scopes from
  qualified inputs. V(python_graph) passes. Neither a cycle nor an
  ambiguous namespace package silently drops a potential edge.

## Wave 3 refinement draft

Rank 30. The required predecessors are Closed as completed and marked Done. [Refinement draft](plan/2026-11-11-141-refinement-draft.md).

## Wave 30 leaf design and refinement

- [Design](design/derive-python-package-edges-design.md) · SHA-256 `0f10b0e978208480b39b304c9e513019e2f603bb1358a0b8738eff75f817d438`
- [Refinement](plan/2026-11-11-141-refinement.md) · SHA-256 `7ef160644c7374a678ad6b837507839ef886de327eeb88c0348b1400160baedc`
- [Independent review](design/reviews/spr-2026-11-11-wave30-design/review-manifest.md)

## Wave 30 Plan and JIT

- [Plan](plan/2026-11-11-141-python-package-edges.md) · SHA-256 `ba033428548e17f629e8f5b161a85b64b7980ebd74a05f2baba530e533e86944`
- [Jit](plan/2026-11-11-141-jit.md) · SHA-256 `445e6838ac835c1ed61f75209c5e5ebec0d43e1c159a220b5f993c8147533e1c`
- [Independent review](plan/reviews/spr-2026-11-11-wave30-jit/review-manifest.md)

## Wave 30 candidate validation

[Source PR](https://github.com/kburson/aitm/pull/262) · [Local validation](plan/2026-11-11-141-local-validation.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `be8f5bff9311655fb788e597c69069c23609a341`, branch tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`, target base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`. Hosted exact-candidate verification and independent review are pending.

### Hosted validation and delivery hold

[Exact hosted run](https://github.com/kburson/aitm/actions/runs/43140853744/attempts/1) completed with `success`. [Independent source assessment](plan/reviews/2026-11-11-141-source-assessment-r2.md). The [trusted verifier](plan/verifier-hold-be8f5bff9311.json) requires the owner's disposition for tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`. Formal review and merge readiness remain pending.

### Evidence-based owner disposition

The Wave 30 coordinator applied the owner’s standing delegation to the exact candidate and verified all required evidence. [Disposition](plan/owner-disposition-be8f5bff9311.json) · [Trusted verifier](plan/verifier-pass-be8f5bff9311.json) · [Authenticated readback](plan/review-entry-signature-be8f5bff9311.json). Independent SAR on this exact candidate follows Review admission.

### Independent PR review

[Formal SAR verdict](plan/reviews/141-formal-sar-r1.md) records **changes-requested** for head `be8f5bff9311655fb788e597c69069c23609a341` and tested tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`.

## Wave 30 replacement candidate validation

[Source PR](https://github.com/kburson/aitm/pull/262) · [Local validation](plan/2026-11-11-141-local-validation-sar-r1.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `8a4d9d5ee81a98596b893c03f43b383fa3acab22`, branch tree `f2c045b29ed4c8f99ba8056de459d17ff340f4d3`, target base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`. Hosted exact-candidate verification and independent review are pending.

### Evidence-based owner disposition

The Wave 30 coordinator applied the owner’s standing delegation to the exact candidate and verified all required evidence. [Disposition](plan/owner-disposition-8a4d9d5ee81a.json) · [Trusted verifier](plan/verifier-pass-8a4d9d5ee81a.json) · [Authenticated readback](plan/review-entry-signature-8a4d9d5ee81a.json). Independent SAR on this exact candidate follows Review admission.
