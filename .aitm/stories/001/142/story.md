---
schema: "aitm.story/v0"
id: 142
title: "[#133 T05] Select and explain test impact"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/142"
parent: 133
children: []
blocking: [143, 151, 163]
blocked-by: [139, 141]
created: "2026-11-10T16:51:07Z"
updated: "2026-11-12T14:18:46Z"
last-branch: "codex/aitm-wave40-142"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-12-142-select-test-impact-design.md", "design/reviews/sar-2026-11-12-wave40-design/review-manifest.md"], "plan": ["plan/2026-11-12-142-refinement.md", "plan/2026-11-12-142-select-test-impact.md", "plan/2026-11-12-142-jit.md", "plan/reviews/sar-2026-11-12-wave40-jit/review-manifest.md", "plan/142-local-validation-4e752acaf311.md", "plan/delivery-checklist.md", "plan/142-focused-nodeids.txt", "plan/owner-disposition-4e752acaf311.json", "plan/verifier-pass-4e752acaf311.json", "plan/review-entry-signature-4e752acaf311.json", "plan/reviews/142-formal-sar-r1.md", "plan/premerge-verifier-4e752acaf311.json", "plan/premerge-rules-4e752acaf311.json", "plan/verified-delivery-4e752acaf311.json"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T05", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "d27a66d5f7cd624d32983cd6a733b14cfba0d53f4adf85b566bdb34d06ade416"}
---

# [#133 T05] Select and explain test impact

[GitHub issue #142](https://github.com/kburson/aitm/issues/142) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L231)

**Required predecessors** [T02 #139](../139/story.md), [T04 #141](../141/story.md).

The planning estimate is 4 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T05. Select and explain test impact — 4h, P1, T02/T04

**Owns** `tools/ci/tia/selection.py`, `tools/ci/tia/edges.json`,
`test_tia_selection.py`. **Interface**
`select(before, after, inventory, policy) -> Selection`.

- [ ] `test_renamed_module_selects_former_consumer`,
  `test_cross_package_declared_subprocess_path`, and
  `test_known_edge_plus_unbounded_reader_runs_full` assert exact
  witnesses, qualified IDs and the full inventory on uncertainty.
- [ ] `test_direct_and_multihop_exact_witnesses` asserts
  `engine.py → test_engine.py::test_run` and
  `leaf.py → engine.py → test_engine.py::test_run` with the exact
  obligation ID and edge kinds. `test_declared_fixture_cross_package`
  asserts the fixture, cross-package consumer and exact test ID.
  `test_changed_test_and_non_test_disposition` asserts the changed
  test's self witness and exact ID, and an empty optional set with
  the named trusted non-test rule on a docs-only fixture.
- [ ] Union old/new reverse consumers, mandatory and changed IDs.
  Resolve declarations against trusted policy and record provenance
  for each path. A no-test result requires positive policy for every
  change and no mandatory obligation. V(selection) passes, including
  missing endpoints, deleted required case and arbitrary filename
  resemblance.

## Wave 40 leaf design and refinement

- [Design](design/2026-11-12-142-select-test-impact-design.md) · SHA-256 `849e2eb8f742ee79a241703f311f50e4efb325cba300d92d25657a2c2e71ae98`
- [Refinement](plan/2026-11-12-142-refinement.md) · SHA-256 `1e59e88020b404501d85775d61a6209e8cb1e0f0b767addc3e6eddb5e1929ce9`
- [Independent review](design/reviews/sar-2026-11-12-wave40-design/review-manifest.md)

## Wave 40 Plan and JIT

- [Plan](plan/2026-11-12-142-select-test-impact.md) · SHA-256 `2d9d2d9105c9ff0b883815138251c3455b766768f5834ef1680fd9dd7411747b`
- [Jit](plan/2026-11-12-142-jit.md) · SHA-256 `de66a1bfafcad9d82575d5717851d5c96be8245fd92b060c031dfee111b3ee59`
- [Independent review](plan/reviews/sar-2026-11-12-wave40-jit/review-manifest.md)

## Wave 40 candidate validation

[Source PR](https://github.com/kburson/aitm/pull/263) · [Local validation](plan/142-local-validation-4e752acaf311.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `4e752acaf311c42c4173fc532977502b88ba398a`, branch tree `61eeabeed1362d5c39188dd6aade2b6549515b01`, target base `011342493399ed6e8a12ba0e9c2a4a1e9efaf294`. Hosted exact-candidate verification and independent review are pending.

### Evidence-based owner disposition

The Wave 40 coordinator applied the owner’s standing delegation to the exact candidate and verified all required evidence. [Disposition](plan/owner-disposition-4e752acaf311.json) · [Trusted verifier](plan/verifier-pass-4e752acaf311.json) · [Authenticated readback](plan/review-entry-signature-4e752acaf311.json). Independent SAR on this exact candidate follows Review admission.

### Independent PR review

[Formal SAR verdict](plan/reviews/142-formal-sar-r1.md) records **accepted** for head `4e752acaf311c42c4173fc532977502b88ba398a` and tested tree `61eeabeed1362d5c39188dd6aade2b6549515b01`.

### Verified trunk delivery

[Delivery receipt](plan/verified-delivery-4e752acaf311.json) confirms merge `0dfbcf0c4b346fe014674aae0775a82f40e3a9b8`, its exact ordered parents and reviewed tree `61eeabeed1362d5c39188dd6aade2b6549515b01` on protected `trunk`. Implementer sign-off and closure follow.

### Implementer sign-off

[Signed retrospective](retro/2026-11-12-142-implementer-retrospective.md) covers the verified source and delivery.
