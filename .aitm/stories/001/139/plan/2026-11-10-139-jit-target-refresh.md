# #139 JIT and suite policy refresh for the #182 trunk merge

This delta supplements the exact accepted #139 design, plan and JIT
in [planning publication b62000a](https://github.com/kburson/aitm/blob/b62000a647dccd1343573deaddf436ca179a5177/.aitm/stories/001/139/story.md).
It updates the source baseline and adds two explicit mappings within the
accepted T02 inventory scope. Preserve the original attempt, its
private evidence and the 3.5-hour estimate, with the four-hour cap.

## Exact target and evidence

- Literal target is `trunk` in `kburson/aitm`. #182 [PR #195](https://github.com/kburson/aitm/pull/195)
  advanced the base from `a495d60a87ac4ca764f019dc266e579f13f1787e` to
  `49865245d175ce6c52913738f2c9a42c0abea632`, tree
  `9737a9685e928c57e922cc8a68343ae195b9bacf`. #138's delivered
  merge is still an ancestor. #182 changed product and tests.
  The `tools/ci`, workflow, project manifest and lock trees match
  the prior baseline.
- [Exact push run](https://github.com/kburson/aitm/actions/runs/42912899702/attempts/1)
  workflow 412848571, suite 116218799122, run 42912899702 attempt 1.
  Quality, file checks, Python and collector succeeded.
  Verified raw archive 13808377023 SHA-256
  `9bc9ff4fb159a2e35416ad93aa636370653116d280b2706e035f5dcbf9d27987`.
  Its raw pytest report SHA-256 is
  `a821943660b790e3571d815f5062b7f808ff5fecf0cfca88d487d18551ca9c6b`.
  Its sorted compact UTF-8 node array SHA-256 is
  `ee3b88c58ceb7607aebf994226ef05a2d11b537b4d2d7cd23029b336368ade5d`.
  It reports 867 unique nodes, zero deselections, both required
  child labels and 9,638/10,538 product and 778/821 helper lines.
  The push supplies comparison evidence and a base reference.
  Fresh exact #139 PR checks remain required.
- Compared with the 748-node prior push, 119 IDs were added and zero
  removed. Added IDs occur in `test_scope_legacy.py` (40),
  `test_codex.py` (31), `test_scope_admission.py` (25),
  `test_claude.py` (22), and `test_monitor_scope.py` (1).

## Explicit suite policy delta

Add `packages/aitm-usage/tests/test_scope_admission.py` and
`packages/aitm-usage/tests/test_scope_legacy.py` as exact
`aitm-usage` integration module rules in `native-process-state`.
Their tests use actual ledger, monitor, CLI or service state, lock
and publication behavior. They belong with the existing conservative
integration group. Keep the current Darwin/APFS collection scope.
Preserve explicit per-test capabilities from the existing policy and
refuse any future unknown module. Existing classifications and
the #103 policy stay in force.

## Pickup and validation

Rebase or merge current trunk into the existing isolated #139
source branch only after independently accepting this exact delta.
Record the old candidate and new exact tree. Retain the frozen 748
and 182 proof and historical role replays as separate evidence.
Recheck the two exact local collection components and common
snapshot on the new baseline. Reconcile the exact 867 host IDs
against the new local product/CLI IDs and the unchanged 182 helper
IDs, with a 1,049-obligation full advisory union if both sets agree.
Re-run focused, neighboring and full local validation and use fresh
#103 exact PR checks and independent source review. Another target
advance requires fresh applicability and exact delivery evidence.
