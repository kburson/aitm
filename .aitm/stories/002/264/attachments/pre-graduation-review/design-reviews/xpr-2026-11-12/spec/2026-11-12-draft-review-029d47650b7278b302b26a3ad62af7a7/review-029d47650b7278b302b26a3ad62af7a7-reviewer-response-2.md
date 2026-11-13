<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-029d47650b7278b302b26a3ad62af7a7"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md"
artifact_commit: "6d2f75a8aa85c81a14938a15b9d463002f40d675"
artifact_blob: "d3931f75947f240b124716ad861979c42c1f06e9"
artifact_digest: "sha256:0adca6f338bbda55f98b17708bcd6d932b0ca87b6ca6965a0994bc2151e78abd"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0f6473fbeb7b0ce4f3edbec042401b9bb4b6d72e6043769973af5539525d3685"
  identity_source: "runtime"
started_at: "2026-11-12T14:35:17.022Z"
submitted_at: "2026-11-12T14:40:40.583Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Round-2 independent cross-provider review of
`.aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md` at blob
`d3931f75947f240b124716ad861979c42c1f06e9` (commit `6d2f75a`, digest
`sha256:0adca6f3…8abd`). The digest matches the one in author response 1.

**Read coverage.** I read the whole revised artifact (lines 1-67 of 67) in
one Read call. I also read author response 1 in full. I did not use Git.

**Verification of the round-1 required changes.**

- **R1-F001 (nested-epic boundary): resolved.** Line 28 now treats any
  admitted dependency that touches a direct child and crosses the displayed
  child set as a boundary link. When the other endpoint is a descendant of a
  displayed child epic, the link is labeled with the actual descendant and
  its containing child epic, subject to visibility, and the actual edge is
  kept for detail and audit. Edges entirely below the direct-child level are
  assigned to their own epic maps. Line 65 adds sibling → nested-descendant
  fixtures in both directions and checks that the boundary names the actual
  descendant and cannot act as a witness.
- **R1-F002 (hidden order and layers): resolved.** Line 50 defines a layer
  as one hop on admitted declared edges, including declarations whose arrows
  are reduced in the overview. Line 52 marks a view as hiding paths when
  admitted intermediates conceal order that has no declared shortcut, and
  lets detail and the text view reveal the admitted path, while the graph
  draws only declared dependencies. This is a clear, deliberate choice.
  Line 66 adds the fixture for a hidden intermediate with no declared
  shortcut. Expanding T02 downstream in #133 brings in T04, T05, T07, T10 and
  T11, and the line 52 recompute rule then reduces T02→T05 and T02→T11
  because T04 and T07→T08 (once expanded) are visible. The two rules are
  consistent.
- **R1-F003 (package placement): resolved.** Line 14 puts the static
  command in Python under `tools/story_dashboard/` with Graphviz at generation
  time, and the interactive feature in TypeScript in `aitm-viewer`. It says
  the frontmatter `package` refers to the viewer feature, and it makes the
  shared expected graph and audit fixtures the conformance contract. Line 66
  requires the same expected internal edges, boundary links, gates and audit
  paths in both fixture sets. This also agrees with line 59, which says the
  static command has no viewer runtime prerequisite.
- **R1-F004 (bundle key and pin): resolved.** Line 38 keys bundles by
  `<source-planning-commit>/<visibility-profile>/`, requires a stable
  versioned profile key and a recorded destination, and replaces the
  ambiguous phrase with "the exact planning commit read by the generator".
  The cutoff is now set by that commit's UTC committer timestamp, so it does
  not need to be part of the key.
- **R1-F005 (witness scope): resolved.** Lines 21 and 29 restrict witnesses
  to final displayed internal child-to-child edges. Boundary links and epic
  gates are always kept and are excluded from witnesses. Line 65 tests this.

**Round-1 optional suggestions.** Suggestion 1 was adopted. Lines 21-22 now
break path ties by ascending numeric story IDs and make both Markdown files
byte-reproducible for the same admitted input and generator version.
Suggestions 2-4 (readiness display, release vehicle, cycles through
boundaries) were left to the Plan, which the author response explains. None
of them blocks acceptance.

**New-text check.** I re-checked the revised paragraphs for new
contradictions. Lines 28-29, 50 and 52 agree with each other on boundary,
witness, layer and hidden-path behavior. Line 38's path change agrees with
the atomic last-valid rule on line 22 and with record retention on line 42.
I found no new defect that requires a change.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Line 28 leaves an edge between descendants of two different displayed
   child epics (e1 under E1 → e2 under E2) to the child maps only. In the
   parent map, E1 and E2 then look unrelated. The Plan could add a
   non-arrow indicator, or a detail entry, on a child-epic node that has
   such descendant-level cross links, so that the parent map does not
   suggest the epics are independent.
2. Line 21's tie-break would be fully exact if it said that paths compare
   lexicographically by their ordered sequence of numeric story IDs, after
   length.
3. Carry round-1 suggestions 2-4 (readiness display, release vehicle for
   the viewer add-on, and cycles closed only through boundary edges) into
   the Plan as explicit decisions.

## Decision

accepted
