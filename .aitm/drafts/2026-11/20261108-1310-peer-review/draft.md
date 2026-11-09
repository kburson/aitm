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

- Designs and plans are reviewed at several levels: SAR, SPR, XPR (assumed: single-agent, same-provider peer, cross-provider).
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

## Candidate approach (proposed, not agreed)

1. **Now: ephemeral review worktree.** aitm creates a local branch `aitm-review/<id>-<doc>` from the planning tip in its own worktree. ai-peer-review runs there unchanged, with `reviews_root` pointed at `.aitm/stories/<bucket>/<id>/<design|plan>/reviews`. On finalize, aitm imports the revised doc and the review folder into planning through the plumbing writer, records the acceptance (manifest path, reviewed blob SHA) as `core.doc.accepted`, and deletes the review branch. While a review is open, the doc is locked against `aitm sync` from the story worktree. Setup files outside `.aitm/` are never imported.
2. **Later (M4): planning-aware ai-peer-review.** The artifact is read from a git ref (`planning:<path>`) and collateral is handed to a sink (the aitm-peer-review bridge) instead of committed on HEAD.

To verify: whether review manifests record commit SHAs (which change when commits are replayed onto a moved planning tip) or only blob SHAs (which don't).

## Open

- Refactor in place, or rewrite in Python?
- What SAR means, since ai-peer-review has no SAR.
- Which review levels each document type needs (master design, section design, plan).
- Whether review-round commits are replayed into planning or only the final files are imported.
