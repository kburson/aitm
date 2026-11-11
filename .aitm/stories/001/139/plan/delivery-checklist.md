# #139 delivery checklist

Attempt 1. Implementer `codex-collaboration:/root/impl139`. Closure
owner Codex coordinator. Literal delivery target `trunk`. The
owner requested progression through Done after independent JIT.

- [x] Own design, Plan and JIT accepted after independent review.
  [Planning record](../story.md)
- [x] #138 Closed, Done, and delivered on trunk. Own binding in
  Develop. The [accepted target refresh](2026-11-10-139-jit-target-refresh.md)
  preserves the original candidate and adds two reviewed suite rules.
- [x] Open [PR #197](https://github.com/kburson/aitm/pull/197). Base
  `49865245d175ce6c52913738f2c9a42c0abea632`, head `6687ba0262df6eb99e76c66509bf32262017d5b5`,
  tree `ffc00d32b1fa7d9a91c986958a86d19dabc41dfe`.
  Exactly three owned additive paths.
- [x] Refreshed local tree. 29 focused, 87 neighboring, and 1,165
  full tests passed on the staged tree that matches the clean commit.
  Package and CI Ruff, actionlint and tracked-file checks passed.
  The [refreshed reconciliation](refreshed-inventory-reconciliation.json)
  preserves 867 product and CLI plus 182 helper IDs in the full local
  advisory union. The [frozen local validation](frozen-local-validation.json)
  preserves earlier results and the transient initial full-run failures.
- [ ] Verify hosted #103 attempt and exact tested source. [CI run](https://github.com/kburson/aitm/actions/runs/42915266772)
- [ ] Retain independent exact-source review and required #103 disposition.
- [ ] Verify trunk delivery and original implementer sign-off, then Close.

### First exact source candidate

The [post-commit local run](local-validation-6687ba0262df.json) passed
1,165 tests on the exact clean head. All six jobs passed on the
[canonical hosted attempt](https://github.com/kburson/aitm/actions/runs/42915266772/attempts/1).
[Signed artifact replay](hosted-ci-receipt-6687ba0262df.json) confirmed
867 candidate outcomes, 866 base outcomes, and both line floors.

Independent source inspection reproduced malformed pytest parameter
wrappers, invalid hosted Git refs, and transposed child labels
being admitted. The story returns to Develop for scoped corrections.
This head retains its successful tests and its source review hold.

### Corrected candidate on the #194 base

[Independent findings](source-review-attempt-1.md) ·
[GitHub inline findings](https://github.com/kburson/aitm/pull/197#pullrequestreview-5850624988) ·
[Implementer corrections](implementer-correction-handoff.md).

The corrected branch was fast-forwarded on [PR #197](https://github.com/kburson/aitm/pull/197).
Exact base `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2`, head
`36f700e330c07dc8750dfcfa9fe8841c49e35877`, tested source tree
`13f338628918c14f41b56f0c1ef52649b126fc41`. The correction adds
fail-closed validation for malformed pytest parameter wrappers,
malformed hosted refs, and swapped child process mappings. The
three owned file blobs survived the base refresh byte-for-byte.

[Exact local validation](local-validation-36f700e330c0.json) passed
47 focused, 87 neighboring, and 1,193 full tests. The #194 merge
added ten test IDs within the existing install rule, with no
removals or changes to #103 controls. [Reconciliation](inventory-reconciliation-36f700e330c0.json)
binds 877 product and CLI plus 182 helper obligations to the
current base. The [base push](https://github.com/kburson/aitm/actions/runs/42916832495/attempts/1)
passed. Fresh [PR CI](https://github.com/kburson/aitm/actions/runs/42917875102)
is in progress. Independent review is scoped to the replacement.

### Current exact-source verdict and delivery hold

All six jobs passed on the [exact hosted attempt](https://github.com/kburson/aitm/actions/runs/42917875102/attempts/1).
[Signed artifact and raw replay](hosted-ci-receipt-36f700e330c0.json)
verified 877 candidate outcomes, 876 base outcomes, and both coverage
floors. The [independent source SPR](source-review-attempt-2.md) accepted
the exact corrected head and resolved all three prior findings.

The trusted #103 verifier [returned a hold](verifier-hold-36f700e330c0.json).
Its gate-control comparison includes the three additive files under
`tools/ci`. The existing workflow, verifier, policy, helper coverage
denominator and runner inputs are unchanged. #103's first owner
disposition for this change is pending on exact tested tree
`13f338628918c14f41b56f0c1ef52649b126fc41`. No prior disposition applies to the new #139 files.
The source verdict is retained while the Project remains in Test.

### Trunk advanced through #201

Literal trunk advanced to `5324a80bad7730b2bdb4a2b87acf00f7171305c0`.
The [prior verdict](source-review-attempt-2.md) applies to its
recorded base and candidate. An [independently reviewed JIT delta](2026-11-10-139-jit-trunk-5324a80.md)
adds two explicit journal module rules. The [review](reviews/spr-2026-11-10-trunk-5324a80.md)
accepts the scope conditional on a successful hosted baseline.

The [first trunk attempt](https://github.com/kburson/aitm/actions/runs/42940157251/attempts/1)
failed in `test_queued_claude_disable_uses_the_physical_tail[abandoned]`.
The four variants passed in isolation on exact trunk. The full local
product and CLI suite passed all 970 tests. Two collect-only components
reproduced the 970 product and CLI IDs and the unchanged 182 helper IDs
on the shared snapshot
`ae49cc4f00ed734485b003ce3dbf2a717e37eadc553025209548bb5f9e376a58`.
[Hosted attempt 2](https://github.com/kburson/aitm/actions/runs/42940157251/attempts/2)
is the bounded exact-trunk retry.

The bounded retry passed with all four applicable push jobs. Verified
archive `13822032683` SHA-256
`ef3a59a38d63e895486445be261abb0d342770ec6e40bf83b654f608ee0060e3`
and raw pytest SHA-256
`61029da1be74ac1786447aec2e6c38b0b00202db87d628dec309af73a3c92d0a`.
Hosted product and CLI IDs matched all 970 local IDs. The artifact
recorded 10,360/11,301 product and 778/821 helper lines. The first
hosted failure remains part of the record, and its cause is unknown.

[PR #197](https://github.com/kburson/aitm/pull/197) now has head
`a2b52e4367325f1638102dba6709933e1634d262`, tree
`583a652fb4e1d9112c2f77401095b814f8c7e625`, and the exact trunk
base above. The only change to owned files since the prior review
is the two explicit rules in the suite policy. The
[local validation](local-validation-a2b52e436732.json) passed all
1,286 tests and Ruff checks. The
[reconciliation](inventory-reconciliation-a2b52e436732.json) records
1,152 advisory obligations. The story reentered Test with
[fresh hosted PR checks](https://github.com/kburson/aitm/actions/runs/42944835329).

All six jobs passed on the [refreshed hosted attempt](https://github.com/kburson/aitm/actions/runs/42944835329/attempts/1).
[Authenticated artifact replay](hosted-ci-receipt-a2b52e436732.json)
verified 970 candidate outcomes, 969 base outcomes and both coverage
floors. [Independent source review](source-review-attempt-3.md)
accepted the exact candidate with no new findings.

The [trusted #103 verifier](verifier-hold-a2b52e436732.json) held for
the first explicit owner disposition on tested tree
`583a652fb4e1d9112c2f77401095b814f8c7e625`. The gate-control diff consists
of the three additive TIA files under `tools/ci`.

The #202 merge advanced trunk to
`1282538954dc5a7e7f7b27da4e3ab096892e3add` during review. The
pass and disposition hold above apply to the prior base. The
new target changed product code and tests in the two already
mapped journal modules. Recheck the current inventory and review
the exact replacement before delivery.

### Current review on the #202 base

PR #197 fast-forwarded to head `a5fdd76f7e682e2a9ff547db900a9c82ac502fc1`
on literal trunk `1282538954dc5a7e7f7b27da4e3ab096892e3add`. All three
independently reviewed files are byte-identical to the prior
candidate. The [exact trunk push](https://github.com/kburson/aitm/actions/runs/42945628106/attempts/1)
passed and its authenticated archive `13823420424` matched all 996
locally collected product and CLI IDs. There are 26 additions and
zero removals. All additions are in the two reviewed journal modules.
The [reconciliation](inventory-reconciliation-a5fdd76f7e68.json)
records 1,178 advisory obligations, and the
[local validation](local-validation-a5fdd76f7e68.json) passed 1,312
tests with zero failures.

All six jobs passed on the [exact hosted attempt](https://github.com/kburson/aitm/actions/runs/42945914184/attempts/1).
[Authenticated artifact replay](hosted-ci-receipt-a5fdd76f7e68.json)
verified 996 candidate outcomes, 995 base outcomes and both coverage
floors. [Independent source review](source-review-attempt-4.md)
accepted the candidate with no new findings.

The [trusted #103 verifier](verifier-hold-a5fdd76f7e68.json) requires
the first explicit owner disposition for the three new files under
`tools/ci` on tested tree `7709cca894edba3e40e4b193a091e3077e4d5534`.
The story remains in Test pending that disposition.

## Refresh onto b0f8ac7

[PR #197](https://github.com/kburson/aitm/pull/197) was refreshed onto
literal trunk `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`. Its head is
`dbbc729574c9b078658af310b2efa2945020224f` and GitHub tested
`59a03a1942401d2f462c11e548ad74b1d73beeaf` with that base and head as ordered parents.
The tested tree is `7d93353e06c8177c19bc1f918217e2f8ccf75da7`.

The three #139-owned files remained byte-identical. The
[inventory reconciliation](inventory-reconciliation-dbbc729574c9.json)
matched the exact local and hosted trunk push's 1,071 product and CLI
IDs. The 75 additions fit the existing monitor-scope module rule.
There are zero removals, the 182 helper IDs are unchanged, and the
advisory inventory has 1,253 obligations. The
[locked local receipt](local-validation-dbbc729574c9.json) records
1,448 passing tests and 84 subtests, with Ruff, actionlint and
tracked-file checks passing.
The [local product and CLI replay](local-product-coverage-dbbc729574c9.json)
also passed all 1,071 cases and verified both required child labels.


[Hosted attempt 1](hosted-ci-failure-dbbc729574c9-a1.json) recorded the
literal trunk fixture setup failure. The candidate Python suite
passed. The exact failing source was inherited, and the target push
and isolated local reproduction passed. [Attempt 2](hosted-ci-failure-dbbc729574c9-a2.json)
passed the trunk lane and failed one unchanged candidate test after
restart and append. All four isolated test variants passed locally
on the exact base and candidate. Both failed attempts remain part
of the evidence.

[Attempt 3](https://github.com/kburson/aitm/actions/runs/43058239273/attempts/3) passed all six jobs. The
[diagnostic receipt](hosted-artifact-diagnostic-dbbc729574c9-a3.json) independently verifies the
signed artifact, 1,071 candidate and 1,070 base outcomes, and both
coverage floors. The [independent source review](source-review-attempt-5.md)
accepted the exact source without new findings.

[Reviewer confirmation of the CI identity and verifier discrepancy](source-review-attempt-5-ci-confirmation.md).

The [trusted #103 verifier](verifier-hold-dbbc729574c9-a3.json) held before
owner disposition. GitHub reports original run creation
`2026-11-11T16:25:48Z` and rerun creation `2026-11-11T16:42:30Z`.
The delivered verifier requires them to match. A fresh event on the
same PR is the #103-documented recovery. PR #197 remains open and
#139 remains in Test.

[Exact owner disposition scope](owner-disposition-scope-dbbc729574c9.json).

## Fresh canonical PR event

[PR #197](https://github.com/kburson/aitm/pull/197) was reopened using
the [existing #103 procedure](../../103/design/github-ci-quality-gates-design.md).
[Readback](reopened-event-dbbc729574c9.json) confirms an open PR with the
same head and literal base. GitHub generated test merge
`cddd5d3d830769f48850a67479952df15fc18e76` with the same ordered parents and reviewed
tree `7d93353e06c8177c19bc1f918217e2f8ccf75da7`. The original run and its exact evidence
remain above.

The [fresh first attempt](https://github.com/kburson/aitm/actions/runs/43062845686/attempts/1) has a terminal
[hosted receipt](hosted-ci-hold-dbbc729574c9-reopened.json). The candidate Python, quality and
file checks passed. The [candidate receipt](candidate-python-receipt-dbbc729574c9-reopened.json)
verified all 1,071 outcomes. Literal trunk failed during setup of
`test_v2_decoder_rejects_malformed_or_unowned_shape[mixed]` with
`Native capture position is unavailable`. Evidence collection failed
and signing was skipped. The
[trusted #103 verifier](verifier-hold-dbbc729574c9-reopened.json) reported
`selected attempt is not complete and successful`. The proposed disposition is tied to the unchanged
tree. It cannot clear the current evidence hold. The story remains
in Test and the PR remains open.

[Independent identity confirmation](source-review-attempt-5-reopened-ci-confirmation.md).

[Exact #103 owner disposition scope](owner-disposition-scope-dbbc729574c9-reopened.json).

## Exact owner approval and verifier correction

The owner [approved the three additions](owner-disposition-approved-7d93353e06c8.json)
on tested tree `7d93353e06c8177c19bc1f918217e2f8ccf75da7`. That disposition
applies to PR #197. The independent CI evidence requirement remains in force.

The [verifier correction](https://github.com/kburson/aitm/pull/244) is a
separate draft at `64df4e773fe0bdfb52d2854b55ad40535758e6d3`. The first
attempt still requires equal creation times. A rerun can report its own
creation time between original run creation and the attempt update. Every
attempt must still start at or after original run creation. Job and
attestation freshness continue to use the reported attempt start. The
recorded attempt 3 metadata passes this check, including GitHub's reported
start two seconds before the rerun creation record.

Six new regression cases use fixed timestamps and local GitHub API fixtures.
All 276 local CI-helper tests passed. The 188 coverage-lane cases passed
with 95.2% verifier line coverage. The 47 inventory tests on PR #197's exact
head passed twice in separate pytest processes. Keep unit cases isolated,
with independent fixtures and repeatable inputs. Integration cases may use
internal components together and mock external services. Reserve live
provider and cross-system connections for end-to-end validation.

## Revalidation of the approved tree

[Canonical attempt 2](https://github.com/kburson/aitm/actions/runs/43062845686/attempts/2)
retained the approved tree, base, head, and test merge. The [terminal
receipt](revalidation-hold-7d93353e06c8-a2.json) records 1,068 passing
base tests and two setup errors in the native capture fixtures. Both
failing cases passed in isolated local runs on the exact base and head.
The affected test modules and `monitor_registry.py` are identical on
those revisions. The hosted trigger remains unconfirmed.

The candidate Python lane exceeded its eight-minute job limit. Quality
and file checks passed. Evidence collection failed and signing was skipped.
The deployed verifier and a diagnostic run of the patched verifier both
held on the latest attempt's unsuccessful outcome. The earlier signed
attempt remains historical. PR #197 stays open and #139 remains in Test.
