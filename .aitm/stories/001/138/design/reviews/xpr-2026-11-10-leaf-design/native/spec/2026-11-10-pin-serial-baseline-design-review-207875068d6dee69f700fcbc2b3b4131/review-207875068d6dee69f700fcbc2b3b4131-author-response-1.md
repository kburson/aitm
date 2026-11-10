<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-207875068d6dee69f700fcbc2b3b4131"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/138/design/pin-serial-baseline-design.md"
artifact_commit: "f7928d15ace3a4949ce67c42da37ea7371e05892"
artifact_blob: "6b881112d3a589ada6b74415a242aa56fa81d6a6"
artifact_digest: "sha256:afc748d5a3f07ecd92be59c5866af3fc919548d79f338380b750790be8dfeeb2"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  model_display: "gpt-6.1-sol"
  session_fingerprint: "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
  identity_source: "runtime"
started_at: "2026-11-10T18:47:51.319Z"
submitted_at: "2026-11-10T18:55:14.457Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
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
