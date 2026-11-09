<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-4fd804fb61330759842fa8d75f4dedd9"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_commit: "b9c4998482b5a87788279b5d3c52f87bc99e0461"
artifact_blob: "30d4f40b5308eb4a1d462e9fbe7fcfd2d9ae22f6"
artifact_digest: "sha256:ec134886ca97a5163848b6396c9bcc037eafe0ca4abd48ac5f0d22985e8d3796"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
  identity_source: "runtime"
started_at: "2026-11-09T07:29:06.774Z"
submitted_at: "2026-11-09T07:41:56.563Z"
finding_ids: ["R2-F001","R2-F002","R2-F003","R2-F004"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Round 2: full re-read of the current `core-implementation-plan.md` (1306 lines, digest `sha256:ec134886…3796`), not only the delta.

Verification of the round-1 dispositions:

- R1-F001: C04 Produces now includes `AttemptPreflight`/`OperationCategory` with not-applicable/unavailable/fixture vectors. C01 enumerates the slot, C28 uses a declared fixture and C31 re-runs C28 with the real preflight. Resolved, but see R2-F001/R2-F002 for consequences the fix introduced.
- R1-F002: `uv.lock`/`pyproject.toml` are owned C01→C03→C53 and serialized in the table. Resolved.
- R1-F003: C01 owns `cli/catalog.py` (a fixed route table), every `__init__.py` and `reducers/`. C09/C28 dispatch roles are distinguished. Resolved.
- R1-F004: C01 installs the `tests/unit/conftest.py` guards, and C52 measures from the performance lane. Resolved.
- R1-F005: C69 owns the checker, the `--release-manifest` conftest option, fixture/live suites and `core-post-release.yml`. C60 has separate fixture and post-publication commands. Resolved.
- R1-F006: C11 owns `--planning-branch`/prompt/collision rules/non-default ref end to end, and the CLI map and C67 assert it. Resolved.
- R1-F007: C64–C68 split the qualification work, and C69 takes the checker. Re-checked the arithmetic: the 69 rows sum to 217.5 h, all within 2.5–4 h, and the table remains topological (C64 after C43; C67/C68 after C49; C52/C59 after C65–C68; C69 after C53; C60 after C69). Resolved.
- R1-F008: all seven named contracts now appear in Produces. Resolved.
- R1-F009: C28 is in the integration lane. Resolved.
- R1-F010–F012: the strategy path is pinned by SHA-256, `cli/outcomes.py` is removed and paths are deduplicated. Resolved.

I also re-checked the shared-file overlaps for the new leaves. C64 `tests/support/shared_store.py`, the C65/C66/C67/C68 suite files, C69 `tests/packaging/*` and `core-post-release.yml`, and C60 `docs/release/*` are either unique or ordered (C53→C60 for `core-m1.md`).

Three residual defects remain:

- R2-F001: the interim "unavailable until later leaf" assertions conflict with the plan's own rule that dependency suites are re-run and CI runs whole directories.
- R2-F002: the fixture-preflight allowance covers only C28, but C27 and C30 also run attempt-bearing commands before C31.
- R2-F003: the shared test-support module introduced by C64 has no owned import path.

## Findings

### R2-F001 — Interim "unavailable" assertions become false when the later wiring leaf lands, and that leaf cannot edit them

Evidence:

- Several leaves now specify assertions whose truth depends on time, through the default production composition:
  - C28 (line 700): "Separately assert a default production attempt-bearing command returns preflight-unavailable before C31".
  - C17 (line 486): "until C43 installs the runner, report pending/unavailable".
  - C06 (line 322): "until C10 is installed, such history stays fenced".
  - C11 (line 442): unavailable hook steps "remain reported" until C12.
  - C12 (line 456): doctor's lane probe until C35.
  - C04 (line 292): "WriteAuthorizer absence likewise refuses production writes before C14".
- After C31, C43, C10, C12, C35 and C14 install their implementations into `services.py`, the default composition is no longer missing those slots. Any such assertion written against default production composition then fails.
- The plan requires those suites to keep running:
  - Step 4 of the common cycle (line 73) runs "relevant dependency contract suites".
  - C59 `core-ci.yml` (line 1273) runs "the full unit and integration directories".
  - C60/C59's installed runner executes the C5 manifest.
- The wiring leaves cannot repair them. C31's allowlist (line 740) does not include `tests/integration/test_c28.py`. C43 (line 886) does not include `test_c17.py`. C10 (line 422) does not include `test_c06.py`. Likewise for C12/`test_c11.py` and C35/`test_c12.py`.

Failure scenario:

1. C28 delivers a passing `test_c28.py` that asserts preflight-unavailable on the default composition.
2. C31 installs the real preflight. Running "relevant dependency contract suites" now fails `test_c28.py`.
3. C31 cannot change that file within its allowlist. It must either edit outside scope, mark the test skipped (forbidden by line 78), or replan.

The same pattern recurs at C43, C10, C12, C14 and C35. It surfaces as red CI in C59 if missed earlier.

### R2-F002 — The declared fixture-preflight allowance covers only C28, though C27 and C30 also drive attempt-bearing commands before C31

Evidence:

- C04 (line 292): "attempt-bearing implementation mutation without installed AttemptPreflight reports unavailable ... Until C31, C28 uses an explicitly injected typed fixture preflight". Only C28 is named.
- C27 (line 684, before C31) requires "CLI attempt reconcile persists those facts". `reconcile_attempt` attaches evidence to a live attempt and is attempt-bearing by definition.
- C30 (line 728, before C31) requires "Real expand in local-only and shared stores tests construction failure, competing clone and lost ACK". Expansion consumes the live origin attempt's allowance and pauses its clock, so it is attempt-bearing.
- C04's category list (`normal, authored_sync, stop_reconciliation, recovery`) does not say whether `attempt reconcile` or `expand` is exempt from preflight.
- C31's re-run obligation (line 744) covers only "C28 real pipeline-order, advisory provisional-attempt and reconcile cases". C30's real expand is never re-proved with the installed preflight. C65 `test_expansion_completion_fence` covers fencing races, but not C30's construction-failure/lost-ACK expand cases.

Failure scenario: the C30 implementer runs real `aitm expand` on an attempt-bearing origin through production composition. Per C04 it returns preflight-unavailable, so the required positive proof cannot pass. The implementer must either invent an undeclared fixture exception (a silent contract fork, which line 60 prohibits) or classify `expand` into a category that skips preflight. The latter would let a second/nested expansion bypass the C31 trip check that expansion is supposed to be subject to. The same choice faces C27 for `attempt reconcile`.

### R2-F003 — The shared test-support module has no owned import path or pytest configuration

Evidence:

- C64 (line 1004) adds `tests/support/shared_store.py`, and C50/C65/C66 consume it from `tests/integration/*.py`. C59 (line 1150) copies `tests/support` and the conftest files into the isolated runner.
- No allowlist creates `tests/__init__.py`, `tests/support/__init__.py` or a root `tests/conftest.py`. No leaf states pytest configuration such as `[tool.pytest.ini_options] pythonpath`/`--import-mode`. C01 owns `packages/aitm-core/pyproject.toml` but its test text does not mention pytest configuration.
- The only conftests are `tests/unit/conftest.py` (C01) and `tests/packaging/conftest.py` (C69). Under pytest's default `prepend` import mode with no `__init__.py`, each test file's own directory is put on `sys.path`. So `tests/integration/test_shared_store.py` cannot import `tests/support/shared_store.py` without one of those mechanisms.
- The same applies, more weakly, to `tests/packaging/release_checker.py` and `installed_runner.py`, which are imported by sibling test files. Those work only because they are in the same directory.

Failure scenario: C64 adds an unlisted `tests/conftest.py`/`__init__.py` or edits C01's `pyproject.toml` pytest configuration, both outside its allowlist and with no serialization edge against C03/C53 on `pyproject.toml`. Alternatively, C50/C65/C66 each work around the import differently. C59's isolated runner then has to reproduce whichever ad hoc path was chosen outside the source tree.

## Required changes

1. R2-F001: Rewrite every interim-unavailable assertion so it stays true after the later wiring lands. Target an explicit test service composition with the named slot deliberately unregistered, not "default production" composition. Apply this to C04 (WriteAuthorizer/AttemptPreflight), C06 (ForwardRepairVerifier), C11 (hook step), C12 (lane probe), C17 (PendingActionRunner) and C28 (preflight). Have each wiring leaf (C10, C12, C14, C31, C35, C43) assert the production composition now resolves its slot, in its own test file. Alternatively, add the predecessor test file to each wiring leaf's allowlist with a serialization edge, and state that the wiring leaf flips that assertion. Either way, state the rule once in the File and interface map paragraph (line 60).
2. R2-F002: State which operation category `attempt reconcile` and `expand` use, and whether preflight applies. `expand` must remain subject to trip preflight. Extend the declared fixture-preflight allowance explicitly to C27's CLI reconcile and C30's real expand, or to every pre-C31 attempt-bearing producer by rule. Add C30's real local/shared expand cases, with the installed preflight, to C31's re-run obligation, or to a named C65 scenario.
3. R2-F003: Assign ownership of the test import path:
   - Option 1: C01 adds a root `tests/conftest.py` (or `[tool.pytest.ini_options] pythonpath = ["tests"]` in its owned `pyproject.toml`) and documents the import-mode choice.
   - Option 2: C64 adds `tests/support/__init__.py` plus the required parent-package marker to its allowlist, with any `pyproject.toml` edit serialized in the manifest chain.

   In both cases, C59's runner copies whichever file provides the path.

## Optional suggestions

### R2-F004 — Separate C49's publication-pending check from the local-only walk

C49 (line 1094) puts "Verify promote without --push attempts default publication and reports retryable pending after simulated ACK loss" inside `test_complete_cli_walk`. However, the accepted design's nominal walk is `init --local`, where publication is "not applicable" (design CLI section and walk). Name a separate remote-configured case, for example `test_core_walk.py::test_default_publication_pending` using a disposable remote, so the local-only walk can still assert publication N/A without conflicting with this check.

## Decision

revisions-requested
