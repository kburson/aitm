# #182 independent target-refresh-review

Reviewer **Claude Opus 5.5, medium**. Exact target refresh on November 10, 2026.

# #182 target refresh review (packet only, no tools)

**Verdict: PASS.** The approved #182 scope and JIT can move to literal trunk `a495d60a87ac4ca764f019dc266e579f13f1787e`. Two conditions apply: the fresh locked baseline must pass, and the helper numbers it reports must replace the old ones (see below).

I took three things from the packet as given because I couldn't check them without tools: the ancestry, the two-path diff, and the pickup SHA-256 `f30d0b70…`.

## Changed paths
- Only two paths differ, and both are new files: `tools/ci/tia/snapshot.py` and `tools/ci/tests/test_tia_snapshot.py`.
- Neither file is one the pickup plans to change. The pickup's paths are `scope_admission.py`, `cli.py`, `scopes.py`, the registry lookup/drain seams, `test_monitor_control.py`/`test_scope_admission.py`, `test_codex.py` and `test_claude.py`. Nothing overlaps.
- No product, CLI, native-reader, registry, ledger or inbox code changed. So nothing in the grant, witness, mixed-queue, adoption-record, lock-order or native-grammar design needs a second look.

## Project, command, lock and fixture assumptions
- **Project:** these are the same. The branch is still `codex/aitm-182-scope-command-admission`. The parent plan, section pins, #117 predecessor, M07c dependency and ranks are unchanged.
- **Command:** this is the same. The `aitm-usage monitor scope …` grammar, the five legacy invocations and the exact queued JSON all live in product code, which didn't change.
- **Lock:** the dependency lock is the same. No lock file, project metadata or workflow is in the diff, and the addendum says the workflow is byte-identical. The locked serial Darwin run means the same thing as before.
- **Fixtures:** these are the same. No fixture or existing test-input path changed. The private adoption-record test writer and the M06 wire-byte pins still have the same bases.
- **Budget:** this is the same. The diff adds no work to the 3.75-hour estimate, the 2.25-hour checkpoint or the 4-hour reopen cap.

## Conditions on carrying forward
1. **Product numbers must match exactly.** The fresh baseline must show 748 product and CLI tests and 9,096/9,981 product lines covered. Any difference means something changed that the diff doesn't explain, and the verdict becomes HOLD.
2. **Helper numbers will change, and the new ones must be recorded.** `test_tia_snapshot.py` adds helper tests, and `snapshot.py` adds helper lines. The pinned 182 tests and 778/821 lines will no longer hold. Record the new counts and use the helper coverage floor from the fresh run, not 778/821. Treat a helper-floor regression that comes only from `snapshot.py` as pre-existing trunk state, not as #182 work.
3. **Ruff and whitespace** must pass on the new trunk.
4. **Order:** rebind the Develop branch only after both the fresh baseline and this target refresh pass, as the addendum says. Leave the pickup bytes as they are. The addendum is what records the new target.

I didn't review the #184 behavior itself. The two non-blocking notes from the prior review still apply: run the legacy recheck on every legacy write, not just Claude's, and return ID conflicts and already-finished IDs as a sanitized "unavailable" result.
