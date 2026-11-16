[18:01:22]
**SOURCE_335: HOLD**

This verdict rests only on the supplied diff, the visible test bodies, and the authenticated log and CI hashes. I executed nothing.

**What the source supports**
- Condition 1 (receipt domain) is met.
- Condition 2 (pure, lock-free lookup) is met.
- Condition 4 (namespace) is met.
- Condition 5 (keyed tags, checkout dev:ino) is met.
- Exact original scope holds: `grok_mark` requires `envelope.body.request == request`, and the forged `project_id` case is refused.
- The real verified prefix and restart are covered by `test_wrong_pilot_receipt_or_rewritten_verified_event_cannot_apply_scope`.
- Native overlap is covered by `OVERLAP_UNVERIFIED`.

**Hold reasons**

1. **Late revocation guard is not proven inside the custody window.**
   - In `scope_admission.grok_mark`, these checks all run after the body has exited, so they run after `apply_mark` has committed:
     - `lease.check()`
     - `_require_live_source(..., prior=live)`
     - `_grok_mark_proposal`'s post-yield `recheck()`
   - Those checks can only report after the commit. They cannot prevent it.
   - Exclusion therefore depends on `ScopeInboxReader.revoke` serializing on `ControlInbox.publication`. That source is not supplied.
   - `test_grant_revoked_after_native_read_refuses_first_application` revokes only before `grok_mark` is entered.
   - What is needed: the supplied `revoke` lock source, or a regression where a revoke attempted inside the `grok_mark` block is blocked or refused.

2. **A rotated grant is unproven.**
   - `test_read_only_native_lookup_survives_renewal_and_refuses_rotated_or_revoked_scope` covers same-generation renewal and revoke only.
   - No test with a changed grant generation is supplied, although Verification requires "revoked or changed grant".

3. **The physical owner hook has no supplied proof, and condition 8 is unmet.**
   - `_has_process_ancestor(evidence, process, image)` at `packages/aitm-usage/src/aitm_usage/sources/grok_scope_hook.py:37` hardwires `_process_hop`. Condition 8 requires an injectable hop reader.
   - Every visible binding test replaces `_has_process_ancestor` with `lambda *_: True/False`. So none of the real walk has supplied proof:
     - the double read
     - the UID check
     - the zombie check
     - birth order
     - PID ≤ 1 and depth 8
     - the image stat identity
   - There is also no fake-libproc test of it.
   - In `test_original_owner_and_live_process_are_required`, the second case fails because command 33510 was never enqueued. It does not test process substitution.
   - The test bodies after `test_module_accepts_exact_native_input_and_prints_nothing` are not in the packet. The "17 passed" log cannot be credited to tests whose bodies are unseen.

4. **The hook does not recheck the account.**
   - In `bind_grok_prompt`, `confirm()` checks the source ref, proposal digest, checkout and ancestry.
   - It never compares `attempt.profile` with the live profile generation. The spec requires "Recheck private source key and account".
   - As a result, a bind under a rotated account consumes the one-use attempt. Later, `grok_receipt_lookup` and `grok_mark` refuse it, so the one-use persistence is spent without authority.

5. **The hook does not guarantee "always exits 0" (condition 6).**
   - `main` catches a fixed tuple at `packages/aitm-usage/src/aitm_usage/sources/grok_scope_hook.py:93`.
   - `ConflictError` is not listed, and its subclass relationship to `LedgerError` is not in the supplied source.
   - Any other exception escapes with a stderr traceback and a nonzero exit. Examples: `KeyError`, `RuntimeError`, `ImportError`, `AssertionError`.

6. **Condition 7 is not met literally.**
   - `packages/aitm-usage/tests/test_grok_scope_receipts.py:9` uses a redundant alias instead of `# noqa: F401, F811`.
   - Quality passed, so this is low severity, but it is still a stated binding condition.

No gate or control change is proposed. The signed control blobs match the prior verified gate.
