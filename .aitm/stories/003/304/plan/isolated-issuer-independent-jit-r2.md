[22:49:00]
JIT_304: HOLD

**Closed in R2**
- **R1 #1 (exception breadth): closed.** `current(installation)` now catches `Exception` and returns `False`, while `BaseException` still propagates. Hosted tests inject `TypeError` and `KeyError` at the real reader, and the gate stays `current is True` (`monitor_registry.py:660`).
- **R1 #3 (owner vs writer authority): closed.** There are now two separate keys with separate jobs:
  - The owner's disposable Ed25519 key is made with `ssh-keygen` and stays in the runner's control directory. It signs proposals under the namespace `aitm-isolated-owner-proposal-v1` for a fixed principal, and the issuer checks them against the pinned public key.
  - The writer seals each committed revision with `pseudonymize("isolated-issuer-revision-v1", …)`.
  - Neither key can stand in for the other. The writer checks both before activation, and every hot-path call re-checks the current state.
- **R1 #4 (test-only seam): closed.** The seam is named: `_approved_pilot_tuple`, plus the host collector. Both are monkeypatched only inside a disposable fixture in `tests/test_isolated_qualification.py`. No runtime override, loader, optional argument or exported fixture exists, and the Codex fixture runs the real signature, revision, issuer and `Registry` code.
- **R1 #5 (reachability): closed.** An AST test finds every import or call of `_isolated_qualification` or `_install_isolated_profile`. Further checks cover the CLI entry points, confirm `tools/qualification/isolated_grok_pilot.py` is the only outside caller, and confirm a normal `Registry.writer` starts closed. The code matches: `Registry.__init__` and `writer()` (`:512`) always set `_live_profile = None`.
- **Estimate: passes.** 0.8 + 1.1 + 0.8 + 1.1 = 3.8h, under the 4h cap.
- **No gate changes: passes.** The checks in `_require_live_source` and the `_reserve` transaction stay as they are. Inside `_reserve` (`monitor_journal.py:1249`), `_fresh_view` runs on every path, including retry when `current == read.progress`, and again before commit, all inside `transaction(write=True)`.
- **No fabricated decision on lost lease or root: matches the code.** `self.lease` raises before the decision branch, and an unpinned directory leaves the decision as `None`.

**Remaining blocker (R1 #2 is only partly closed)**

1. **The reserve/retry decision depends on a field that isn't in the evidence.** R2 makes the decision with `observed=bool(batch._admitted)` in `_require_batch_qualification` (`monitor_scope.py:1587`). But nothing supplied defines `VerifiedScopeBatch._admitted`: not where it is set, what it holds, or why it is only true for a batch whose admission was authenticated and consented. The nearest thing supplied is `_admitted_readers`, which returns a `frozenset[UUID]`, and no shown code links it to the batch. That field alone decides the plan's claim that "a foreign, unauthenticated or unconsented batch cannot get a decision." The identity and view checks only rule out foreign batches. The amendment needs to:
   - either cite where `_admitted` is set today or declare it a new field and say exactly where it is filled and what it holds;
   - list every caller of `_require_batch_qualification` and `_recheck_batch`, not just `reserve` and `reserve_batch`, and say what `observed=True` changes for each. In particular, say whether a prepare-side caller would now record an exclusion it didn't record before.
   - add hosted tests where an unadmitted batch gets `_LiveSourceUnavailable(None)` and an admitted batch gets the decision, on both the first reserve and the same-progress retry.
