# Epic dependency maps design SPR, round 1

**Decision — REQUEST REVISIONS** for the exact Design candidate identified below.

## Review evidence

- Artifact `.aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md`. Retrieved and read all physical lines 1–61, including blank lines, from the isolated planning worktree.
- Independently computed raw SHA-256 `00b79ca154d258c4ed0b731d3fe8b1862179c086af12dc9558d88b8ad87b719c`. The digest matched the review handoff and was rechecked at submission.
- Planning base `e086c099dd807cced6521f9606e7d381b0d086a4` and candidate commit `1f698069d25c766fa9b901ec68f8bb5f9ddc9c73` are supplied review pins. The raw file digest is independently verified.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 14:29:45 UTC and was submitted 2026-11-12 14:31:43 UTC.
- Retrieved context from the same planning worktree. Read the accepted #247 decomposition lines 1–152, #250/#251/#260 story records lines 1–37 each, and `.aitm/README.md` lines 1–36. Also read the #230 replan lines 1–29 and the #247 decomposition SPR round 2 lines 1–7.

## Required design changes

### R1-F001 — Make the reduction rule consistent with the rendered view

Draft lines 21, 28, and 48 require an alternate path made of displayed arrows that survives the current view, then permit an explanation in place of restoring an edge when its witness disappears. For example, if A → C was suppressed by A → B → C and a filter hides B while A and C remain, the current wording permits a rendered graph with no A-to-C relationship. Define which omissions the full audit covers and require that an eligible direct edge between visible endpoints be restored whenever its visible witness disappears. If an endpoint itself is filtered or collapsed, permitted context in detail can explain the omission without a summary arrow. Qualification should exercise collapse and filtering separately, and verify that full-scope audit witnesses are deterministic shortest paths using the final displayed edges.

### R1-F002 — Specify how coverage constrains absence claims

Draft lines 22, 27–30, 47, and 60 distinguish missing child records from unresolved boundary records but leave the boundary of the completeness claim open. Outgoing links come from the dependents' records. If one of those records is unavailable or its authoritative field is unreadable, there may be no positive link to display, even if it depends on a child of the epic. Define how the adapters distinguish verified-empty coverage from partial, unresolved, or restricted coverage and which cases fail the map or allow an explicitly partial map. Preserve verified declarations in a supported partial view, never fill a coverage gap from the reverse projection, and limit absence and cycle claims to the validated scope. Specify what the graph, detail and audit can say when coverage is incomplete, subject to audience policy. Qualify an incomplete outgoing scan with no known boundary edges and a known unresolved incoming link. A definitive empty list or readiness implication would fail those cases.

### R1-F003 — Bind artifact generation and attachment to an admitted audience

Draft lines 20–22, 30, and 34–36 permit a raw local bundle followed by review before attachment. They do not state how an attachable bundle is derived from an approved audience profile or which authority establishes that profile for the static adapter. A manual review of raw output cannot establish that restricted records had no effect on reduced topology, aggregate values, path witnesses, source links, or the audit. Require that any attachable bundle be generated from the audience-admitted projection before topology, reduction, counts and audit, with enough provenance to identify the input pin, lifecycle cutoff and applied policy. Bind attachment review to the exact bundle and its approved destination. Include Markdown, SVG metadata and links, audit and any shareable diagnostics in the disclosure check. Require an authorized source pin or keep the bundle local when the pin itself would expose restricted material. Add a fixture in which restricted input could otherwise affect counts or reduction without a restricted identifier appearing in the main diagram.

### R1-F004 — Define a complete, scope-compatible refresh

Draft lines 20–22, 36, 40, 44, and 47 protect against graph validation failure and require last-valid viewer fallback. They leave failure during rendering, an older refresh finishing later, and a changed access scope unspecified. Define that a static replacement makes all three outputs from one validated pin visible together, with the previous valid bundle preserved if any generation or write fails. For the viewer, admit the graph, detail, labels and provenance together from the same eligible snapshot. Keep the last valid view only while it is authorized for the current project and visibility context. A completion from an older or superseded refresh must not replace the current view. State that selection and its detail clear when the selected story is no longer visible or admitted. Qualify a renderer failure after another output has been produced, superseded refresh completion, and a failed refresh after a visibility change. Reuse of the viewer's existing refresh mechanism remains appropriate.

### R1-F005 — Make graph exploration available by keyboard and in the text view

Draft lines 46–48 and 61 require keyboard story selection and a readable text view. Expansion, collapse, following prerequisites, navigating to nested maps and accessing edge explanations are also core tasks. Require equivalent access to these actions and their direction, state and coverage information through keyboard-operable controls and the text presentation. Specify a predictable focus destination after collapse or refresh removes the focused node. Qualify these tasks without a pointer and verify that missing or filtered relationships are understandable without relying on color or visual layout.

### R1-F006 — State the independent gate for hosted delivery

Draft lines 44 and 52–54 gate viewer integration on released Core and #250/#251. A statement about hosted freshness and the existing visibility policy leaves room to read those prerequisites as sufficient to publish the add-on to an existing route. The #247 decomposition at lines 120–124 assigns real-data hosting and link qualification to #258, including M2 issue-link authority and an authorized audience and route. State that hosted delivery of this follow-on requires the applicable released hosting and link contracts plus audience approval and verification for the added graph, detail and audit data. This is a gate on the add-on's hosted delivery, with no prerequisite added to #258 or #260 and no hosting dependency on the static or local deliverables.

## Scope and implementation decisions

The draft keeps this follow-on outside the 13 accepted M6 items, preserves #260's existing predecessors and puts the released Core contract ahead of product viewer work. The #230 replan resolves the earlier completion-accounting cycle and leaves the existing Cost and release gates in place. The pinned #133 topology and two-pin lifecycle replay provide concrete qualification targets. The review assessed the design and these proposed checks. It did not execute a pilot rebuild.

The implementation plan can choose the graph algorithm, witness tie-break, bundling and replacement mechanism, export field names, serialization, renderer configuration, UI controls and responsive layout once the behavioral contracts above are accepted. The static command and viewer should have separately verifiable slices, with item-specific JIT review and the applicable four-hour limit. The next design round should review the full revised artifact and record a disposition for each finding ID.
