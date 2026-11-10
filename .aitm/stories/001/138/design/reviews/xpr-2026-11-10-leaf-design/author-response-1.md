---
schema: "aitm.review-response/v0"
level: "xpr"
story: 138
role: "author"
round: 1
artifact_path: ".aitm/stories/001/138/design/pin-serial-baseline-design.md"
artifact_base_commit: "f7928d15ace3a4949ce67c42da37ea7371e05892"
artifact_digest: "sha256:d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
author_session: "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T18:50:59.611Z"
submitted_at: "2026-11-10T18:55:14.457Z"
start_basis: "claim"
start_source: "native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-review-manifest.md#claim-claim-bb90c805-eba8-4700-9f49-89dca4728373"
finding_ids: []
answered_finding_ids: []
patch: "patch-001.diff"
native_source: "native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-author-response-1.md"
native_source_digest: "sha256:e96516ec2dd80a5ebde8d047e8f649859dfb5678ec354f3b468e91281167ca01"
---

Mode: `normal`

## Summary

Pinned all historical archive identities and the controlled helper-node
inventory. Made the trust-boundary and exact-head delivery contracts
explicit while keeping both leaves independently scoped.

## Finding dispositions

The broker extracted an empty sealed set because round 1 used bold labels
instead of level-three headings. See the five narrative dispositions below.

## Changes made

- R1-F001 resolved. The pinned workflow recorded product node outcomes,
  helper coverage, and helper lane success. It did not record hosted
  helper IDs. The exact PR tested and trunk trees match, and collection
  of the four workflow targets on that tree yielded 182 unique helper
  node IDs. The design requires a controlled, exact-tree advisory helper
  collection with a pinned digest for #139. It is not a hosted proof or
  a substitute for historical helper outcomes. A missing or discrepant
  collection blocks acceptance and #139 pickup pending reassessment.
- R1-F002 resolved. Authenticated Actions archive listings and the direct
  archive endpoint confirm archive 13788584397 belongs to successful
  push run 42871778928, its `a1` artifact, exact head, and the existing
  digest. Its reported creation time is 18:08:33 UTC, after the PR
  archive. Numeric artifact IDs do not track creation time for this
  pair. Pinned all four PR archive IDs and SHA-256 digests as well.
- R1-F003 resolved. The workflow's raw collector scans `tools/ci`, but
  the pinned `python_gate._line_totals` sums only `policy["helpers"]`.
  All four named files predate `tools/ci/tia/`. With the pinned locked
  setup, a scratch full helper run passed all 182 tests and reproduced
  778/821 gated lines. Injecting 10,000 synthetic uncovered statements
  at a new `tools/ci/tia/` report path left that exact denominator
  unchanged. The new tests retain their own exact-head delivery evidence.
  A changed or failing gate blocks delivery and returns to planning or
  existing policy authority. Gate-defining disposition remains required.
- R1-F004 resolved in this leaf. The implicit namespace needs no
  initializer. Set the physical `tools/ci` path explicitly and import
  `tia.baseline`. #140 will use the same invocation convention, with
  its own module and test, in its own review.
- R1-F005 resolved. Named the trusted closure-owner components, the
  versioned boundary and output schemas, rejection rules and downstream
  fields for #139 and T35.

Revised exact custody, proof contracts, helper inventory, delivery,
focused verification and timing definitions. Distinguish both observed
warm samples from an unavailable comparable cold sample and use provider
run creation and job start for the listed latency.

## Declined changes and rationale

None. The push archive ID was retained after authenticated reconciliation.

## Verification

Read the protected workflow, policy and gate code at the pinned trunk
commit. Queried both exact attempts and their artifacts with the GitHub
API. Reproduced the advisory collection and gated helper lines with the
locked Python version on a disposable archive of the historical tree.
Verified the patch with `git diff --check`.
