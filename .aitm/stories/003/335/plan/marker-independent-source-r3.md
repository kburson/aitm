[18:24:44]
**SOURCE_335: HOLD**

This review uses only the supplied diff, test bodies, issuer and grant excerpts, and the supplied hashes and logs. I executed nothing.

## Prior hold reasons against current source

| # | Prior reason | Status |
|---|---|---|
| 1 | Late revocation outside the custody window | **Resolved.** `grok_mark` holds `ControlInbox(writer.root).publication()` for the whole body. The supplied `ScopeInboxReader._invalidate` (revoke/withdraw) and `register` (rotation) take the same lock. `test_first_application_holds_the_revocation_publication_lock` pins the same inbox inode and gets `BlockingIOError` on `LOCK_NB` while the mark applies. The lookup stays lock-free: it succeeds under a held publication lock and leaves the tree metadata unchanged. |
| 2 | Rotated grant unproven | **Resolved for the hook.** `test_source_approval_profile_and_command_witness_do_not_transfer` registers generation 2. `bind` then fails with `seal changed`, raised in `_grok_mark_proposal` before any qualification check. See residual (c). |
| 3 | Hop reader hardwired; real walk unproven | **Partly resolved.** See Hold 1. |
| 4 | Account not rechecked by hook | **Resolved within the stated bound.** At staging, the qualification record ref is read between two `_require_live_source` calls, so it is tied to the live generation. `confirm()` compares it before the bind and again as `before_commit`. Replace and revoke before bind are refused and leave the attempt unbound. The comparison grants no authority. A race with the issuer's separate lock yields denial, because lookup and `grok_mark` require `live.profile.generation`. It does not yield a stale binding. |
| 5 | Hook may exit nonzero | **Resolved.** `main` catches `except Exception` and returns 0. The test covers an unexpected `RuntimeError`, duplicate keys, oversize input, and missing or mismatched env, all with empty stdout and stderr. The wheel smoke also shows exit 0 with empty output. |
| 6 | Literal noqa | **Resolved.** `test_grok_scope_receipts.py:9` reads `# noqa: F401, F811`. |

## JIT conditions

- **Conditions 1, 2, 4, 5, 6 and 7 are met in source and tests.** This includes:
  - the verified prefix recheck (`prefix changed`) and the restart cursor refusal;
  - `OVERLAP_UNVERIFIED`;
  - both forge orderings;
  - wrong-owner and forged `project_id` refusal.
- **Condition 3 is met in source.** The walk starts from `getppid` with a double read. It checks UID, zombie status, birth order, PID ≤ 1, depth 8, a stable hop before and after, and the image stat ref. `OSError` propagates, which fails closed.
- **Condition 8 is not met.** See Hold 1.
- **Locked local and signed hosted runs match.** Both cover head `332e4f5c…` and tree `db93f38e…`, and the control blobs equal the prior verified gate.

## Hold reasons

1. **Required custody and commit-window proofs are outside the delivered suite and the signed hosted run.**
   - Two proofs exist only in the out-of-tree `test_335_exact_adversarial_checks.py`, which is labelled "outside the signed suite":
     - the `_process_hop` refusals for size, foreign PID, init, UID, zombie, no start, and microseconds;
     - the proof that a rotation between bind validation and `_publish` refuses the commit (the `before_commit=confirm` path).
   - Condition 8 requires the cross-platform tests to cover every branch. In-suite, the fake-libproc tests reach only the `_process_hop` success path. In-suite qualification tests cover only revision *before* bind.
   - The same-UID and zombie refusals and the commit-window guard are central custody claims. They need retained regression coverage under the signed hosted Test.
   - Fix: move both tests into `packages/aitm-usage/tests/test_grok_scope_receipts.py`, which is writable, then rerun locked local and signed hosted Test.

## Residuals (non-blocking, low)

- **a.** Condition 8 says the real libproc tests should be "marked macOS-only". `test_platform_native_process_custody_has_no_provider_request` instead branches on `sys.platform` at runtime, with no marker.
- **b.** The receipt-privacy assertion checks that there is no `"pid"` key. It does not check that the PID value `33503` or the image path is absent from the bytes. The source stores neither.
- **c.** A rotated grant at first application (`grok_mark`) is not isolated in a test. The lookup assertion after rotation is confounded, because the earlier `f.revise("replace", 2)` already makes it `None`. The shared `_grok_mark_proposal` seal check covers it in source.
- **d.** The receipt file only grows and has a 1 MiB cap with no retention policy. Once it reaches the cap, staging fails closed permanently for that source key. #121 should own retention.
