---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 5
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0"
artifact_digest: "sha256:2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T07:52:37.160Z"
submitted_at: "2026-11-09T07:53:09.783Z"
start_basis: "prior-submit"
start_source: "author-response-4.md"
finding_ids: []
answered_finding_ids: []
native_source: "native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-5.md"
native_source_digest: "sha256:d75518405cdb438195985778311a7007fcf0b043e14ba1c8e4b006dfda295587"
---

Mode: `normal`

## Summary

Round 5 (final permitted round) reviews the current plan, digest `sha256:2106b881…f0dd`: 70 leaves / 220.5 h, all ≤4 h.

The change since round 4 is confined to C59 (line 1165):

- `pytest -c <copied harness-pytest.ini> --rootdir <harness-root> --confcutdir <harness-root> --import-mode=importlib`, where the harness root is defined as the parent of the copied `tests/`. Discovery therefore no longer depends on where the ini file is stored.
- `test_wheel.py` now asserts effective values, not intended arguments, for rootdir, confcutdir, import mode, config, markers and collected suites.
- `test_wheel.py` also asserts that the loaded plugin paths include the copied `tests/conftest.py` and `tests/unit/conftest.py`.
- Disposable unit probes that attempt subprocess and socket access must fail through the guards, with no side-effect marker. They run with the same interpreter, config and flags as the real suites.
- An integration probe must import `tests.support` from the exact copied path.

This fully resolves R4-F001. The C69 `--release-manifest` option, registered in `tests/packaging/conftest.py`, remains below the explicit confcutdir and is unaffected. The touched-file list, dependency graph and estimates are unchanged. The previously verified properties still hold: 220.5 h total, a topological table and ordered shared-path overlaps.

I accept the author's source qualification on R4-F001. pytest's `_is_in_confcutdir` excludes only ancestors of confcutdir, so the sibling `tests/unit/conftest.py` would not necessarily have been dropped. Only the root `tests/conftest.py` was unconditionally excluded. My round-4 statement about the sibling unit conftest was overbroad. The core defect (root conftest and import path excluded, with no verification that the guard was active) was real, and the revision removes reliance on implicit discovery in both directions.

Across the five XPR rounds, all 21 findings have been resolved in the current bytes:

- Round 1: R1-F001…F012 (9 required, 3 optional).
- Round 2: R2-F001…F004.
- Round 3: R3-F001…F002.
- Round 4: R4-F001.

No owner-open decision was resolved by these revisions. Global review-depth/sequence policy, the expansion completion boundary, the second-trip cap, hosted every-push audit, provider/harness details and production adoption remain explicitly open or out of scope.

This acceptance covers the plan's decomposition and bytes at the stated digest for this XPR level only. It does not authorize implementation, issue creation beyond the plan's own leaf-creation procedure, release or production adoption.

## Findings

None.

## Required changes

None.

## Optional suggestions

None.

## Decision

accepted
