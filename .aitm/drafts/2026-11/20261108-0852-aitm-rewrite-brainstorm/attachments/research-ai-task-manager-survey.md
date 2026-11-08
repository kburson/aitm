---
kind: research
title: Survey of ai-task-manager before the rewrite
created: 2026-11-08T15:30:00Z
source-repo: kburson/ai-task-manager @ c8b64b6b2 (trunk-derived worktree)
---

# Survey of ai-task-manager (2026-11-08)

## Size

| Measure | Value |
| --- | --- |
| Tracked files | 4,804 (2,547 under `scripts/`, 2,035 under `docs/`) |
| Source lines (`scripts/**/*.mjs`, non-test) | 193,575 |
| Test lines | 341,981 |
| Modules in `scripts/task-tracker/lib/` | 373, of which 49 are guards |
| Distinct `aitm-*` marker names in code | 161 |
| Largest verb | `verbs/close.mjs`, 5,433 lines |
| Verbs | 70 under `verbs/` |
| Commits / first commit | 2,833 since 2026-04-25 |
| Skill prose (`skill/shared`) | ~92 KB |

## Throughput

| Month | Commits | Issues created | Bugs among them | Issues closed | Closed not planned |
| --- | --- | --- | --- | --- | --- |
| 2026-05 | 411 | 244 | 61 | 224 | 6 |
| 2026-06 | 494 | 418 | 144 | 381 | 11 |
| 2026-07 | 700 | 342 | 173 | 341 | 18 |
| 2026-08 | 810 | 280 | 139 | 269 | 48 |
| 2026-09 | 257 | 236 | 64 | 196 | 3 |
| 2026-10 | 87 | 165 | 113 | 103 | 1 |

176 issues open on 2026-11-08. Open titles are dominated by recovery, saga, revision-fence, ledger, custody and idempotent-repair work: the tool building transaction infrastructure around issue bodies.

## State machine (to carry over conceptually)

- States: Backlog, Refine, Ready for Plan, Plan, Develop, Test, Review, Done (`scripts/task-tracker/states/`).
- Each state is `{ id, entryGuards, residentActions, exitGuards }`. Guards return `{ok}` or `{ok:false, reason}`; actions run after the status write, are idempotent, and never refuse.
- Plan alone has 12 exit guards; Review has 6. Close gates live partly in `verbs/close.mjs`.

## GitHub facts verified live

- GraphQL budget 5,000 points/hour, shared account-wide. REST `core` is a separate budget.
- Projects v2 REST works on the REST budget: `GET /users/kburson/projectsV2/11/fields` and `.../items` both returned data (header `X-GitHub-Api-Version: 2026-03-10`).
- REST item-field PATCH (`/users/{u}/projectsV2/{n}/items/{id}`) is documented by third parties; **not verified live**.
- `kburson/ai-task-manager` and `kburson/aitm` are public, so Pages is free.

## Link stability on GitHub

| Link | Behaviour |
| --- | --- |
| `blob/<branch>/path` | Follows the tip; breaks when the branch is deleted |
| `blob/<sha>/path` | Permanent while the commit stays reachable; rebase/squash orphans it. GitHub keeps `refs/pull/N/head`, so PR commits usually survive branch deletion; force-pushed-over commits are not guaranteed (community evidence, not official docs) |

Conclusion: a never-rewritten `planning` branch gives both an always-latest link and permanent SHA snapshots.

## Startup timing (local, cold-ish)

- `node scripts/task-tracker/bash-guard.mjs` with empty input: ~139 ms.
- `python3 -c 'import json,subprocess,pathlib'`: ~88 ms.

## Prior designs worth reusing

- `docs/superpowers/specs/2026-09-25-1817-worktree-local-backlog-and-history-design.md` — local drafts, coalesced publication, closed-issue archive.
- `docs/superpowers/specs/2026-09-26-1821-branch-local-estimation-rubric-design.md` — per-story Refine/Plan/Close records, rebuildable manifest, calibration from complete triads.
- `docs/superpowers/specs/2026-09-20-aitm-mcp-adapter-architecture-design.md` — headless kernel, capability ports, MCP surface (1,853 lines; mine for ideas, do not copy its weight).

## Sources

- [Is a deleted branch on GitHub guaranteed to not leak data? #70144](https://www.Github.com/orgs/community/discussions/70144)
- [Scaling Git's garbage collection](https://github.blog/engineering/scaling-gits-garbage-collection/)
- [GitHub REST rate limit](https://docs.github.com/en/rest/rate-limit/rate-limit)
- [GitHub Projects REST fields](https://docs.github.com/en/rest/projects/fields)
