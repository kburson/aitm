# #443 effort reporting implementation plan

The [portable effort plan](../../426/plan/2026-11-24-agent-effort-cost-implementation-plan.md) governs this story. The delivery coordinator and implementing agent are Codex. The target is `trunk` from `1b74f36fb1f2381802754a685c5153e2826ac12f` via `codex/443-effort-report`. GitHub confirmed #442 closed and Done.

1. Add a read-only SQLite snapshot entry point. Exercise missing stores, project mismatch and databases created before trail tables existed. Take one consistent snapshot per command.
2. Reuse the existing rollup to produce story, epic and unattached reports with role and provider breakdowns and attempt-level outcomes. Retain gaps and separate native provider indicators, API-equivalent estimates and verified charges. Add canonical versioned JSON and human-readable CLI output.
3. Read approved legacy v1 usage exports without changing their bytes. Validate their project, sequence, digest and row identities. Carry legacy estimates with their recorded basis and hold cross-source accounting open when overlap cannot be established.
4. Run focused and existing producer compatibility tests, local product tests, authenticated hosted CI and trusted verification. Obtain independent review of the tested source and verify the remote merge tree before sign-off.
