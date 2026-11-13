# Epic dependency maps design SPR, round 3

**Decision — ACCEPT** the exact post-XPR Design revision identified below. The six SPR findings remain resolved. The revision addresses all five XPR round 1 findings.

## Review evidence

- Read all 67 physical lines, including blanks, of `.aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md` from the isolated XPR planning worktree. Candidate commit `6d2f75a8aa85c81a14938a15b9d463002f40d675` is the supplied review pin.
- Independently computed raw SHA-256 `0adca6f338bbda55f98b17708bcd6d932b0ca87b6ca6965a0994bc2151e78abd`. The digest matched the handoff and the XPR author response and was rechecked at submission.
- Reread [SPR round 2](reviewer-response-2.md) lines 1–24. Retrieved and read the durable XPR reviewer response 1 lines 1–260 and author response 1 lines 1–54 for `review-029d47650b7278b302b26a3ad62af7a7`.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 14:40:13 UTC and was submitted 2026-11-12 14:41:04 UTC.

## SPR finding confirmation

| Finding | Status on the post-XPR revision |
| --- | --- |
| SPR R1-F001 | Resolved. Lines 21, 29, 52 and 66 retain deterministic witnesses over final displayed internal edges and restore a direct edge when collapse or filtering hides its witness. |
| SPR R1-F002 | Resolved. Lines 27, 30–31 and 65 preserve dependent-side authority, distinguish input failures and partial directional boundary coverage from a verified empty result, and scope cycle and absence claims. |
| SPR R1-F003 | Resolved. Lines 32, 36, 38 and 66 preserve policy admission before projection, exact bundle review for the approved destination, and checks on every shareable surface. The versioned visibility profile is now part of bundle identity. |
| SPR R1-F004 | Resolved. Lines 22, 46, 51, 65 and 67 retain atomic static bundle replacement, current and scope-compatible refresh, authorized stale fallback and selection clearing. |
| SPR R1-F005 | Resolved. Lines 30, 50–53 and 67 preserve equivalent keyboard and text navigation, textual lifecycle and dependency context, and predictable focus recovery. |
| SPR R1-F006 | Resolved. Lines 32, 48 and 57–59 preserve released hosting and M2 link contracts and audience qualification for the hosted follow-on. Static and local acceptance remain independent. |

## XPR round 1 finding confirmation

| Finding | Disposition on the post-XPR revision |
| --- | --- |
| XPR R1-F001 | Addressed. Lines 28–29 preserve the declared dependency between a direct child and an admitted descendant as a boundary link, identify the descendant and containing child epic, and exclude the boundary from witnesses. Line 65 exercises both directions. |
| XPR R1-F002 | Addressed. Lines 50 and 52 define a layer as one hop on admitted declared edges. If a view hides a path with no declared shortcut, the graph indicates hidden paths and detail reveals the admitted path. Line 66 covers the case. |
| XPR R1-F003 | Addressed. Lines 14 and 66 name the Python planning tool under `tools/story_dashboard/` and TypeScript viewer in `aitm-viewer`, clarify the frontmatter package, and require common expected graph and audit results for conformance. |
| XPR R1-F004 | Addressed. Lines 36 and 38 key the bundle by exact generation commit and stable versioned visibility profile. The commit's UTC committer timestamp determines the lifecycle cutoff, and the reviewed destination is recorded. |
| XPR R1-F005 | Addressed. Lines 21 and 28–29 limit witnesses to final displayed internal child-to-child edges. Lines 65–66 qualify that restriction and retain the separate boundary and gate results. |

Lines 10 and 57–59 preserve the 13-item M6 release and the existing #258 and #260 dependencies. The linked follow-on retains the accepted Design, Plan and applicable item-specific JIT prerequisites to Develop. Its interactive deliverable waits for released Core and #250/#251. The #133 pilot and lifecycle replay remain qualification cases at lines 63–64. This records the independent Codex Design disposition. The Claude reviewer owns the XPR disposition.
