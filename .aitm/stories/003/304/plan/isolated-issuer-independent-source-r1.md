[06:01:32]
**SOURCE_304: HOLD**

I used only the supplied artifacts. I couldn't recompute the SHA-256 digests or verify the gate signature, so I checked the gate and local evidence for consistency only. The gate and local evidence agree: the tree matches the reviewed tree, 1290 tests ran with no failures, and coverage figures match.

**What matches the JIT:**
- **Executable custody:** the binary is opened without following the final link, its digest is checked against the closed resolver, and it is copied to a 0500 file with one link. That copy is rechecked by identity, ACL and digest before launch and after exit.
- **Native join:** the hook ties together the envelope, environment, nonce, live child process and its descendants. The carrier requires exactly one successful `hook_execution` followed by one `end_turn` for the same prompt, inside one exclusive session directory.
- **Owner signature and writer seal:**
  - Proposals are rebuilt in canonical form and verified with `/usr/bin/ssh-keygen` against the pinned signer and namespace.
  - Each must be the next generation within a validity window of up to 10 minutes.
  - The stored revision must match the one in memory, the writer seal is applied, and `_publish` runs a custody check before commit.
- **Currentness:** `current()` checks the installation, generation, both expiry clocks, layout and writer root, the native evidence, the stored record and the seal. It catches `Exception` and lets `BaseException` through.
- **Scope change:** the change in `monitor_scope.py` is exactly `observed=bool(batch._admitted)`.
- **JIT conditions:** all three are met in substance. The view is unchanged after revoke, `reserve` is tested unconditionally, and `.decision` is only read on the `prepare` path. Rollback is tested on both the prepare side and after staging.

**Blockers:**

1. **The basis and test count don't reconcile.**
   - The JIT was accepted against trunk `6b64ea8`, but the PR base is `4cfb418`. The diff's line numbers are about 60 lines later than the JIT citations (`_recheck_batch` was cited at :1599 and is now near :1659).
   - The AST test expects #300's `_record_live_exclusion` inside `prepare`.
   - The new file adds 12 tests (`12 passed`), but 1277 + 12 = 1289, not the 1290 reported.
   - Fix: show the lineage `6b64ea8` → `4cfb418` (presumably #300), re-run the admission AST extraction on `4cfb418` and show it matches the accepted digest, and account for the 13th test with a full diffstat.

2. **The native pilot result isn't tied to the reviewed source.** The `native_pilot` record has no log SHA-256, and the runner output has no commit, tree or module digest, so I can't tell which source produced it.
   - Fix: add those to the runner output and record the pilot log digest at head `6870413` / tree `d9823db`.

3. **One required hosted check is missing.** The JIT requires proof that "test fixtures never make a product path issue Codex or Claude." No test covers this.
   - Fix: without any patch, assert:
     - `_approved_pilot_tuple` returns `None` for every digest except `_GROK_DIGEST`, and exactly the Grok tuple for it;
     - `_OpenedExecutable.copy` refuses the fixture binary;
     - after teardown the resolver and collector are the original functions.
   - Also, "a fresh writer starts closed" is only tested with `Registry(writer.root)`. It should close the activated writer, open a new `.writer()`, and assert `_live_profile is None` and that `read_source` is refused.

4. **The reachability AST test has gaps.**
   - It only counts calls inside `ast.FunctionDef`, so calls at module level, in class bodies or in async functions aren't seen.
   - It only scans `aitm-usage/src` and `tools`, not every first-party package.
   - It doesn't catch imports by string (`importlib.import_module`, `__import__`, `getattr` with a constant name).
   - The entry-point check reads only one `pyproject.toml`.
   - The JIT says "any import or call" and "sole first-party caller."
   - Fix: walk whole modules across all first-party sources, and flag string constants naming `_isolated_qualification` or `_install_isolated_profile`.

5. **The four-case assertions aren't exact.**
   - `pytest.raises(_LiveSourceUnavailable)` also accepts subclasses. Add `type(exc) is _LiveSourceUnavailable`, which JIT condition 1 forbids loosening.
   - `validate_source_ref` only proves the references are well-formed. Assert `decision.installation` and `decision.generation` equal the issuer's installation reference and the active profile's generation reference ("exact source and keyed policy/installation identities").
   - `_durable` doesn't read claims back. Add explicit claim and tip readback, or show that `as_of()` advances on every claim commit.

6. **The `_install_isolated_profile` contract differs from the JIT.** The JIT says that function sets `Registry._live_profile` and returns an `_InstallationProof`. Instead it returns an `_Issuer`, and `_Issuer.commit` sets the profile.
   - Fix: either change the code to match the JIT or record a JIT amendment.

**Non-blocking (record or fix):**
- **Revoke isn't final.** After `revoke` (generation 2), a signed `replace` at generation 3 is accepted and reinstalls the profile using the original closure, with no fresh native verification. Making revoke final would be simpler to reason about.
- **The pilot's post-revoke check is loose.** It catches any `_LiveSourceUnavailable`. It should assert the exact type and `decision is None`, so it proves the Grok `decision=None` claim on a real carrier.
- **Revocation isn't ordered against the reserve transaction.** It is serialized with each `current()` call through the issuer lock, but not with the reserve's SQL transaction. A revoke that lands between the final recheck and COMMIT lets that reserve commit, which is correct as of the recheck. Document this against the JIT wording "same writer ordering as a reserve."
- **One failure in the local run hasn't been explained.** `test_corrupt_pair_payload_refuses_routing_without_moving_frontiers` failed once in the candidate run ("native cursor unavailable"). The new test module runs before `test_monitor_*`, so state leaking between tests is plausible. Record the cause; passing on a fresh rerun doesn't explain it.
