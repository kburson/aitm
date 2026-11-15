[22:45:25]
**JIT_304: HOLD**

**What passes**
- **Pilot and executable.** The one real positive mode is macOS arm64 Grok CLI 1.0.77 / `50ca579fa996`, and its digest matches #115. The plan launches a private copy of the binary from runner-owned custody, which is the route accepted at Refine. It also rechecks the digest and dev/ino before launch and after exit. The build/tuple comes from the closed digest record, not from `client_version`.
- **Native join.** The pilot joins `hook_execution` to `end_turn` under a one-use nonce and a pinned private `GROK_HOME`. It claims only `ScopeState.read_source` and no Grok journal cursor, which is correct.
- **Call chain.** The cited chain matches the supplied code. `_reserve` (`monitor_journal.py:1249`) calls `_fresh_view` twice inside `transaction(write=True)`, and also on the `current == read.progress` path. That leads through `_journal_view` (`monitor_scope.py:2606`), `_recheck_batch` (`:1598`) and `_require_batch_qualification` (`:1587`) to `_require_live_source` (`monitor_registry.py:660`), which calls `current()`.
- **Constructors.** `Registry.__init__` and `writer()` (`monitor_registry.py:512`) always start with `_live_profile = None`.
- **Held modes and scope.** The three held modes (Codex Desktop macOS at #128, Codex CLI Linux and Grok Linux at #129) are each named with the proof they still need. Docker is excluded as a signed target. Epic #2, C01 and production cutover are excluded.
- **Time.** 0.8 + 0.9 + 0.8 + 1.0 = 3.5h, under the 4h cap.

**Blockers**

1. **A checker that raises can still skip the refusal (Refine #5).** The plan catches only `LedgerError`, `OSError`, `ValueError`, `AttributeError` and `RuntimeError`. `TypeError`, `KeyError`, `IndexError`, `OverflowError`, `struct.error` and `ctypes.ArgumentError` from the private checker would still skip the refusal branch. Refine already named this gap ("other exception types outside the caught set"). Cancellation is not a reason to keep the list narrow: `KeyboardInterrupt`, `SystemExit` and `CancelledError` are `BaseException`, so catching `Exception` inside the checker would not mask them. The fix is a checker that never raises past `Exception`, plus hosted controls that inject `TypeError` and `KeyError`.

2. **Reserve and retry can refuse without the exclusion decision Refine #5 requires.** On the reserve/retry path the call passes `prior=` without `observed`, so the code raises `_LiveSourceUnavailable(None)`. Refine requires "a refusal with an exclusion decision". The plan instead hands this to "#300 journal classification" but cites no call site. The supplied evidence doesn't show how `_reserve`'s caller classifies a refusal with no decision. The plan must either produce the decision or cite exactly where that refusal is consumed.

3. **The externally authored currentness is not actually external.** The record is described as owner-authenticated, yet it is authenticated "with the writer's existing private source evidence key". No separate owner credential or verifier is named. There are also no separate domains for an owner proposal and a committed writer revision. As written, a proposal and an effective revision can't be told apart cryptographically, and "owner-authored" reduces to "writer-keyed". The plan must name:
   - the owner key and how it is provisioned;
   - the proposal domain and the committed-revision domain;
   - who verifies each.

4. **The seam for the hosted revoke/retry tests is unnamed and contradicts itself.** The plan says hosted tests use "the real issuer" with a Codex native fixture. It also says the digest-to-tuple record is closed and product issuer mode is closed to Codex. The real issuer therefore can't produce a Codex `_InstallationProof` without a seam that injects a tuple. The plan must name that seam and show it only exists in the test tree, so product and runner code can't reach it. Without this, the transactional revoke/retry proof doesn't rest on the real issuer.

5. **No test proves the install route is unreachable (Refine #6).** `_isolated_qualification.py` ships inside the installed `aitm_usage` package. The plan asserts there is no CLI, factory wiring, service entry or loader, but names no hosted control that checks it. That control should cover:
   - no product module imports it;
   - no entry point references it;
   - only the runner calls the profile install function.

Fixing blockers 3 and 4 adds design work inside the 0.9h and 1.0h items, so the 3.5h estimate needs re-confirming against the 4h cap after the amendment.
