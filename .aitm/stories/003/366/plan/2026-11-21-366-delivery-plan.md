# #366 Scheduled failure flag reader implementation plan

**Goal**

Give a maintainer and an agent a read-only way to check the same published advisory.

**Scope**

[Story](../story.md), [epic plan](../../362/plan/2026-11-21-362-delivery-plan.md), accepted #364 storage receipt and delivered #365 writer. Target `trunk`. Bind the reader to #365's delivered schema and issue identity at JIT.

**Files**

Extend `tools/ci/scheduled_sweep_flag.py` and `tools/ci/tests/test_scheduled_sweep_flag.py` from #365. Register added test IDs in `tools/ci/category_sweep_catalog.tsv`. Add the check and stable issue link to `docs/ci.md`.

## Tasks

- [ ] Confirm the writer's parser, target binding and canonical URL derivation. Specify `python tools/ci/scheduled_sweep_flag.py check` and `check --json` for the human and agent modes. Share one validated record in both formats and document its as-of timestamp.
- [ ] Add focused tests for active with the exact run/attempt link and timestamp, clear, and unavailable on missing, malformed, conflicting, uninitialized or unreachable storage. Check that clear and active both return successful read status, unavailable returns a distinct nonzero status, and neither mode performs a write. Run `uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest tools/ci/tests/test_scheduled_sweep_flag.py -q` and observe the expected missing-reader failures.
- [ ] Implement the check using the delivered storage adapter; avoid a second format or store. Explain in `docs/ci.md` how to open the issue and retrieve machine output. Identify the as-of limits if a slot or publisher update is delayed. Keep the interface informational.
- [ ] Rerun the focused tests and reconcile the new catalog entries against collection. Compare rendered issue, human check and machine output against an isolated record for controlled active/clear/unavailable cases, and read the deployed issue for a real scheduled run. Open the story PR and obtain canonical CI, trusted verification and independent Grok PR review of the current candidate. Verify and sign off delivery. Hand the deployed evidence and replay to the epic for acceptance.
