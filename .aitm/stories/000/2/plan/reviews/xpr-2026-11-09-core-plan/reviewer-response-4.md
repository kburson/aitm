---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 4
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0"
artifact_digest: "sha256:cd371fe77a716fde2add99815de7d7285bb69cdee643332794fd29547397f017"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T07:50:07.672Z"
submitted_at: "2026-11-09T07:51:01.521Z"
start_basis: "prior-submit"
start_source: "author-response-3.md"
finding_ids: ["R4-F001"]
answered_finding_ids: []
native_source: "native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-4.md"
native_source_digest: "sha256:80dac47ac2b06bdf988d8d2dda2daf31271b2e08dad329381e914e55be32fbee"
---

Mode: `normal`

## Summary

Round 4 reviews the current plan (digest `sha256:cd371fe7…f017`, 70 leaves / 220.5 h).

- R3-F001 is resolved:
  - C31 (line 745) is re-scoped to trip/pivot/decision, the three wiring points, production resolution and one representative promote/qualifying-stop pipeline. Its 3.5 h estimate is explicitly bounded to that scope.
  - New C70 (3 h, line 1015) owns the C27/C28/C30 real-preflight re-proofs in its own suite, reusing C64 fixtures.
  - The table places C70 after C64 and all of its prerequisites (C31, C27, C28, C30), so ordering is valid. C52 and C59 depend on C70, and C70 is in the C5 manifest.
  - Gate B (line 1244) is pending until C70. The scenario-map row (line 1276) and acceptance row (line 1236) are updated. The sum checks out: 217.5 + 3 = 220.5 h over 70 leaves, all ≤4 h.
- R3-F002 is resolved as written: C59 owns and copies `harness-pytest.ini` and passes `-c … --import-mode=importlib`. However, the chosen location of that ini file introduces one pytest-specific defect (R4-F001).

## Findings

### R4-F001 — Placing `harness-pytest.ini` in `tests/packaging/` and passing it with `-c` stops the copied root and unit conftests from loading

Evidence:

- C59 (line 1161/1165) places the harness configuration at `tests/packaging/harness-pytest.ini` and runs `pytest -c <copied-harness-pytest.ini> --import-mode=importlib` with the explicit suite paths from the manifest. That manifest includes `tests/unit` (the "full guarded unit suite"), `tests/integration/*`, `tests/performance/*` and `tests/platform/*`.
- When `--confcutdir` is not given, pytest sets it to the directory containing the selected ini file (`inipath.parent`), and rootdir is likewise derived from that file. pytest loads `conftest.py` files only from directories at or below confcutdir.
- With the ini file at `<harness>/tests/packaging/`, the following would not be loaded:
  - `<harness>/tests/conftest.py`: C01's import-path setup, which only adds the copied test-package parent.
  - `<harness>/tests/unit/conftest.py`: C01's autouse subprocess/network guards. This is a sibling directory, not a descendant.
- Under `--import-mode=importlib`, pytest does not change `sys.path`, so the copied root conftest is the only thing that makes `tests.support.*` importable. The integration suites (C50/C65/C66/C70) would therefore fail on import. That failure is loud.
- The guard failure is silent: installed-wheel unit tests would run with no subprocess/network trap, and the released C5 manifest would record a "guarded unit suite" PASS that was not guarded.
- The `test_wheel.py` assertion as specified ("effective import mode/config/markers and collected suite names") would not detect either problem.

Failure scenario: C60's released-wheel run reports the full guarded unit suite as passing on both platforms, while a unit test that spawns `git` (exactly what C01's guard exists to catch) passes undetected. Gate D's "no required skip / exact proof" claim then rests on a guard that never ran in the released-artifact lane.

## Required changes

1. R4-F001: Make conftest loading in the isolated harness explicit and verified, using either option below. Then extend `test_wheel.py` to assert, inside the isolated harness, that the root `tests/conftest.py` and `tests/unit/conftest.py` were loaded:
   - Option 1: place the copied harness ini at the harness root, the parent of the copied `tests/`, so its directory is the rootdir/confcutdir and contains every suite path.
   - Option 2: keep the file where it is, but pass `--rootdir <harness-root> --confcutdir <harness-root>` explicitly.

   For example, a deliberately failing probe unit test that attempts a subprocess must be refused, and a `tests.support` import from an integration probe must resolve to the copied path. Update the C59 touched-file path if the ini file moves.

## Optional suggestions

None.

## Decision

revisions-requested
