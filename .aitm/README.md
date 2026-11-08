# `.aitm/` layout

Hand-built until the core exists. The core will own this layout once it ships.

```
.aitm/
  ideas/<YYYY-MM>/<YYYYMMDD-HHMM>-<slug>.md        parking lot: one file per idea
  drafts/<YYYY-MM>/<YYYYMMDD-HHMM>-<slug>/         brainstorming before a story exists
      draft.md
      attachments/
  drafts/discarded.jsonl                           one line per discarded draft (title, reason, last SHA)
  stories/<bucket>/<id>/                           bucket = id // 100, zero-padded to 3 digits
      story.md                                     frontmatter + human-readable story (generated sections)
      events.jsonl                                 append-only event log (authority for state and timing)
      draft.md                                     the graduated draft, moved here at graduation
      design/   <design docs>   reviews/
      plan/     <plan docs>     reviews/
      retro/                                       agent sign-off retrospective
      attachments/
```

## Rules

- Paths are computed from the story ID only. Never group by epic or state; those live in frontmatter.
- Epics are stories. Parent/child links live in frontmatter, not in nested folders.
- Done and abandoned stories never move, so links never break.
- Each file has exactly one writer. `<details>` JSON blocks in `story.md` are generated output and are never parsed back.
- A local SQLite index (gitignored, rebuildable) will sit on top of these files once the core exists.

## Lifecycle

1. **Idea** — parked in `ideas/`.
2. **Draft** — brainstormed in `drafts/`.
3. **Graduation** — a GitHub issue is created, the draft folder moves to `stories/<bucket>/<id>/`.
4. **Design** — written and peer-reviewed inside the story folder (Backlog state; Backlog exit requires an accepted design).
5. **Refine → Ready for Plan → Plan → (JIT) → Develop → Test → Review → Done.**
