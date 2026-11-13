# Epic dependency maps design SPR, round 2

**Decision — ACCEPT** the exact Design revision identified below. All six round 1 findings are resolved.

## Review evidence

- Artifact `.aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md`. Retrieved and reread all physical lines 1–66, including blank lines, from the isolated planning worktree.
- Independently computed raw SHA-256 `f2ce1a217e971ccbeff3ad119725c672a8b8c0af2a104d6d61c6a26ce8726030`. The digest matched the review handoff and the author response and was rechecked at submission.
- Planning base `e086c099dd807cced6521f9606e7d381b0d086a4` and candidate commit `854db6ec7249634d83336c6063381f17db720015` are supplied review pins. The raw file digest is independently verified.
- Retrieved and read [round 1 reviewer response](reviewer-response-1.md) lines 1–43 and [round 1 author response](author-response-1.md) lines 1–16.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 14:33:35 UTC and was submitted 2026-11-12 14:34:12 UTC.

## Finding dispositions

| Finding | Disposition and revised design evidence |
| --- | --- |
| R1-F001 | Resolved. Lines 21 and 28 bind the full audit to shortest deterministic witnesses over the final displayed edges. Lines 50–51 require restoration when both endpoints remain visible and the witness disappears, with allowed context for an omitted endpoint. Line 65 exercises collapse and filtering separately. |
| R1-F002 | Resolved. Lines 27 and 30 define dependent-side authority, separate hard failures from admitted partial boundary views, limit absence and cycle claims, and carry directional coverage through the graph, detail and audit. Line 64 tests an unresolved incoming link and an incomplete outgoing scan with zero known edges. |
| R1-F003 | Resolved. Lines 31 and 35 require audience admission before projection, bind provenance to the authorized pin, cutoff and policy profile, and scope review of the exact bundle and shareable diagnostics to the intended destination. Lines 37 and 65 address evidence retention and restricted-input qualification. |
| R1-F004 | Resolved. Lines 22, 45 and 50 require complete static replacement, current and context-compatible snapshot admission, authorized stale fallback and clearing unavailable selection. Lines 64 and 66 cover failures after output begins, superseded refresh, visibility change and selection behavior. |
| R1-F005 | Resolved. Lines 29 and 49–52 provide textual state and equivalent graph exploration and audit access, with explicit focus destinations. Line 66 qualifies keyboard and text exploration, nested maps and focus recovery. |
| R1-F006 | Resolved. Lines 31, 47 and 56–58 apply audience qualification to hosted data and require the applicable released hosting and M2 link contracts for the add-on. The static and local acceptance paths are independent, and the accepted #258 and #260 dependencies are preserved. |

Lines 10 and 56–58 retain the linked follow-on outside the 13-item M6 release, place Plan acceptance and item-specific JIT review before Develop, and keep released Core compatibility ahead of product viewer work. The pinned #133 topology and two-pin state replay remain qualification requirements at lines 62–63. This disposition covers Design. Plan review, released-contract verification and execution of the qualification cases remain subsequent work.
