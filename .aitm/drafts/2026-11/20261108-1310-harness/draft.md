---
kind: draft
slug: harness
title: aitm-harness — Claude Code, Codex and Grok integration
created: 2026-11-08T19:10:12Z
updated: 2026-11-11T16:02:43Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: harness
package: aitm-harness
depends-on: [aitm-core]
---

# Draft: aitm-harness

## Known

- One shared `SKILL.md` plus thin per-harness shims (`.claude/skills`, `.agents/skills`, `.grok/skills`).
- One Python hook entrypoint; per-harness translators normalise each harness's envelope in and denormalise the result out (replaces `grok-wire.mjs`). Contract tests against recorded real payloads from each harness.
- Hooks are accelerators and recorders, never required for correctness. Double-firing (Grok native + Claude-compatible hooks) must be harmless.
- Per-harness quirks live in the translator: session ID variable, transcript location, deny semantics, trust model.
- Pre-tool-use deny rules guarding the planning branch (layer 4 of "Guarding the planning branch" in the core design). They deny checking out or switching to the configured planning branch, `git worktree add` on it, `gh pr create --base <planning>`, and `git merge --allow-unrelated-histories`. They also deny agent calls to `aitm pivot`, the one human-only command.
- Optional MCP server over the same functions as the CLI.
- `uvx aitm install --agent claude,codex,grok` writes each harness's files.
- Hook latency target < 100 ms; import-light hook module; never via `uv run`.

## Open

- Does Grok support MCP? Do Codex and Grok support custom agent definitions?
- Word counting from transcripts per harness — optional feature or dropped?

## Managed PR lifecycle intake from #2

[Reviewed handoff](../../../stories/000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md#package-handoffs-and-proof-order). Carry the following separately testable slices into M3 refinement. Estimates are preliminary implementation agent-hours and include local verification and independent review.

| Slice | Hours | Entry condition and proof |
| --- | ---: | --- |
| Runtime identity and broker scope | 4 | Consume [#233](https://github.com/kburson/aitm/issues/233), [#234](https://github.com/kburson/aitm/issues/234) and [#241](https://github.com/kburson/aitm/issues/241). Bind runtime-attested identity outside the workspace. Exercise copied artifacts, stale generations, current cross-story denial and scoped authorized observation. |
| Tool, credential and network containment | 4 | Use the scoped broker and M2 hosted push fixture, which can run before managed readiness. Prove denial of direct provider Git/API routes, including anonymous public routes, while an allowed managed push works. Report unqualified host/profile combinations unavailable. |
| Installed CLI, skill and MCP parity | 3.5 | Consume [#240](https://github.com/kburson/aitm/issues/240) and [#242](https://github.com/kburson/aitm/issues/242). Compare installed schemas, arguments, same-dispatch admissions, supported operations and typed refusal. |

Qualify hosted readiness jointly with M2 before enabling the integrated repair flow. Plan and authorize each supported runtime profile through the receiving milestone.
