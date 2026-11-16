[19:19:29]
**SOURCE_335: PASS**

I executed nothing. This verdict rests only on the supplied diff, the full test module, the product patch, the gate excerpt, the hashes and the signed run metadata.

## Identity and scope

- **Base.** The base is the literal trunk `4ba4354f603ad861c897111dcaaf2342fc68da86` in the JIT record, the local record and the hosted record.
- **Product source is unchanged.** The prior reviewed head `332e4f5c…` and the current head `b36a6d9e…` share the product subtree `f45d9102…`.
  - `scope_admission.py` is `bad9e55e`, which equals the post-image of the reviewed patch (`8a9abc54..bad9e55e`).
  - `grok_scope_hook.py` is `4d27ddaa`, which equals the reviewed new-file blob.
- **Only the test file changed.** The sole change is `M packages/aitm-usage/tests/test_grok_scope_receipts.py` (`ea0e8241..58bd9b46`). The supplied module matches this diff.
- **Local and hosted results agree.**
  - Both report tree `2ffe0024…`, head `b36a6d9e…` and identical product coverage of 14487/15925.
  - Hosted status is `pass`, and `reviewed_tree` equals `tree`.
  - The control blobs (gate, lock, observer, policy, verifier, workflow) are identical to the previously verified gate.

## Prior Hold 1: now resolved in the signed suite

1. **The fake-libproc refusals in `test_process_info_refuses_invalid_custody` are real.**
   - The fixture's baseline row is valid: matching size and PID, PID 33500, euid, status 1, a nonzero start and 37 µs.
   - Each of the seven parameters flips exactly one guard in `_process_hop`: size, foreign PID, PID ≤ 1, UID, zombie (status 5), zero start, and µs ≥ 10⁶.
   - So deleting or weakening any single guard turns that case's return value from `None` into a tuple, and the case fails.
   - `install._libproc` is patched with the class itself, so `install._libproc()` returns an instance, consistent with the existing walk test.
2. **The commit-window test (`test_rotation_between_bind_validation_and_publication_refuses_commit`) is real.**
   - `_store_grok_receipts` resolves `_publish` through the module global, so the patch applies.
   - The revision happens after the first `confirm()` has passed. The only later path that raises "qualification revision changed" is `confirm` acting as `before_commit` inside `_publish`.
   - Three assertions close the window:
     - `invoked == [True]` proves `_publish` was entered;
     - the readback shows `prompt is None`, so no commit landed;
     - `lookup` returns `None`.
3. **Residual (c) is closed.** The rotate branch of `test_grant_change_after_native_read_refuses_first_application` registers generation 2 after the native read. That isolates the failure in `grok_mark`'s `_grok_mark_proposal` seal check ("seal changed"). It also asserts an unconfounded `lookup` of `None` and an unchanged snapshot.
4. **Residual (b) is mostly closed.** The test now asserts that the raw executable path is absent from the receipt bytes and that the PID is not equal to any attempt field value.
5. **Residual (a) is accepted.** The protected gate refuses unregistered skips, so runtime `sys.platform` branching is the policy-compatible form. No gate was changed.

## Residuals (non-blocking, low)

- **a. Some ancestor-walk refusals have no direct test.** From the supplied bodies, no test reaches three refusal branches of `_has_process_ancestor` (`grok_scope_hook.py`):
  - `caller[0] != os.getppid()`;
  - an unstable or `None` hop inside the loop, as opposed to at the caller;
  - `parent == pid`.

  Each still fails closed, either directly or through the depth-8 bound. The prior hold did not list them, so they do not block this candidate.
- **b. The PID check compares whole values only.** It does not do a byte-substring check. The source stores the PID only inside keyed pseudonyms.
- **c. The receipt file has no retention policy.** It has a 1 MiB cap and no retention, and still fails closed for the source key once full. Retention remains with #121.
- **d. Real Darwin ancestry runs only on macOS hosts.** It is exercised only in the macOS branch, so it is backed by the locked local Test rather than by the Linux hosted Test.
