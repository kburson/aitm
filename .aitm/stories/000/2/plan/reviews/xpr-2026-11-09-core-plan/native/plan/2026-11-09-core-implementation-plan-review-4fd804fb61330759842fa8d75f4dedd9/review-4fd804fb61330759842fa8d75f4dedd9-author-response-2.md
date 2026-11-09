<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-4fd804fb61330759842fa8d75f4dedd9"
role: "author"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_commit: "b9c4998482b5a87788279b5d3c52f87bc99e0461"
artifact_blob: "30d4f40b5308eb4a1d462e9fbe7fcfd2d9ae22f6"
artifact_digest: "sha256:ec134886ca97a5163848b6396c9bcc037eafe0ca4abd48ac5f0d22985e8d3796"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  model_display: "gpt-6-astra"
  session_fingerprint: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
  identity_source: "runtime"
started_at: "2026-11-09T07:28:31.068Z"
submitted_at: "2026-11-09T07:46:23.013Z"
finding_ids: []
answered_finding_ids: ["R2-F001","R2-F002","R2-F003","R2-F004"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Accepted all three required findings and the optional clarification. The plan remains 69 leaves / 217.5 h, all ≤4 h. Revised test composition and import ownership make predecessor suites remain executable after later production wiring.

## Finding dispositions

| Finding | Disposition | Resolution |
| --- | --- | --- |
| R2-F001 | accepted | Established a global stable negative-vector rule: deliberately unregister the required slot/module in explicit test composition, never assert permanent absence in the evolving default graph. Applied it explicitly to C04/C06/C11/C12/C17/C28. C10/C12/C14/C31/C35/C43 prove their actual production registration in their own owned test files. Predecessor suites remain unchanged and unskipped. |
| R2-F002 | accepted | C04 declares that every pre-C31 attempt-bearing producer uses the typed test-only fixture, naming C27 reconcile, C28 transitions and C30 expansion. attempt reconcile and expand both use normal category and require preflight; no stop/recovery exemption. C27's in-process MemoryBackend proof stays in unit; C30 real CLI uses explicit fixture composition. C31's own integration suite repeats C27/C28/C30 behavior with actual production preflight, including local/shared expansion construction failure, competing clone, lost ACK and second/nested stops. |
| R2-F003 | accepted | C01 owns root tests/conftest.py, tests and subpackage markers, and importlib-mode configuration in its existing pyproject allowlist. Qualified tests.support/tests.packaging imports use only the resolved harness parent, reject a foreign tests package, and never add src/editable core paths. C64 consumes that path. C59 copies all required markers/conftest/support files, preserves import mode and checks helper modules resolve to the copied harness while aitm_core resolves to the installed wheel. |
| R2-F004 | accepted (optional) | C49's init --local nominal walk explicitly asserts publication N/A. Separate named test_default_publication_pending uses a remote-configured disposable store for default publish/lost ACK. Added the distinct scenario-map row. |

## Changes made

No decomposition, estimate or dependency change was necessary. C01 gains bounded test-package scaffolding under its existing 3.5 h estimate, not a new runtime feature. Changed the interim proof convention from time-dependent absence to deliberate unavailable-capability fixtures and positive later production registration. No owner-open choice was resolved, no code implemented, no leaf issues created and no global configuration changed.

## Declined changes and rationale

None. No deferred finding or unresolved required change.

## Verification

Parsed all 69 table/section pairs again; 217.5 h, all estimates ≤4 h, 231 dependency edges topological. All 161 normalized overlapping touched-path pairs remain ordered. git diff --check passes. Checked every named missing-port and later wiring leaf plus C27/C28/C30/C31 proof ownership and the new test import paths. Raw FUR SHA-256: 327af4d64a202e06183491be50b620786681df8dd73f6a0d0265a262f8c7f5be. No product tests were run. Round 3 must review the full current file, including all prior and new sections.
