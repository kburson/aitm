---
schema: "aitm.story/v0"
id: 143
title: "[#133 T06] Deliver local advisory feedback"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/143"
parent: 133
children: []
blocking: [172]
blocked-by: [142]
created: "2026-11-10T16:51:10Z"
updated: "2026-11-12T15:39:20Z"
last-branch: "codex/aitm-wave50-143"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-12-143-local-tia-design.md", "design/reviews/sar-2026-11-12-wave50-design/review-manifest.md"], "plan": ["plan/2026-11-12-143-refinement.md", "plan/2026-11-12-143-local-tia.md", "plan/2026-11-12-143-jit.md", "plan/reviews/sar-2026-11-12-wave50-jit/review-manifest.md", "plan/143-local-validation-e2c87eef770b.md", "plan/delivery-checklist.md", "plan/143-focused-nodeids.txt", "plan/native-run-r1-diagnostic.md", "plan/143-local-validation-717da4ce2540.md", "plan/143-replacement-focused-nodeids.txt", "plan/native-advisory-717da4ce2540.json", "plan/hosted-attempt-1-717da4ce2540.json", "plan/owner-disposition-717da4ce2540.json", "plan/verifier-pass-717da4ce2540.json", "plan/review-entry-signature-717da4ce2540.json"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T06", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "fc2eef29fc3410c7e4a56949ba44c28dc76ef94ee4fc87557d71bd44ca2bdbcb"}
---

# [#133 T06] Deliver local advisory feedback

[GitHub issue #143](https://github.com/kburson/aitm/issues/143) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L256)

**Required predecessors** [T05 #142](../142/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T06. Deliver local advisory feedback — 3h, P2, T05

**Owns** `tools/ci/tia/local.py`, `test_tia_local.py`.
**Interface** `python -m tools.ci.tia.local --base <ref> --plan|--run`.

- [ ] `test_local_dirty_snapshot_never_mints_hosted_proof` and
  `test_selection_failure_runs_entire_applicable_suite` check output
  scope, deduped IDs, actual exit status and full escalation.
- [ ] Render summary plus a machine-readable plan and runner result.
  Stop on post-snapshot drift or unsupported required capability.
  V(local) passes and a controlled local fixture runs both modes.

## Wave 50 leaf design and refinement

- [Design](design/2026-11-12-143-local-tia-design.md) · SHA-256 `467f647b560118c51783313118b01854c8cecb4fc4d53083005a00411cdcbc96`
- [Refinement](plan/2026-11-12-143-refinement.md) · SHA-256 `8320cbccf6f113b8001d900f020fec8a79a61ff1c7b2bcd6195ffa0b16019e99`
- [Independent review](design/reviews/sar-2026-11-12-wave50-design/review-manifest.md)

## Wave 50 Plan and JIT

- [Plan](plan/2026-11-12-143-local-tia.md) · SHA-256 `5da21fa6b30418d58dd1d5cbf18f6b9b022552ed2d5f0b3c05e3331c6b027b63`
- [Jit](plan/2026-11-12-143-jit.md) · SHA-256 `febd54ed163210198097dd69c825644b489a68e09fbbb3213cfbcadf800316ab`
- [Independent review](plan/reviews/sar-2026-11-12-wave50-jit/review-manifest.md)

## Wave 50 candidate validation

[Source PR](https://github.com/kburson/aitm/pull/265) · [Local validation](plan/143-local-validation-e2c87eef770b.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `e2c87eef770bd89a2ab68c7795a7d0a34398cfef`, branch tree `8b71d7263241fdeb8f4e057f4daa6b5b14d0ac82`, target base `0dfbcf0c4b346fe014674aae0775a82f40e3a9b8`. Hosted exact-candidate verification and independent review are pending.

## Wave 50 replacement candidate validation

[Source PR](https://github.com/kburson/aitm/pull/265) · [Local validation](plan/143-local-validation-717da4ce2540.md) · [Delivery checklist](plan/delivery-checklist.md).

Attempt 1 head `717da4ce2540d4ba52f340cd3fe276fc43ccfb5b`, branch tree `2f5169c7e1129f0cdb089b9d52ffe776de6af782`, target base `0dfbcf0c4b346fe014674aae0775a82f40e3a9b8`. Hosted exact-candidate verification and independent review are pending.

### Evidence-based owner disposition

The Wave 50 coordinator applied the owner’s standing delegation to the exact candidate and verified all required evidence. [Disposition](plan/owner-disposition-717da4ce2540.json) · [Trusted verifier](plan/verifier-pass-717da4ce2540.json) · [Authenticated readback](plan/review-entry-signature-717da4ce2540.json). Independent SAR on this exact candidate follows Review admission.
