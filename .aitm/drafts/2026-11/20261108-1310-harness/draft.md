---
kind: draft
slug: harness
title: aitm-harness — Claude Code, Codex and Grok integration
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
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
- Optional MCP server over the same functions as the CLI.
- `uvx aitm install --agent claude,codex,grok` writes each harness's files.
- Hook latency target < 100 ms; import-light hook module; never via `uv run`.

## Open

- Does Grok support MCP? Do Codex and Grok support custom agent definitions?
- Word counting from transcripts per harness — optional feature or dropped?
