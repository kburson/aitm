# #118 independent target refresh review

Claude Opus 5.5 at medium effort issued the conditional verdict below on the exact old and new target. The detached locked baseline matched all stated conditions. The helper collection explicitly names tools/ci tests and excludes the new dashboard test by scope.

**Verdict: PASS (conditional).** The approved M08a pickup and split can carry to literal trunk `679c328204ab797aabdc9a9f93fbf1085d03bb65`, but only if the fresh locked baseline on the clean detached copy matches exactly:

- 877 product and CLI tests
- 182 helper tests
- Ruff and whitespace clean
- 9,649/10,549 product lines
- 778/821 helper lines

Any difference in counts or coverage turns this into a **HOLD**.

**Why it carries:**
- The new trunk descends from the accepted base `c4ea6b0`.
- The three changed paths are new files under `tools/story_dashboard/`. None of them overlap #118's source seams (`monitor_journal.py`, the private store module, `monitor_registry.py` lease expiry, `monitor_scope.py` diagnostics retention) or its tests.
- The workflow, package and `tools/ci` diffs are empty, so the M08 authority, the M08b predecessor to #119 and the out-of-scope list are unaffected.
- The pickup's own `c4ea6b0` target and old baseline sentence stay as written to keep its SHA-256 (`5483…e58f`). The refresh note retargets the candidate, hosted checks and review to `679c328`.

**One gap to resolve before calling the baseline a match:**
- The refresh says "tests … are byte-identical", but one of the three added paths is a test file: `tools/story_dashboard/tests/test_evidence.py`. The packet doesn't say whether the helper gate collects `tools/story_dashboard/tests` or measures coverage over `tools/story_dashboard/`.
- If it doesn't, 182 and 778/821 should hold exactly, and PASS stands.
- If it does, the helper count and coverage will change. Under your rule that's an unexplained discrepancy and a **HOLD**, until the packet states the helper gate's scope and records the new expected numbers.
