---
schema: "aitm.review-response/v0"
level: "xpr"
story: 138
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/001/138/design/pin-serial-baseline-design.md"
artifact_base_commit: "f7928d15ace3a4949ce67c42da37ea7371e05892"
artifact_digest: "sha256:d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:2fb694d9ad80b4467c1bb5056516a998d517503f3ff8035c80ede39b6324374b"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T18:55:14.457Z"
submitted_at: "2026-11-10T18:56:18.324Z"
start_basis: "prior-submit"
start_source: "author-response-1.md"
finding_ids: []
answered_finding_ids: []
native_source: "native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-reviewer-response-2.md"
native_source_digest: "sha256:b9753ad52c64f2d9c418d64c63868bc501b51a1fa41ce1f31ab22b1377d415c8"
---

Mode: `normal`

## Summary

Round 2 cross-provider review of the #138 (T01) leaf design at artifact
commit `60e287c30b9c32339e4ba905b463dfb63278773a`. I checked it against
author response 1 and my round 1 response.

**Read coverage.** Fresh numbered reads of at most 40 lines each, using
the exact invitation path: lines 1–40, 41–80, 81–120, 121–160, 161–200
and 200–217. Line 217 is EOF (the last read returned 18 lines). No range
was truncated.

**Limits.** Shell and web access were unavailable in this session, so I
did not repeat the author's authenticated GitHub readback, scratch gate
replay or helper collection. I judged the dispositions on the evidence
the author reports and on whether the revised design text is consistent
with itself and with the parent plan T01 section (plan lines 172–185),
the plan's interface rules (lines 89–126), the #133 design and #115
custody.

**Note on round 1 IDs.** Round 1 used bold labels instead of level-three
headings, so the broker extracted no sealed finding IDs. The author
answered the five round 1 findings in prose. My verification of each
follows.

- **R1-F001 (helper inventory): closed.** Lines 97–114 now state that the
  hosted helper lane recorded coverage and job success but no node IDs.
  The design pins a separately labeled **local advisory collection** of
  the four exact workflow targets on the shared tested tree. It records
  the lock, Python 3.13.9, the #103 observer, `--collect-only`, 182
  unique IDs and digest `69cef362…`. It forbids treating that collection
  as a hosted `CollectionProof` or as historical per-node outcomes, and
  it makes a missing or discrepant collection block both #138 acceptance
  and #139 pickup. This satisfies the plan's "package/CI helper
  inventories" pin (plan line 178). It keeps the advisory and hosted
  distinction that T02 requires (plan lines 191–193). It also no longer
  uses `Unknown` to fill a proof gap, in line with the leaf's own rule at
  lines 198–199. The 182 count matches the #115 record (checklist
  line 67). The PR tested tree and the trunk tree are the same
  `c1c9bc00…` (lines 24–25 and 36, and #115 line 79), so "shared" is
  accurate.
- **R1-F002 (archive identity): closed.** The author reports authenticated
  readback that binds `13788584397` to run 42871778928, the delivered
  commit, archive name `aitm-ci-python-a1` and attempt 1, created at
  18:08:33Z (lines 64–68). I withdraw the inference from numeric ID
  ordering. Lines 67–68 correctly make the owning run, attempt, name and
  digest the custody basis. Lines 56–62 now pin all four PR archives and
  the push archive by ID and SHA-256. The PR signed archive
  `13790255902` / `3ab42fd5…` matches #115 line 71. Line 28 requires all
  four same-attempt PR archives.
- **R1-F003 (#103 delivery boundary): closed.** Lines 178–188 state that
  the gate sums only the explicit `policy["helpers"]` files through
  `python_gate._line_totals`. Those helpers exclude `tools/ci/tia/**`, so
  the 778/821 denominator does not change. The author reports a scratch
  replay of 182 tests and 778/821 lines, and a 10,000-line synthetic
  injection that left the denominator unchanged. The design requires
  this to be confirmed at JIT and at the exact head. It also requires
  separate focused evidence (lines 204–207), sends drift or a failed
  floor back to planning or policy authority instead of editing policy
  in T01, and keeps the gate-defining owner disposition and independent
  review.
- **R1-F004 (shared package path): closed.** Lines 175–177 choose the
  implicit `tia` namespace with no initializer, put physical `tools/ci`
  on `PYTHONPATH` and import `tia.baseline`, so "Neither leaf owns a
  common package file". Each leaf can then deliver first without
  touching the other's paths. If #140 later adopted an initializer, its
  own review would have to account for that, but it would not break
  `tia.baseline`.
- **R1-F005 (trust-boundary contract): closed.** Lines 72–93 name the
  closure-owner components: the retained `tools/ci/verify_pr.py` result
  and the push-mode replay of `tools/ci/python_gate.py` with protected
  historical controls. They state that the projection has no
  credentials or network access. They name the input envelopes
  `aitm.tia-ci103-input/v1` and `aitm.tia-baseline-timings/v1` and the
  output `aitm.tia-baseline/v1`. They add rejection of duplicate JSON
  keys before map decoding, of unsupported envelope and receipt schemas,
  and of absolute, aliased or escaping paths. They list the fields that
  #139 and T35 consume. This meets the plan's rules at lines 96–100.

**Round 1 optional suggestions.** The cold row now gives its reason
(lines 150–152). Lines 148–150 explain the wheel-smoke component of the
lane total and define "Python start after event" as attempt-specific job
start minus run creation. Line 54 separates what is reread at JIT from
the frozen historical identities.

**Fresh-read check of the revised text.** I found no new material
issues. The PR evidence and the push-run evidence stay separate roles
(lines 20–45). The trusted PR-base outcomes stay a distinct role (lines
32–33 and 95–97). Both roles stay bound to exact attempt 1, and
cross-attempt artifacts and timings are refused (lines 197–198). The
cold timing slot is an explicit `Unknown` with role, scope and reason,
and the two warm samples are not presented as a cold comparison or as
qualification (lines 146, 151–152 and 158–161). The no-authority
boundary is unchanged (lines 126–129). The 2.5h breakdown still sums
correctly. The refinement has already reproduced the helper collection
and the gate-scope check, so the added custody work plausibly fits the
0.5h readback slot, and lines 213–215 keep the reassessment trigger.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Line 203 adds `PYTHONPATH="$PWD/tools/ci"` and `python -m pytest` to
   the plan's V(module) convention (plan lines 116–118). Say explicitly
   that this is the `tia` namespace refinement of V(baseline), so that
   later `tia` leaves (#139/T02 onward, and #140) use the same invocation
   rather than each drifting on its own.
2. The new module sits outside the gated helper coverage (lines
   181–184). Consider recording the focused run's line coverage for
   `tools/ci/tia/baseline.py` in the delivery evidence (lines 204–206),
   so the trust-boundary code has a measured coverage figure even though
   #103 does not gate it.

## Decision

accepted
