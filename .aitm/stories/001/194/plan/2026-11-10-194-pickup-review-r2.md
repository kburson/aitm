# #194 independent pickup review, round 2

Reviewer **Claude Opus 5.5, high**. Off-platform exact pickup on November 10, 2026.

# PASS: #194 M07c revised pickup re-review

I used only the packet and no tools. I didn't recompute the SHA-256 `a835da08…de5c3`.

## First-round blockers

1. **Installed upgrade fixture: resolved.**
   - **Old starting state:** the test builds the old runtime through the normal verified install path. Only the generator is swapped to the retained old one, and the receipt is not hand-written. Then the test restores the default and re-reads. This produces a genuine old receipt that `_read_runtime` must select from.
   - **Second digest:** the `_wheel` code shows that `directory = parent / suffix` and `wheel.comment = suffix`. The digest is the SHA-256 of the whole file, so two suffixes under one parent give two different digests with the same control root. They also go to separate `{version}-{digest}` runtime and retained-wheel paths. "Test-only root redirection only" still holds.
   - The 0.9 h checkpoint now includes this buildability check, which closes the gap I flagged in the estimate.
2. **Verification order: resolved.**
   - The order is now explicit: receipt and schema, then wheel custody, then the executable hash, then the interpreter hash. Only after that does it run `_interpreter(base)`, derive the site, select the variant and compare the full launcher. This matches the current code, where both digests are checked before `_interpreter(base)` runs.
   - A RED test refuses a mismatched interpreter before the version probe.
   - An unknown digest that matches a mutated launcher passes the early file-hash check. It is still refused because selection finds no generated variant with that hash.
3. **Pinning sites: resolved.** The pickup now lists every site:
   - `_prepare` generates and pins the new bytes.
   - `_read_runtime` selects the old or new bytes.
   - `_probe_runtime` passes the selected bytes to `_inspect_surface`. Today `_inspect_surface` calls `_launcher(python, site)` itself, which is the hidden third site. After the change it receives bytes instead.
   - No site may regenerate after selection, and `_runtime_for` still goes through `_read_runtime`.

## Baseline and estimate

- **Baseline:** the exact numbers are recorded (867 product and CLI tests, 182 helper tests, 9,638/10,538 and 778/821 lines) against trunk `4986524`. The locked serial gate is reused, so the prerequisite is met.
- **Estimate:** 1.75 h. The allocations add up (0.45 + 0.55 + 0.40 + 0.35). The checkpoint now gates the riskiest piece, and the four-hour reopen cap is kept. That's sound.
- **Platform scope:** running the shell fixture only on Darwin is acceptable for this leaf. `${VAR+"…"}` is plain POSIX, and the Linux carrier/host gates are separate with no workflow changes. The remaining risk is that dash is unproven until those gates run. That's accepted.

## Non-blocking notes for Develop

- The packet doesn't show the code that admits a second 0.1.0 wheel with a different digest on the `upgrade` route. The pickup asserts it, and the checkpoint should confirm "accepted by upgrade", not just "buildable". If it fails, that is a reserve or reopen decision, not a redesign.
- Swap the generator with `monkeypatch` or a context manager, so the default comes back even if the old-runtime setup fails.
- Patch the generator symbol that `_prepare` uses. After the change `_inspect_surface` only receives bytes, so patching there would do nothing.
- Confirm the new launcher stays well under the 8192-byte read limit in `_read_runtime` when paths are long.

**Verdict: PASS.**
