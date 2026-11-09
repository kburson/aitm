---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "author"
round: 4
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0"
artifact_digest: "sha256:2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  effort: "xhigh"
author_session: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T07:51:01.521Z"
submitted_at: "2026-11-09T07:52:37.160Z"
start_basis: "prior-submit"
start_source: "reviewer-response-4.md"
finding_ids: []
answered_finding_ids: ["R4-F001"]
patch: "patch-004.diff"
native_source: "native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-author-response-4.md"
native_source_digest: "sha256:25aa7eb37bfb80d70c933eda5858bbe4d44348ea9118e352a99a7519190ce6b4"
---

Mode: `normal`

## Summary

Accepted the explicit isolated-harness boundary and active-guard verification change. The plan remains 70 leaves / 220.5 h, all ≤4 h.

## Finding dispositions

| Finding | Disposition | Resolution |
| --- | --- | --- |
| R4-F001 | accepted | Chose option 2: C59 retains its owned ini fixture but passes explicit --rootdir and --confcutdir at the parent of copied tests/, alongside -c and importlib mode. test_wheel checks effective values and loaded root/unit conftest paths. Disposable subprocess/socket unit probes must fail through the guards with no subprocess marker, and an integration import must resolve to copied tests.support. The same interpreter/config/flags apply to the real suites. |

## Changes made

Made the harness discovery boundary independent of the ini storage location and required proof that root loading and unit protections are active, beyond checking intended options. This is a bounded addition to C59's existing installed-runner qualification; no new runtime implementation, dependency or graph edge.

Technical qualification: [pytest's current primary source](https://docs.pytest.org/en/stable/_modules/_pytest/config.html) confirms the default confcutdir derives from the selected ini directory, and ancestor conftests can therefore be excluded. Its _is_in_confcutdir predicate does not categorically exclude all sibling hierarchies, so the review's claim that the sibling unit conftest necessarily disappears is broader than the source establishes. That does not weaken the accepted root-loading defect or the need to verify both protections explicitly. The revision avoids relying on either implicit discovery behavior.

## Declined changes and rationale

No requested change declined or deferred. The narrow source qualification above preserves accuracy without removing any requested proof.

## Verification

Reviewed the exact C59 command, copied path assertions and expected-failure guard probes against the current pytest source. Reparsed the plan: 70 leaves, 220.5 h, 238 topological dependency edges; all 161 overlapping touched-path pairs ordered. git diff --check passes. Raw FUR SHA-256: 2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd. No product test execution is claimed. Round 5 is the final permitted round and must review the full current plan; any unresolved required finding will remain unaccepted rather than exceeding the cap.
