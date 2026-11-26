# Pinned story effort and cost reports implementation plan

> **For agentic workers:** Use the executing-plans workflow for the ordered implementation below. Steps use checkbox syntax.

**Goal.** Build, publish and reopen one exact story effort report. Emit eligible #181 Cost evidence from verified complete coverage.

**Architecture.** Use the shipped session store to export a sanitized coverage roster, immutable Git objects for the reporting boundary, a versioned request-pricing card, and a canonical envelope with frozen JSON and text. Publish only validated envelopes through the protected planning writer, then register their discovery pairs. Costs and independently evidenced timing retain separate authority.

**Tech stack.** Python 3.13, SQLite, Git, Decimal, pytest and the existing portable `aitm-effort` distribution.

**Spec.** [XPR-reviewed design](../design/2026-11-25-pinned-story-effort-cost.md) · [Design XPR](https://github.com/kburson/aitm/commit/f2491859).

## Global constraints

- Target `trunk` from verified base `87bc3d8a2875884014b59281117f68b9d63fabee` via `codex/458-pinned-story-reports`. Revalidate exact base, required checks and applicable project instructions before pickup.
- Use full immutable planning commits, expected project UUID and story, UTC occurrence window `start < end <= cutoff`, exact reviewed rate digest, and the report ID and containing commit for reopen. No checkout, branch name or clock-dependent fallback in the reader.
- Validate normal tree modes and canonical wire shapes. Limit inputs to 2 MiB per blob and 64 MiB cumulative, and the envelope to 16 MiB. Keep native IDs, source paths, private keys, raw transcripts and unrelated story evidence out of the output.
- Preserve shipped receipt, report, legacy and monitor pricing contracts. The only initial estimate card is GPT-6.2 Sol Standard. Its exact evidence and per-request short/long comparison formula receive review. Additional model pricing is outside this implementation plan.
- Notify the #459 workflow of the frozen input contract through the delivered plan and evidence. Existing #181 Cost authority, Actual timing and #230 Core live qualification apply.

## Review focus

1. Old pins or late/withdrawn receipts cannot age into a complete Cost result or alter an older report. Task 2 and Task 4 exercise this.
2. A caller-provided roster may not erase missing evidence or use an arbitrary empty scope to qualify Cost. Task 1 and Task 5 exercise closed/open admission, explicit zero-work declaration, and exact expected/observed reconciliation.
3. Coverage, native overlap/timing and pricing must remain independent. Task 3 tests scope gaps, insufficient clocks, partial usage, category reconciliation and pricing band edges.
4. A report identity, path or pin can be substituted separately. Task 2 and Task 4 verify closed schemas, digest-contiguous revisions, independently checked envelope/request identities and fail-closed reopen.
5. A stale or ambiguous planning update can misregister a report. Task 5 verifies scoped identity, no-op replay, collision hold and exact readback before registration.

## Task 0 — Gate and pickup

- [ ] Verify the design XPR, seal this plan XPR, and publish its verdict. Reflect Refine, Ready for Planning and Planning against the accepted scope. The agreed owner delegation authorizes objective readiness decisions within that scope.
- [ ] Before Develop, pin the current protected trunk base and applicable workflow/check matrix, confirm the source checkout's instructions and record pickup. Add exact new test IDs to the authoritative shard inventory as the tests are introduced. No implementation task starts before the plan and pickup gates pass.

## Task 1 — Portable coverage record and scoped export

**Files.** Add `packages/aitm-usage/src/aitm_usage/effort/pinned_coverage.py`, extend `effort/session.py` and `effort/session_cli.py` only at their existing boundaries, and add `tests/test_effort_pinned_coverage.py`.

**Interfaces.** `SessionStore.coverage_snapshot(sessions, story)` takes explicit enrolled session handles and returns one transactionally consistent view across enrollment, effective observations, retained revisions, pending callbacks and conflicts. `session-export-coverage STORY --session UUID [--session UUID ...] --window-start UTC --window-end UTC --cutoff UTC --admission {open,closed} [--admission-evidence FILE] [--supersedes SHA256]` serializes schema `aitm.story-effort-coverage/v1`. Use the same opaque public-attempt mapper used by `public_receipts`. Carry scope, effective dispositions and digest-linked supersession. For closed admission require a validated explicit caller evidence file binding authorized project, story, window, cutoff, exact enrolled session set, and evidence digest to the attested closed dispatch set. An empty selection can qualify only through an explicit verified no-work attestation. Include timing joins by digest and existing registered evidence reference only when available.

- [ ] Write red tests for one SQLite snapshot, distinct opaque attempts, story-switch retention, open and closed admission, exact zero and missing proof, explicit pending/missing/withdrawn/disputed and bounded unattributed evidence, collision, and no private sentinel output.
- [ ] Implement bounded export and strict canonical validation. Keep enrollment coverage and native price evidence separate. Let unresolved state hold the candidate until reconciled rather than assuming a missing receipt is pending or no work.
- [ ] Run `uv run --locked pytest -q tests/test_effort_pinned_coverage.py tests/test_effort_session.py` in the package, verify red then green and commit this slice.

## Task 2 — Pinned Git evidence reader

**Files.** Add `effort/pinned_inputs.py` and `tests/test_effort_pinned_inputs.py`. Reuse receipt path/scope validation and the existing sanitized Git execution boundary where compatible.

**Interfaces.** `read_inputs(repo, project, story, planning_commit, window) -> PinnedInputs` provides canonical selected receipts, immutable evidence descriptors, resolved coverage and explicit gap codes. Validate the full commit identically after resolving it with replacement objects disabled. Enumerate target story receipt paths and, for identities present in the target, check placement uniqueness. Read only target evidence blobs. Match coverage records through `core.evidence.recorded` with kind `story-effort-coverage` and exact scope/window/cutoff/path/digest. Resolve one verified supersession chain; missing/invalid evidence and conflicts have distinct dispositions.

- [ ] Write red tests for malformed paths, special modes, foreign story/project, duplicate identities and cutoff-crossing lineage; registered digest mismatch, missing and unregistered coverage, conflicts and withdrawal, old pins, exact cutoff and window edges, oversized inputs.
- [ ] Implement strict Git tree discovery and exact contiguous previous digest validation. Separate full-chain validation from eligibility selection. Report explicit excluded reasons. Report only the pinned subset when coverage cannot reconcile it to the expected set.
- [ ] Run `uv run --locked pytest -q tests/test_effort_pinned_inputs.py tests/test_effort_session_publication.py`, verify green and commit.

## Task 3 — Report arithmetic and reviewed rate threshold

**Files.** Add `effort/pinned_amounts.py`, a versioned resource under `aitm_usage/rates/effort/`, and `tests/test_effort_pinned_amounts.py`. Reuse exact Decimal arithmetic, public receipt counters and #443 rollup semantics.

**Interfaces.** `load_comparison_rates(path, expected_sha256)` verifies the closed Standard USD model/card shape and exact bytes. `summarize(inputs, rates) -> dict` computes measured and expected turn coverage, timing and separately known token and monetary columns. Preserve complete, partial and unknown independently for each measurement. The additive engagement result requires verified actor/clock and scoped wait evidence. Always give known per-turn native durations where valid.

- [ ] Write red tests for per-column partial groups, verified zero, duplicate/disputed/inclusive exclusions, interruption, separate provider Grok ticks and explicit Unknown billing, insufficient timing boundaries and the positive registered timing case.
- [ ] Verify exact rates on the [official GPT-6.2 Sol model page](https://developers.openai.com/api/docs/models/gpt-6.2-sol#pricing). Pin canonical card bytes, provider source, cutoff and the card digest in the reviewed rate evidence. Retain a dated sanitized rate extract with its own digest so review can reproduce the card when the website changes. Test 272,000 and 272,001 per-request input boundaries, two short requests whose sum crosses the threshold, per-request reconciliation, and unknown unsupported model/cache/tier cases. The price means a Standard list-price comparison even when actual processing tier is unknown.
- [ ] Implement and run `uv run --locked pytest -q tests/test_effort_pinned_amounts.py tests/test_effort_report.py tests/test_effort_trail.py`. Commit after green.

## Task 4 — Reopenable artifact and public CLI

**Files.** Add `effort/pinned_report.py`, extend `effort/cli.py` and the package README, and add `tests/test_effort_pinned_report.py`.

**Interfaces.** `build_pinned_report(inputs, rates) -> bytes` outputs canonical `aitm.story-effort-report/v1` with versioned manifest, JSON bytes, frozen text and individual digests, deriving its report ID from the payload before the ID field is attached. `reopen_pinned_report(repo, artifact_commit, project, story, report_id) -> envelope` reads `.aitm/stories/<bucket>/<story>/attachments/effort/reports/<report_id>.json` and verifies id, schema, story/project, component digests and frozen output without rebuilding. `aitm-effort --project UUID story-report-build STORY --repository PATH --planning-commit FULL_SHA --window-start UTC --window-end UTC --cutoff UTC --rate-card PATH --rate-sha256 SHA256` writes the canonical envelope. `aitm-effort --project UUID story-report-open STORY REPORT_ID --repository PATH --artifact-commit FULL_SHA --format {json,text}` reopens the selected frozen output. Success is 0, invalid arguments/input are 2, and a well-formed reopen request whose pinned artifact is missing, corrupted or unsupported is 3 with a stable unavailable reason. The existing commands retain their database requirements.

- [ ] Write red tests for deterministic build, separate-process byte-identical JSON/text reopen, corrupted and missing artifact, renderer update, foreign project/story, overbound envelope, late receipts, repricing, withdrawal and attempts to reopen a newer artifact at an earlier pair.
- [ ] Implement envelope, operator-facing output and failure semantics. Validate every serialized field and receipt/rate pin. Add CLI argument tests for missing or malformed required flags, invalid input versus unavailable results and all existing entry points.
- [ ] Verify `uv run --locked pytest -q tests/test_effort_pinned_report.py tests/test_effort_report.py`. Commit after green.

## Task 5 — Safe publication and existing Cost intake

**Files.** Add `effort/pinned_publication.py`, `effort/pinned_cost.py`, and `tests/test_effort_pinned_publication.py`. Use the existing dashboard qualification tests for compatibility where a cross-package boundary can be exercised.

**Interfaces.** `publish_pinned_report(repo, authorized_remote, envelope) -> (report_id, artifact_commit)` uses temporary-index nonforced Git writes, exact path containment, bounded refresh/retries and SHA readback. Before discovery registration, return the verified report ID and containing commit. The package's `prepare_report_registration` validates the exact remote readback and parses the pinned story event stream, then returns a closed `core.evidence.recorded` fact of kind `pinned-story-effort-report` for the authorized planning coordinator to append and publish in a subsequent ordinary Git commit. Payload includes project UUID, story, report ID, full artifact commit, report path and SHA-256, planning input pin, window, cutoff and rate digest. Actor and recorded time use the existing story event envelope. Use the verified report ID and original artifact commit as the lookup pair. An existing byte-identical binding returns no new event. A conflicting binding for the same ID or a publication readback mismatch holds. Independent reports at a different input pin or rate digest retain their own IDs. A missing registration leaves exact-pair reopen available from the writer's verified result. The coordinator links the registered pair in the story planning record. This plan does not add an automatic discovery reader. `cost_candidate(envelope, selector, operator_verification) -> receipt_or_hold` returns a compatible `aitm.story-usage-receipt/v1` artifact only for a user-authorized exact report selector with reconciled, closed coverage and original #181 verification fields. Verify report source digest, story, project slug mapped to pinned UUID, revision and window before producing the candidate.

- [ ] Write red tests for protected local-replica publication, stale retry and readback, unchanged replay, collision, private path leakage, deterministic registration replay, same-ID conflict, readback mismatch and partial Project Cost hold. Run `complete_cost_projection` and `partial_cost_hold` through the actual #181 reader. Verify Actual remains sourced to its independently registered receipts.
- [ ] Implement the writer and Cost adapter without adding a board writer or privileged release route. No automatic assertion of live completeness.
- [ ] Run the new focused tests with `tests/test_effort_session_publication.py` and the existing `tools/story_dashboard/tests/test_usage.py` from the repository root. Commit when green.

## Task 6 — Required review, hosted validation and live report

- [ ] Run package tests, lint, wheel smoke, authenticated hosted CI and three-platform effort fixture checks. Use the trusted verifier and an independent source reviewer on the exact head/base/tree. Record reviewer and CI receipts before merging through the authorized path. Verify the delivered tree.
- [ ] Before choosing the #461 reporting pin, the implementing coordinator reviews the distinct prior #461 run authorizations and exports the bounded available roster with the delivered wheel. Publish the sanitized coverage file and its exact `story-effort-coverage` registration through existing planning authority. Establish a closed admission set only when the scoped dispatch evidence supports it. If custody is partial or the original store is unavailable, record the proved evidence as open or unavailable with precise scope and reason, and retain a Cost hold. An observed subtotal remains a valid real demonstration. Verify the evidence tree, then choose that exact planning pin and cutoff.
- [ ] With the delivered wheel and existing planning writer, build and publish the #461 example from the verified pin. Reproduce the known Sol Standard subtotal from exact per-request evidence. Verify the complete Cost fixture and publish the real example's actual Cost disposition. Verify two fresh-process representations, unchanged replay, exact manifest, plan and publication commit. Register the report in a follow-up planning checkpoint.
- [ ] Add final evidence, sign-off and the per-turn Agent Cost table with explicit unknowns. Link the PR on Project 24, verify delivery, then close #458 and mark Done. Verify issue, Project status and planning state.
