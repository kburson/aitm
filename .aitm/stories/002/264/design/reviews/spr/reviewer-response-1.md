# Story #264 Design same-provider review

**Decision — ACCEPT** the exact Design revision for story #264. There are no required Design revisions.

## Review evidence

- Candidate `.aitm/stories/002/264/design/dependency-maps.md` at supplied commit `d5c1413a0658f904de7ed921bec872797a376f15`. Read physical lines 1–60 in full and independently verified raw SHA-256 `f8d229b076947ac00fae768ea4f0df566ecabb5e74fae50ce3c1192388724ddf` in the review worktree.
- Read `.aitm/stories/002/264/story.md` physical lines 1–27 in full and verified raw SHA-256 `d6b9798689a9c2427dc903e121e4ca81eb0aae25ee2fa565cf889cfb22cbceea`. Rechecked both digests at submission.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 15:03:29 UTC and was submitted 2026-11-12 15:04:24 UTC.
- Reread all 33 lines of the pre-graduation SPR round 3 response and compared the Design to the previously reviewed 67-line draft with raw SHA-256 `0adca6f338bbda55f98b17708bcd6d932b0ca87b6ca6965a0994bc2151e78abd`. The changes bind the title and scope to the assigned story and remove the draft frontmatter and its package-field explanation. The technical Design is equivalent.

## Assigned story and release scope

The story record identifies #264, its GitHub issue, Backlog status, and its creation at 15:02:03 UTC, before this review started. It names this Design path in frontmatter and links it from the story body. The story is a linked follow-on to #247, with no parent or dependency edge recorded. The #247 story record still lists its 13 accepted children. The #258 record lists #256 as its prerequisite and the #260 record lists #258, #257 and #259. These planning records agree with Design lines 3 and 50–52. This review verified the planning records and did not query live GitHub.

The static planning command and product viewer have separate pickup gates. Lines 39–41 and 51–52 retain released Core and #250/#251 for product viewer work and retain applicable released hosting and link contracts and audience qualification for hosted delivery.

## Prior finding check against the assigned Design

| Finding | Resolution in the #264 Design |
| --- | --- |
| SPR R1-F001 | Lines 14, 22, 45 and 59 retain deterministic displayed witnesses, edge restoration when a visible witness disappears, and separate collapse and filter cases. |
| SPR R1-F002 | Lines 20 and 23–24 retain dependent-side authority, verified-empty and partial coverage, scoped absence and cycle claims, and Unknown readiness under missing coverage. Line 58 covers both boundary gap cases. |
| SPR R1-F003 | Lines 25 and 29–31 retain visibility admission before projection and exact review for the authorized destination, with pin, cutoff and profile recorded. Line 59 covers shareable output surfaces. |
| SPR R1-F004 | Lines 15 and 39 preserve atomic bundle replacement, eligible current snapshot admission and authorized stale fallback. Lines 44 and 58–60 retain selection clearing and failure qualification. |
| SPR R1-F005 | Lines 23 and 43–46 preserve text labels, keyboard and text exploration, audit context and focus recovery. Line 60 qualifies the paths. |
| SPR R1-F006 | Lines 25, 41 and 50–52 retain separate hosted qualification, the existing #258 and #260 dependencies, and independent static and local delivery paths. |
| XPR R1-F001 | Lines 21–22 and 58 preserve admitted descendant boundary links with actual endpoints and containing child epics. Both directions are qualified and cannot witness internal reduction. |
| XPR R1-F002 | Lines 43 and 45 define a layer as a hop on admitted declarations and explain hidden paths without inventing a shortcut. Line 59 qualifies the hidden-intermediate case. |
| XPR R1-F003 | Lines 7 and 59 assign Python to the static tool and TypeScript to the viewer and use common expected graph and audit outputs to qualify conformance. |
| XPR R1-F004 | Lines 29–31 pin the exact generator input commit and versioned visibility profile, fix the cutoff to the UTC committer timestamp, and record the destination. |
| XPR R1-F005 | Lines 14, 21–22 and 58–59 limit witnesses to final displayed internal child-to-child edges and preserve boundary links and epic gates. |

The #133 topology and two-pin lifecycle replay remain qualification requirements at lines 56–57. This accepts the assigned story's Design. Plan acceptance and applicable item-specific JIT review are still required before Develop.
