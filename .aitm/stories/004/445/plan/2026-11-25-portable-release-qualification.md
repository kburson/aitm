# #445 portable effort release qualification

The [approved implementation plan](../../426/plan/2026-11-24-agent-effort-cost-implementation-plan.md) defines the release gates. Codex implements and coordinates delivery. The target is `trunk` from `e4c41649f6ccdba33396cf9af46d5cf98102c842`. GitHub confirmed all nine predecessors Done.

1. Add an installed-wheel fixture target on GitHub-hosted Linux, macOS and Windows. Test the exact PR merge with Python 3.13.9, the locked development tools, and an isolated dependency-free wheel. Exercise portable imports, the console entry point, store, capture, adapters, rollups, reports, and AIPR fixtures. Windows qualification is fixture coverage.
2. Use a private, disposable project with the configured Codex, Claude Code and Grok Build headless routes. Run a same-provider child story and a cross-provider epic including that child. Check exact native counters independently of the report. Freeze the canonical export, restart SQLite with a pending refinement, then settle and replay without another provider invocation. Record overhead, gaps and privacy evidence.
3. Publish the provider and host matrix. Include the earlier interactive evidence and its limits, unqualified live Windows, billing and Codex sealed-review coverage. Preserve existing sandbox and AIPR authority.
4. Obtain independent review of the exact source and pilot, authenticated CI, and trusted tree verification. Verify merge parity, sign off and close #445, then close #435 after checking all children and recording aggregate release evidence.
