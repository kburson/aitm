[21:20:23]
SOURCE_303: HOLD

I reviewed only the supplied diff. This session has no file or shell access to the #303 checkout, so the findings below come from the diff hunks and the hosted and local receipts you supplied.

## Findings

1. **The physical-root and installation custody checks have no tests.** In `monitor_registry.py`, `_require_live_source` adds these checks, and no test in `test_monitor_qualification.py` makes any of them fail:
   - `_pinned(profile.root)`
   - `profile.root.path == str(self.root)`
   - `item.directory == approved.directory`
   - `_pinned(approved.directory)`
   - `len(installations) == 1`

   JIT step 3 requires "changed root" and step 2 requires "wrong/missing installation, foreign root". The only installation mismatch tested is a different build string; lease loss and cross-writer proof are covered.
   - **Action:** add a parametrized test for each of these cases:
     - the profile root is replaced at the same path;
     - the profile root points at another registry path;
     - the installation directory is a sibling of the approved directory;
     - the approved directory is replaced after approval;
     - there is no matching installation;
     - there are duplicate matching installations.

     Each case should refuse `approve_source` and `read_source` with the view, cursor and receipts unchanged.

2. **Codex and Grok disclose a typed exclusion under different consent rules.**
   - `_read_grok` computes `observed=any(source_read_allowed(...))`.
   - `read_source` passes `_approved_candidate(..., observed=True)` unconditionally on the Codex path.

   The guard above it is visible only as "no admitted unbounded read". If that guard is conditional on `cursor is None`, a bounded Codex read discloses a decision without verified consent. The JIT's "wrong-project consent refuses" case is not tested.
   - **Action:** compute `observed` for Codex with the same predicate as Grok, or show that the guard is unconditional.
   - **Action:** add a Codex test where consent exists only for another source or project, and assert `decision is None`.

3. **No test shows healthy queued work continuing past a held disable.** `test_revoked_capture_keeps_payload_dependent_disable_pending` queues only the one disable. JIT step 4 requires "plus independent healthy queued work", and the recovery contract says later commands on an independently healthy edge continue. The rejected-enable test does have a later same-edge command, but nothing covers the held (BoundaryUnavailable) path.
   - **Action:** queue an independent edge or command after the held disable in the same `apply_pending` pass. Assert that it is APPLIED while the disable stays pending with `command_status is None`.

4. **The new final-side check inside the transaction is untested.** The diff adds `_require_batch_qualification` inside `_require_settlement_side`, which is binding condition 4. The only refusal before commit that is tested is the stale retry, and that one already fails at the first gate.
   - **Action:** under the real gate, revoke or supersede between `_build_settlement_change` and the second `_require_settlement_side`.
   - **Action:** in the same scenario, assert that no settlement row is written, the claims and `cursor_for` are unchanged, and the transaction rolls back.

## Strengths

- **No issuer in the product.** `_live_profile` starts as `None` and no product code ever assigns it. There is no environment variable, flag or loader that grants it. The shim lives in `tests/conftest.py`, applies only when a test opts in, and is undone after each test by `monkeypatch`.
- **Currentness check.** The gate requires the exact lease identity, the pinned root and the exact tuple, including build and format. It runs the `current()` verifier on every check, accepts only `current is True`, and confirms the profile is the same one after the verifier returns. Re-checks compare the earlier proof by identity (`prior.profile is profile and prior.installation is installation`), so a superseded profile, a revoked profile, a missing verifier or a new writer all refuse.
- **Approval and live reads.**
  - Live Claude refuses because it is not in `_TARGETS`.
  - `_approve` checks before the identity loop, so a refused approval gets no ID.
  - Codex and Grok both check before `read_delta`, check again after the read, and keep the proof in memory with `compare=False`.
- **Capture commands.**
  - The enable check comes after the earlier-pending check, so an earlier disable keeps its priority. A refused enable is re-raised past the held handler, so it ends as REJECTED.
  - A disable that would need an excluded read is translated to `BoundaryUnavailable` at the `_make_arm` site. Nothing new is raised in the first try block.
  - A refused enable doesn't hold its edge, and later commands on that edge still run.
- **Boundaries and the journal.**
  - The capture frontier is checked before and after, and `verify_boundary` and `_require_direct_proof` bind to the frontier's proof.
  - `_recheck_batch` gates reserve and the current==read.progress retry.
  - The readback after commit checks again before each prefix is reopened. A stale retry can neither add a second row nor report success, and `as_of` and `cursor_for` still read the durable history.
- **Privacy.** Approve and enable refusals carry `decision=None`, and the exception message is generic.

## Remaining risks (not blocking)

- **The shim bypasses the gate in four whole suites.** `pytestmark` applies it module-wide to the registry, scope, control and journal suites, and it returns a bare `object()`. Those suites therefore can't catch a regression where reading archive, expiry or history starts to need a grant. Today only `as_of`, `cursor_for`, `view` and `command_status` are checked with no profile.
- **`verify_boundary` uses a bare dict lookup.** It indexes `self._boundary_qualification[key]` directly, so a missing entry raises `KeyError` rather than the typed refusal. Using `.get(...)` and raising `_LiveSourceUnavailable`, as `_require_direct_proof` does, would make them consistent.
- **`_TARGETS` is a mutable `set`.** A `frozenset` would fit the immutable contract better.
- **Discovery isn't gated on the disable path.** `locate` and `_locator_lost` still run discovery before the gate. That matches existing behavior that proves a locator is lost.
- **The `previously_admitted` fixture leaves a stale handle.** It passes a `monkeypatch.context()` that is undone as soon as the fixture returns into `NativeJournalFixture`, so any patch the fixture made through it disappears.
- **The test-boundary check is trivially true.** `test_substrate_shim_is_absent_from_the_installed_package` only checks for a module that never existed.

Scope is preserved: Epic #2, C01, live Claude exclusion, no production cutover, the #304 issuer and #300 durability are all untouched.
