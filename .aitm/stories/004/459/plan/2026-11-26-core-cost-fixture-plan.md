# Core Cost producer fixture qualification implementation plan

> **For agentic workers:** Use the executing-plans skill and complete steps in order.

**Goal.** Build a deterministic planning export and qualify it against the approved C44 receiver fixture.

**Architecture.** Reuse #458's exact report reopen, pinned input reader, request arithmetic and rate digest validation. Adapt immutable public receipt rows to the existing v1 wire format and carry uncovered provenance in a separate, digest-bound sidecar. Use the unchanged SQLite receiver fixture to prove replay, correction and ambiguous readback.

**Tech stack.** Python 3.13, standard library, Git, installed `aitm-effort` wheel and pytest.

**Spec.** [Refined design](../design/2026-11-26-core-cost-fixture.md).

## Global constraints

- Review base `0f8c6ff70b5112bd3a17af3a2ab5665e347a416c` and fixture blob `9257c7ec948468e8251dcc987ae89bea52f495f5`. Validate the exact fixture digest at pickup and delivery.
- Scope is an authorized project UUID, story, exact artifact/report pair, planning input pin, window, reviewed rate digest and dedicated 32-byte pseudonym key. No mutable Git ref fallback, live receiver, #51 changes, board write, or Actual/monitor policy changes.
- Preserve legacy v1 export bytes and raw #458 envelope bytes. Keep the receiver fixture unchanged and test story/window lanes independently.
- Write JSON with canonical LF and no optional timestamps. Limit bounded inputs via #458 and emitted bundle to 32 MiB. Use explicit UTC cutoff micros, exact Decimal string and normalized wire enums.

## Review focus

1. An internally consistent forged report fails byte reconstruction from the planning pin.
2. Real #461 remains held and its known subtotal remains visible. Missing phase or actor yields pending scope. Unsupported providers and disputed or withdrawn rows are retained as gaps.
3. Stable source identity and compatible corrected/repriced snapshots do not duplicate accepted usage.
4. Confirmed digest, verified absence and conflicting receiver state lead to distinct outcomes after reopening SQLite.
5. Scope pseudonyms and original labels are closed, reproducible and free of private paths, secret material or native actor identifiers.

## Task 1 — Derive and normalize exact evidence

**Files.** Extend `packages/aitm-usage/src/aitm_usage/effort/pinned_inputs.py` with an internal `scope_authority` tuple of attempt, approved-phase candidate and actor, returned from already-validated timing joins. Preserve existing `timing` dictionaries and serialized report outputs. Add `effort/core_export.py` and `tests/test_effort_core_export.py`.

**Interface.** `build_core_export(repository, artifact_commit, project, story, report_id, rate_card, scope_key) -> dict[str, bytes]`. Returns the v1 `manifest.json`, `usage.jsonl` and `provenance.json`. A bad pin or key raises `EffortError`. Each source row uses the existing public HMAC identity, exact receipt revision, scope join, existing wire enums and #458 turn API comparison for complete, bounded observations. Match report receipt descriptors and keep exclusions defensively separate. Emit the API comparison in the v1 row price only when available and in the provenance subtotal separately. Price is independent of scope admission. On a same-cutoff rate-only change the fixture accepts the new snapshot under a different rate basis, keeps the original accepted row bytes, and records exactly one reconciliation item per changed accepted source. Replaying either snapshot is duplicate.

- [ ] Add red tests for positive closed pinned Git-derived rows, foreign artifact, byte-valid forged report, deterministic retries, exact #458 envelope preservation, unpriced, missing/ambiguous scope, open, mixed, duplicate evidence and excluded coverage, unsupported Grok, preserved client/model provenance, stable source under revision/rate changes, exact integer cutoff, 32-byte key and privacy canaries.
- [ ] Run `uv run --locked pytest -q tests/test_effort_core_export.py` and observe the adapter test fail for the missing entry point.
- [ ] Implement the adapter. Validate rate bytes, rebuild before trusting content, and use closed source fields only. Include a per-row wire hash and status, normalized aggregate count, and SHA-256 of the two receiver files in the sidecar. Never copy timing labels or native source paths. Withhold scope unless the verified join carries one unambiguous recognized phase and actor.
- [ ] Run `uv run --locked pytest -q tests/test_effort_core_export.py tests/test_effort_pinned_inputs.py tests/test_effort_pinned_report.py` in the package and confirm green.

## Task 2 — Public command and unchanged receiver parity

**Files.** Extend `effort/pinned_cli.py` and `effort/cli.py`, `packages/aitm-usage/README.md` and `tests/test_effort_core_export.py`.

**Interface.** `aitm-effort --project UUID story-core-export STORY REPORT_ID --repository PATH --artifact-commit SHA --rate-card FILE --scope-key FILE`. Stdout is a canonical `aitm.story-core-export-bundle/v1` object with a `files` object mapping the three fixed names to exact UTF-8 file contents. Public input errors exit 2 with the existing sanitized CLI error path. Read the scope key at most 33 bytes. Require exactly 32 bytes without trimming. A key plus newline is invalid. Use a fixed sanitized error for unreadable input. The key and its path stay private. Refuse an over-limit bundle before stdout with exit 2 and `Core export bundle exceeds its byte limit`. Translate unavailable export report pins into the command's exit 2 while preserving report reopen exit 3.

- [ ] Write parity cases materializing the exact files to a disposable directory and importing them with the named fixture. Verify replay, late second source, changed revision and same-cutoff rate-only change, partial/pending, conflicting immutable payload, retained acceptance after omitted disputed input, and transaction rollback. Drop the first acknowledgement in a controlled fixture run, open a fresh receiver and compare the accepted digest with SHA-256 of the original v1 row. For absence prove transaction rollback, read the absent key in fresh receiver, then resend the identical row. Missing/untrusted readback never qualifies acceptance.
- [ ] Rebuild the identical pin and rate with a different scope key. The original same-cutoff fixture lane rejects the changed scope as a different usage projection, preserves original accepted bytes and records no new acceptance. Verify key newline rejection, no-path stderr, and zero bytes on stdout for an oversized bundle.
- [ ] Run the new CLI test and observe red for an unregistered command. Add CLI and documentation.
- [ ] Run `uv run --locked pytest -q tests/test_effort_core_export.py tests/test_effort_pinned_inputs.py tests/test_effort_pinned_report.py tests/test_export.py tests/test_monitor_recovery_fence.py` and confirm green. The unchanged legacy suite includes byte determinism and receiver replay. List all new node IDs in `tools/ci/category_sweep_catalog.tsv`. Verify the fixture SHA.
- [ ] Verify locked package tests, Ruff and installed wheel smoke. Push the isolated implementation branch and open the trunk PR.
- [ ] Read back GitHub Actions on the exact head, including portability. Obtain independent source review and an authenticated trusted verifier pass.
- [ ] Merge through normal trunk protection. Verify ordered merge parents and delivered tree.

## Task 3 — Live-input fixture proof and closeout

- [ ] With the delivered wheel, export the protected #461 report from #458 with a dedicated local fixture key. Compare repeated bundle bytes and selected receipt digests against the exact #461 handoff pair. That pinned artifact records open coverage and $0.1754084 known subtotal. It provides three pending observations and zero accepted scoped observations. Run the positive closed and adversarial cases in disposable receiver storage.
- [ ] Record the exact pair, original report and wire SHA, fixture pins, outcome matrix and compatibility limits for #230. Link producer handoff to #230 after verified delivery. Publish Agent Cost with explicit Unknowns and sign-off, set the linked PR, verify issue closure and Project Done.
