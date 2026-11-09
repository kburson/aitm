<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-4fd804fb61330759842fa8d75f4dedd9"
role: "author"
turn: 4
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_commit: "e4b89a097b49b6abee1ebb1417b21775e3e02e26"
artifact_blob: "7da679cf53afc3ed0e267cd5bc1efb6fb1c286e0"
artifact_digest: "sha256:cd371fe77a716fde2add99815de7d7285bb69cdee643332794fd29547397f017"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  model_display: "gpt-6-astra"
  session_fingerprint: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
  identity_source: "runtime"
started_at: "2026-11-09T07:28:31.068Z"
submitted_at: "2026-11-09T07:52:37.160Z"
finding_ids: []
answered_finding_ids: ["R4-F001"]
acknowledged_supplement_ids: []
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
