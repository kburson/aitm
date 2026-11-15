[21:37:13]
SOURCE_303: PASS

All four R1 blockers are resolved. The production `src` tree matches R1 (`product_source_matches_first_review: true`), and the only package changes since R1 are in the tests. The signed run passed at head `b01cb13`, with tree `7eba00e` matching the reviewed tree and 1241 tests passing against a baseline of 1215. The focused run passed 25 tests, which matches the count of new qualification and journal cases.

## R1 findings

1. **Physical custody: resolved.** `test_unqualified_physical_custody_cannot_approve_or_read` now covers all six cases I asked for, and each one fails exactly one predicate in `_require_live_source`:
   - **replaced-profile-root:** the pinned root is captured before the rename and copy, so the path still matches but `_pinned(profile.root)` fails.
   - **foreign-profile-root:** `profile.root.path == str(self.root)` fails.
   - **foreign-installation-directory:** the installation's directory no longer equals `approved.directory`, so no installation matches.
   - **replaced-approved-directory:** the approved directory is renamed and copied back after qualification. Approval is refused by the directory-equality check, and the read is refused by `_check_capture_root`.
   - **missing-installation and ambiguous-installation:** `len(installations) == 1` fails.

   Each case asserts the view and `cursor_for` are unchanged. The `previously_admitted` fixture now undoes its shim before the test body runs, so these tests run under the real gate. That also fixes the R1 stale-handle risk.

2. **Codex consent: resolved.** The production `read_source` shows the "no admitted unbounded read" guard is unconditional. It runs before `_approved_candidate(..., observed=True)` and does not depend on `cursor`, so a bounded read cannot reach the call that discloses the decision.
   - The new test runs with and without a cursor. It keeps only the `COPY` permissions, revokes the profile, and makes `read_delta` fail the test if it is ever called.
   - It asserts the guard's own message, `decision is None`, and an unchanged cursor.
   - Because the profile is revoked, any bypass of the guard would surface as a qualification refusal rather than the guard's message.

   The Codex predicate is narrower than Grok's because it requires an unbounded read on the exact stream. It is consistent with Grok on the property that matters: no consent means no decision is disclosed.

3. **Healthy work past a held disable: resolved.** An independent project registration is queued after the held disable. In the same `apply_pending` pass it ends APPLIED with a durable `command_status`. The disable stays in the inbox with `command_status is None`, and epochs and permissions are unchanged. This runs under the real gate.

4. **Final-side check inside the transaction: resolved.** In the before-commit case, the test revokes the profile immediately after `_build_settlement_change` returns, and `assert result[1]` confirms the build actually produced a change.
   - The real gate is restored on the writer instance through `MethodType`.
   - `as_of() == before` and the unchanged cursors prove the refusal happened before commit, so nothing was written, the claims are unchanged and the transaction rolled back. A refusal only at readback after commit would have left a settlement row.
   - The after-commit case still covers retained history and blocks a second retry.

## Nonblocking, downstream

- In the custody test the `read_source` refusal is checked with a bare `LedgerError` and no message match, so it is weaker than the `approve_source` check.
- In the replaced-approved-directory case, no test isolates `_pinned(approved.directory)` on its own. Other checks refuse those paths first, so it works as defence in depth.
- The ambiguous-consent case is not tested: consent for `LIVE` in a different project, or proof that `COPY` holds a permission.
- These R1 items are still open:
  - `verify_boundary` uses a bare dict lookup, so a missing entry raises `KeyError` instead of the typed refusal.
  - `_TARGETS` is a mutable `set` rather than a `frozenset`.
  - The shim still applies to four whole suites.
  - The shim-absence test is still trivially true.
  - Discovery on the disable path still runs before the gate.

The scope items from R1 are still untouched: Epic #2, C01, the live Claude exclusion, no production cutover, the #304 issuer and #300 durability.
