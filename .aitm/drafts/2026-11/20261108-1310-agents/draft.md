---
kind: draft
slug: agents
title: aitm-agents — researcher, planner and plan-reviewer roles
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: agents
package: aitm-agents
depends-on: [aitm-core, aitm-harness]
---

# Draft: aitm-agents

## Known

- Three roles: researcher (read-only, cheaper model), planner (writes only to the story's `design/` and `plan/`), independent plan reviewer (different model or harness preferred).
- Defined once in a harness-neutral form (prompt, allowed tools, inputs, output schema); generated as native agents where supported, skill fallback elsewhere.
- They use the superpowers brainstorming and writing-plans skills; aitm adds the inputs and output contract.
- aitm feeds each run a compact context packet: comparable past stories, their trips and reasons, files and dependencies involved.
- Plan output schema: leaf stories ≤ 4 h, touched files, risks, likely defect areas; non-conforming plans are rejected automatically.
- Industry-trend research is opt-in for epics.
- Success is measured by trip rate before and after.

## Open

- Should the design author also be a dedicated role, or the planner?
- How the JIT deep-dive is run: planner role in revision mode?
