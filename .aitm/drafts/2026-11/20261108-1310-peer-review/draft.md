---
kind: draft
slug: peer-review
title: ai-peer-review — caller-chosen output location, possible rewrite on the new stack
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: peer-review
package: aitm-peer-review (bridge) + ai-peer-review (separate repo)
depends-on: [aitm-core]
---

# Draft: ai-peer-review integration

## Known

- Designs and plans are reviewed at several levels: SAR (single agent in the current provider), SPR (same-provider peer), XPR (cross-provider). Definitions confirmed 2026-11-08.
- ai-peer-review must let each review session write to a caller-chosen location, so collateral lands in `.aitm/stories/<bucket>/<id>/{design,plan}/reviews/`.
- Each review records the `planning` commit SHA of the document it reviewed.
- Because the user does not read designs or plans, these reviews are the safety net before delivery; XPR matters most.
- A rewrite of ai-peer-review on the new stack is a candidate first enforcing consumer of the released core.

## Findings: ai-peer-review 0.4.0 as it is today (2026-11-08)

Read from `~/projects/Vibe-Coding/ai-peer-review` (README, `schemas/primary-config-v2.json`, `src/collateral/paths.mjs`, `src/git/`).

- It defines **SPR** (same provider, distinct session) and **XPR** (cross provider, registered through a project-local broker). It has **no SAR**.
- The reviewed artifact must be tracked and committed in the **checked-out worktree**; the review binds to the exact blob and refuses a dirty file.
- Collateral location is already configurable: `review.reviews_root` (default `docs/peer-reviews`) plus `review.review_path_template` with placeholders `<issue> <kind> <name> <date> <review-id> <record-id>`. It is relative to the checkout.
- The author's revisions and the round triads (reviewer response, revised doc, author response) are committed by the tool **on the checked-out branch**. Coordination state lives in ignored `.scratch/peer-review/`.
- `--issue N` is required for SPR/XPR, and the tool prefixes its commits `[#N]`.
- `--phases spec,plan` can govern a design then a plan in one review.
- Setup writes `.ai-peer-review/config.json`, harness skill wrappers and hooks into the checkout.

Conflict with aitm: aitm's planning branch is never checked out, and `.aitm/` in a story worktree is gitignored (untracked), so ai-peer-review can't review either copy as it stands.

## Owner's direction (2026-11-08)

- **[user] Refactor: a patch file per author turn.** ai-peer-review records a patch (diff) of the file under review (FUR) for every author turn that revises it. Patches are numbered by author turn and recorded in git as part of the review record. Every revision is kept, starting from the base version of the FUR. Any revision can be rebuilt and compared with the reviewer and author notes for that turn. Because the diffs are filed independently, the record survives git squash merges.
- **[user] SAR = single-agent review, inside the current provider.** It picks a model and effort level from the current provider and runs a multi-phase review, iterating review → revise until there is nothing left to revise. It needs no broker and no cross-provider conduit; neither does SPR. SAR exists to **normalize the review collateral**: its reviewer responses, author responses and per-revision diffs follow exactly the same format and frontmatter rules as SPR and XPR.
- **[agreed] Consequence for aitm.** The review record (base + numbered patches + responses + manifest) is self-contained files. aitm only needs to import those files into planning; it never needs to replay review commits, so the earlier commit-SHA concern goes away.
- **[call] Patch 000 holds the base.** The first patch is the creation diff of the base version (from empty), so the record rebuilds every revision without needing any git object. It also records the base's planning blob SHA for cross-checking.

## Owner's answers (2026-11-08, second round)

- **[user] What gets reviewed.** SAR, SPR and XPR were meant for spec (design) and plan files. They can also apply to the JIT deep-dive plan, as long as that plan is a file in the story folder and the issue only carries a link to it, never its content. Drafts don't need review. How much review the master design and high-level plans need is left to investigation (recommendation below).
- **[user] The record needs no pre-commit.** ai-peer-review used to keep every revision by committing it and comparing commits. With per-turn patches, the record is just the final revised FUR plus every patch from 000 to the final revision. That makes a complete review session a portable collection of files, so the FUR and responses no longer need to be committed before or during the review.
- **[user] Interim process on aitm today.** Use a temporary branch off the planning branch that can be checked out, and run a full review cycle there. Copy the final collateral into the planning branch by the safest means available. Each later level (SPR, then XPR) refreshes from the planning branch first, so it starts from the previous level's results. If a cycle is interrupted after one level, nothing from that level is lost.
- **[user] Naming.** "Multi-phase" meant the review → revise loop that runs until the reviewer has nothing left. **[call]** Call it an **iterative review**. Each review → revise pass is a **round**, and the review ends when the reviewer is **exhausted**: a round with no required changes. Avoid "phase", because ai-peer-review already uses phases for a spec → plan sequence (`--phases spec,plan`).

## Review levels by document (recommendation, 2026-11-08)

**[call]** Review effort follows how far a mistake spreads and how expensive it is to change later:

| Document | Review | Why |
| --- | --- | --- |
| Ideas, drafts | none | Brainstorm material. Its decisions get reviewed when they reach a design. |
| Master design (`architecture.md`) | SAR → SPR → XPR once before M1 code starts; after that, a **delta review** (SAR, plus XPR if a decision changes) of the patch whenever a section design changes an architecture decision | Every section inherits it, so an error here is the most expensive one. A cross-provider read decorrelates blind spots. |
| Master plan (`master-plan.md`) | SAR, re-run at each milestone boundary | It's ordering and checkpoints, cheap to change, and re-planned as milestones land. |
| Section design (e.g. `core-design.md`) | SAR → SPR → XPR | It is what a builder plans from. Same weight as a story design. |
| Story design | SAR → SPR → XPR | Backlog exit requires an accepted design. |
| Implementation plan | SAR → SPR → XPR | Plan exit requires an accepted plan. |
| JIT deep-dive plan | SAR | It is written against the current code just before Develop, so speed matters. An XPR would be stale by the time it finished. |

Which levels a story needs could become config (`[review] design = ["sar","spr","xpr"]`, `plan = …`, `jit = ["sar"]`), with the peer-review extension registering the guard that checks them.

## Interim review procedure (until the ai-peer-review refactor ships)

For one document at one level (SAR, SPR or XPR):

1. In the hand-built planning checkout, `git pull --ff-only` so the planning branch has every earlier level's results.
2. Create a throwaway branch `review/<story>-<doc>-<level>` from the planning tip, in its own worktree (e.g. `~/projects/Vibe-Coding/aitm-review`). It is never pushed or merged.
3. Run the level there. SPR and XPR use ai-peer-review 0.4.0 with `reviews_root` set to the story's `design/reviews` or `plan/reviews` and `--issue <story>`. SAR is run by hand in the same file formats (ai-peer-review's `templates/reviewer-response.md` and `author-response.md`).
4. At the end, generate the per-turn patches from the review branch's revision commits (`patch-000` = the base from empty, then one per author turn). Copy only the revised FUR and the review folder (responses, manifest, patches) into the planning checkout, and commit them there with a fast-forward push. Nothing outside the story folder is copied: no setup files, no `.scratch/`.
5. Delete the review worktree and branch.

## Candidate approach (proposed, not agreed)

1. **Now: ephemeral review worktree.** aitm creates a local branch `aitm-review/<id>-<doc>` from the planning tip in its own worktree. ai-peer-review runs there unchanged, with `reviews_root` pointed at `.aitm/stories/<bucket>/<id>/<design|plan>/reviews`. On finalize, aitm imports the revised doc and the review folder into planning through the plumbing writer, records the acceptance (manifest path, reviewed blob SHA) as `core.doc.accepted`, and deletes the review branch. While a review is open, the doc is locked against `aitm sync` from the story worktree. Setup files outside `.aitm/` are never imported.
2. **Later (M4): planning-aware ai-peer-review.** The artifact is read from a git ref (`planning:<path>`) and collateral is handed to a sink (the aitm-peer-review bridge) instead of committed on HEAD.
3. **Proposed with the patch refactor: record-only mode.** Since the patches make the record self-contained, ai-peer-review could bind the FUR by content hash instead of a committed blob on HEAD, write the record folder, and leave committing to the host. aitm then reviews the bound copy in the story worktree's `.aitm/` and `aitm sync` commits the record to planning. No temporary branch is needed.

~~To verify: whether review manifests record commit SHAs.~~ Moot once records are self-contained patch files.

## Open

- Refactor in place, or rewrite in Python?
- ~~What SAR means.~~ Answered above.
- ~~Which review levels each document type needs.~~ Recommendation above, awaiting the owner's read.
- ~~Whether review-round commits are replayed into planning.~~ Only files are imported (patch refactor).
- ~~Record-only mode.~~ Agreed: no pre-commit needed.
- Where the ai-peer-review patch refactor is built: the existing JS repo, or the Python rewrite planned for milestone M4. The interim procedure above runs reviews until then.
- ~~"Multi-phase" in SAR.~~ It means iterative review.
