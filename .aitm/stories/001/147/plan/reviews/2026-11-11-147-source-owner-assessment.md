# #147 independent exact-source assessment for owner disposition

**Reviewer** Codex / story141, independent of author Codex / story147.
**Reviewed at** 2026-11-12 02:24:46 UTC.

**Verdict** Hold owner disposition for two important input binding gaps. This is a preflight source assessment. The independent post-verifier Review gate has separate evidence.

| Identity | Observed value |
| --- | --- |
| Repository, PR, target | `kburson/aitm`, [PR #261](https://github.com/kburson/aitm/pull/261), `trunk` |
| Base and sole parent | `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` |
| Candidate and branch tree | `a9f97f937369192b6f565f6d5cec1e26340358ab`, `b3aef9e5f6b75aa987f443bc6133d5a243147011` |
| Exact changes | `tools/ci/tia/controls.py` blob `55c0de689374eed8e8c4787391e27f3a32c4aa06`, raw SHA-256 `dbd056f07842e245d09c02a1feee72d5ad79b0cd5d03957881adc12b76f00b4e`; `tools/ci/tests/test_tia_controls.py` blob `c1da9558c7f36ea94fb25353640de2b09e4b1a15`, raw SHA-256 `282dffff9172b001dd6158338d116bf8d8824a07155f42ed546e46f2d9080d50`. |
| Accepted Plan and JIT | Planning `4a56ad67541ae17d9b90fd05d633124711ed210a`, Plan SHA-256 `08d5840595fa108bae1929e7d36ca3cba1425b507432652bfad36eb1d7917af9`, JIT SHA-256 `f70f836effa5e66c30acc0be0f53ca38a19501a62511055748f47d7b389300c2`. |

## Important findings

1. **A control edit can clear approval on an incomplete full scope.**
   `tools/ci/tia/controls.py:341` accepts any nonempty normalized lane
   tuple for a syntactically valid workload label. I exercised the
   real #140 hosted Git fixture with a changed CI policy path,
   declared workload `full`, only the product lane, and distinct
   matching decisions. The disposition returned `full_required=True`,
   `hold_reason=None`, and both approval references. The full flag
   remains set, but the accepted leaf requires the approval to bind
   the complete applicable lane set. A partial set mislabeled as
   `full` should hold even when both records exactly match that
   incomplete scope. Check the full workload's independently expected
   profile/platform pairs and owners before binding approval. At this
   pinned policy both `ci-helpers/darwin-apfs` and
   `product-cli/darwin-apfs` are required. Add a focused refusal with
   the candidate scope and both approval records consistently partial.
2. **The full reference admits malformed nested collection provenance.**
   `tools/ci/tia/controls.py:642` checks presence of the observer,
   controls and per-scope receipt keys and compares lane identity.
   It never checks those provenance values. In a disposable test
   fixture, canonical bytes with all three values set to null and a
   matching raw digest still yielded a derived full inventory with
   null provenance. T02's actual v1 projection rejects that shape at
   `tools/ci/tia/inventory.py:544`. Exact raw binding protects bytes,
   and validation must still refuse a reference that cannot be a
   canonical T02 full projection. Apply the existing observer and
   receipt digest and control identity shape requirements and exercise
   the case with a matching digest.

## Other assessed behavior

The candidate projects both raw-byte endpoint trees through the
trusted #103 classifier and finite nested configuration extension,
preserves both rename endpoints, checks the projected diff against
the exact snapshot entries and binds both distinct decisions to the
exact source and control digests. The replay checks its independently
supplied path against both endpoint points, exact step order, row
digests and complete lane equality for each delivery/review binding.
It preserves mandatory rows, child and capability obligations,
existing skip constraints and the helper sources in the qualified
reference. Both genuine fixture inputs use the delivered T02/T03 APIs.
Source review of caller authentication, protected-target history
acquisition and runner observation stays with the downstream adapter,
as the accepted design requires.

Independent focused invocation on the exact candidate, with locked
CPython 3.13.9 and a private uv environment and pytest base directory,
passed 41 tests in 11.61s. The two additional checks above were
read-only defensive checks with disposable fixture data. The branch
and target identities were read back separately. The observed local
results supply neither hosted proof nor an owner decision.
