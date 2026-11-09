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

## Candidate approach (proposed, not agreed)

1. **Now: ephemeral review worktree.** aitm creates a local branch `aitm-review/<id>-<doc>` from the planning tip in its own worktree. ai-peer-review runs there unchanged, with `reviews_root` pointed at `.aitm/stories/<bucket>/<id>/<design|plan>/reviews`. On finalize, aitm imports the revised doc and the review folder into planning through the plumbing writer, records the acceptance (manifest path, reviewed blob SHA) as `core.doc.accepted`, and deletes the review branch. While a review is open, the doc is locked against `aitm sync` from the story worktree. Setup files outside `.aitm/` are never imported.
2. **Later (M4): planning-aware ai-peer-review.** The artifact is read from a git ref (`planning:<path>`) and collateral is handed to a sink (the aitm-peer-review bridge) instead of committed on HEAD.
3. **Proposed with the patch refactor: record-only mode.** Since the patches make the record self-contained, ai-peer-review could bind the FUR by content hash instead of a committed blob on HEAD, write the record folder, and leave committing to the host. aitm then reviews the bound copy in the story worktree's `.aitm/` and `aitm sync` commits the record to planning. No temporary branch is needed.

~~To verify: whether review manifests record commit SHAs.~~ Moot once records are self-contained patch files.

## Open

- Refactor in place, or rewrite in Python?
- ~~What SAR means.~~ Answered above.
- Which review levels each document type needs (master design, section design, plan).
- ~~Whether review-round commits are replayed into planning.~~ Only files are imported (patch refactor).
- Record-only mode (no commits by ai-peer-review; the host commits): acceptable?
- Where the refactor happens: the existing JS repo now, or the Python rewrite in M4? What runs reviews until then?
- "Multi-phase" in SAR: review rounds, or distinct lenses per pass (e.g. correctness, then scope, then consistency)?
