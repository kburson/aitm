<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-029d47650b7278b302b26a3ad62af7a7"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md"
artifact_commit: "ad20083299fc1ea449b39e8d5a3024580e144944"
artifact_blob: "f3ed42891b5c4fca7322414c46f4c612f586565b"
artifact_digest: "sha256:f2ce1a217e971ccbeff3ad119725c672a8b8c0af2a104d6d61c6a26ce8726030"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0f6473fbeb7b0ce4f3edbec042401b9bb4b6d72e6043769973af5539525d3685"
  identity_source: "runtime"
started_at: "2026-11-12T14:35:17.022Z"
submitted_at: "2026-11-12T14:37:49.738Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent cross-provider round-1 review of
`.aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md` at blob
`f3ed42891b5c4fca7322414c46f4c612f586565b` (commit `ad20083`).

**Read coverage.** I read the whole artifact (lines 1-67 of 67) in one Read
call at the path named in the invitation. Nothing was truncated. I did not
read the earlier SAR/SPR review records for this draft, so this review is
independent of them.

**Source checks I made.** All reads were of the working tree at the current
branch head. I did not use Git, so I could not check content at the historical
pins.

- **#133 pilot counts.** `.aitm/stories/001/133/plan/leaf-issue-receipt.json`
  has `leaf_count: 41` and `dependency_count: 64`. I worked out the transitive
  reduction of the 64 `deps` edges by hand. Exactly nine edges are implied by
  longer paths: T02→T05 (via T04), T07→T09 (via T08), T02→T11 (via
  T07→T08), T15→T23 (via T16…T20), T09→T31 (via T12…T25→T26), T25→T32 (via
  T26→T31), T25→T36 (via T26…T33), T25→T37 (same path) and T33→T39 (via
  T36→T38). That leaves 55 displayed arrows, as the draft claims (line 16,
  line 62). T23 (#160) is blocked only by T15 and T20, and T25 (#162) only by
  T24, so the source has no #160 → #162 edge. That matches line 62.
- **#227 / #193 reverse-field gap.** `.aitm/stories/002/227/story.md` has
  `blocked-by: [193]`. `.aitm/stories/001/193/story.md` has `blocking: []`.
  This matches line 27.
- **#133 → #2 epic-level gate.** #133 has `blocking: [2]` and #2 has
  `blocked-by: [100, 133]`. This matches line 62 and the arrow-direction rule
  on line 26.
- **#142 lifecycle.** #142's `events.jsonl` moves plan → develop and later to
  done. This agrees with line 63. I could not confirm which state applies at
  `05d3330` versus `ea4a838` without Git.
- **M6 sequencing.** The M6 decomposition (lines 25-35) shows #250 (V03)
  gated on the released Core export, #251 (V04) after V03, #258 (V10) on the
  M2 hosted issue-link contract and authorized route, and #260 (V13) as the
  aggregate release. This matches draft lines 45-47 and 56-58. The #230
  replan keeps #260 dependent on #259.

**What the design gets right.** The arrow direction is unambiguous
(prerequisite → dependent). The edge source is a single field (the dependent's
`blocked-by`), and `blocking` is used only for discrepancy reporting.
Containment, completion and epic-level gates are kept separate. The map is
explicitly not a pickup authorization. Bundle publication is all-or-nothing
and keeps the last valid bundle. The visibility policy is applied before
reduction, path selection and counts, which closes the side channels through
counts and witnesses. Partial coverage and verified-empty coverage are
distinguished, and readiness is kept separate from lifecycle. The work stays
outside the 13-item M6 release. The qualification list has concrete numbers
that can be checked.

The findings below are about graph semantics that the draft leaves open in
the places a planner relies on most: nested epics, filtered views, and how
reduction treats boundary nodes. They also cover two delivery and
bundle-identity gaps that would cause rework or collisions once the plan is
written.

## Findings

### R1-F001 — Parent maps do not say what happens to descendant dependencies that cross a nested-epic boundary

**Where.** Lines 26, 28 and 49 (direct children only; boundary links are
"cross-epic edges"; "Open a nested epic in its own map"). Line 64 (nested-epic
fixtures).

**Problem.** Take a parent epic P with direct children S (a story) and E (a
child epic). E contains story e1, and e1's `blocked-by` lists S. The P map
shows S and E. It does not show e1, and S → E is not declared, so the draft's
rules produce no arrow between S and E. From P's map a planner would conclude
that E does not depend on S, which is the "where it joins" question the
feature exists to answer (line 14). The reverse case (S blocked by e1) has the
same problem. This also affects reduction and the audit: an edge such as
S → E2 could be implied by a path that runs through E's descendants, and the
draft does not say whether such paths count as witnesses.

The draft defines boundary links only as cross-epic edges. Whether e1 → S
(inside the P subtree) counts as a "cross-epic" link from P's point of view is
not stated.

**Required.** State how the parent map shows a declared edge whose endpoint is
a descendant of a displayed child epic. The options include rolling it up onto
the child-epic node as a distinctly styled derived connector that keeps its
underlying source edges for detail and audit, showing it as a boundary link
annotated with the descendant, or deliberately omitting it with a coverage
note. State whether rolled-up connectors are inputs to reduction, can serve as
witnesses, or neither. Add a fixture to the nested-epic qualification on
line 64 that has a sibling → nested-descendant edge and checks the chosen
behavior.

### R1-F002 — Filtered and expanded views do not define order implied through hidden nodes or what counts as a layer

**Where.** Lines 49 (expand one layer at a time), 51 (recompute omissions;
"Draw a connector only for a verified relationship"), and 65 (filtering
fixture).

**Problem.** Line 51 restores a *declared* edge when its witness disappears.
It does not cover the more common case of order that is implied but never
declared. Take A → B → C, where A → C is not declared and a lifecycle filter
hides B (for example, "hide Done"). The visible view then shows A and C as
unrelated. Hiding completed work is likely to be the most common filter, and
it would disconnect the remaining graph and remove the ordering that the map
exists to show. "Verified relationship" might or might not cover a fully
admitted transitive path through hidden nodes, so two implementers could build
opposite behavior.

Line 49 also does not say whether "one layer" upstream or downstream follows
declared edges or reduced (displayed) edges. In #133, expanding T02 downstream
over declared edges brings in T04, T05, T07, T10 and T11 together, including
the shortcut to T05. Over reduced edges it brings in T04, T07 and T10. The
user-visible result differs.

**Required.** Say whether the viewer shows implied order through filtered or
collapsed nodes, for example as a distinct "via hidden" connector derived only
from admitted edges and explained in detail. If it does not, say that it does
not and how the view warns that order is hidden. Define a layer for
expand/collapse as one step along either declared edges or displayed (reduced)
edges. Extend the line 65 qualification to cover a filter that hides an
intermediate node with no declared shortcut.

### R1-F003 — Package placement for the static command conflicts with its independence from the viewer runtime

**Where.** Frontmatter `package: aitm-viewer` (line 5). Lines 14, 22, 29 and
58 ("The static command has no viewer runtime prerequisite"; it uses "the
existing planning reader's lifecycle rules"; Graphviz is needed at generation
time).

**Problem.** In the M6 plan, `aitm-viewer` is the released-Core consumer.
Pickup of V03 #250 waits for the M1 Core release #72, and the product viewer
uses TypeScript generated from Core JSON Schema with no Node at runtime. The
static command reads a Git pin through the shipped planning reader (the
`tools/story_dashboard` path that V01 reuses) and needs Graphviz. If the
command lives in `aitm-viewer`, it takes on that package's release and
dependency gates and makes Graphviz a dependency of the package, which
contradicts line 58. If it lives elsewhere, the frontmatter is wrong. The
draft says the two deliverables "share semantics and fixtures" (line 14) but
does not say whether that means one implementation of reduction, witness
selection and coverage, or two implementations (for example Python and
TypeScript) held to shared golden fixtures. That choice affects estimates and
how conformance is checked.

**Required.** Name the owning location or package for the static command and
for the viewer add-on separately. Say whether reduction and audit logic is
shared code or duplicated under a conformance contract. If it is duplicated,
state that the shared fixtures' expected graph and audit outputs are the
conformance oracle for both.

### R1-F004 — The published bundle path omits the visibility profile, and "the commit containing the inputs" is ambiguous

**Where.** Lines 35 and 37 (record the visibility profile; path
`plan/dependency-maps/<source-planning-commit>/`; "Use the commit containing
the inputs as the source pin"). Also line 22 (atomic replacement of a prior
bundle).

**Problem.** Line 35 makes the visibility profile part of the bundle's
identity, but the publication path is keyed only by source commit. Two
approved bundles from the same pin for different audiences or destinations
would collide at the same path. Under the atomic-replacement rule on line 22,
one would silently replace the other as the "prior valid bundle". The
lifecycle cutoff is recorded but is not part of the key either. Separately,
every descendant commit "contains the inputs", so the phrase does not pin a
single commit. The intended meaning is the exact commit the generator read.

**Required.** Key published bundles by source pin plus the visibility profile
(and the cutoff, if the cutoff can differ for the same pin), or state that
only one profile per epic and pin is allowed. Replace "the commit containing
the inputs" with "the exact planning commit the bundle was generated from".

### R1-F005 — Reduction can use paths through boundary or external nodes as witnesses

**Where.** Line 28 ("Reduce only ordinary prerequisite edges between
displayed children … shortest witness through final displayed edges in the
full admitted view") and line 21 (the witness is "made entirely of displayed
arrows").

**Problem.** Boundary links are displayed arrows (line 28), so by the current
wording the witness for an internal edge A → B could be A → X → B, where X is
an external story drawn as a boundary stub. The internal arrow A → B would
then be removed, and the only visible order between two siblings would run
through another epic's stub. Boundary stubs are usually drawn as terminals,
so this reads as A and B being unrelated. It also makes the internal map
depend on the completeness of the external scan, which the draft otherwise
treats as partial (line 30). The same applies to epic-level gate nodes.

**Required.** State that a witness path must consist only of internal
child-to-child displayed edges. Boundary links and gate edges are never
witnesses.

## Required changes

1. **R1-F001.** Define how the parent map shows dependencies between a
   sibling and a descendant of a displayed child epic, and how these interact
   with reduction and witnesses. Add the matching nested-epic fixture to the
   qualification.
2. **R1-F002.** Define whether, and how, implied order through filtered or
   collapsed nodes is shown. Define "layer" for expand/collapse as a step on
   either declared or displayed edges. Add a filter fixture that hides an
   intermediate node with no declared shortcut.
3. **R1-F003.** Name the owning location for the static command and for the
   viewer add-on. State whether graph logic is shared code or duplicated under
   a fixture-based conformance contract. Correct or qualify
   `package: aitm-viewer`.
4. **R1-F004.** Include the visibility profile (and the cutoff, if it can
   vary) in the published bundle key, or limit publication to one profile per
   pin. Replace "the commit containing the inputs" with the exact generation
   pin.
5. **R1-F005.** Restrict witness paths to internal child-to-child displayed
   edges.

## Optional suggestions

1. Make the Mermaid Markdown and the audit byte-deterministic for a given
   admitted projection. Their text is fully under the generator's control, so
   only the SVG needs to rely on graph and audit equality. Specify the
   tie-break order for "deterministic shortest" witnesses, for example
   lexicographic by story number, so that both implementations agree.
2. Say whether readiness is shown anywhere in the map or detail. The draft
   currently mentions readiness only in negative rules (lines 29-30). If it is
   never shown, saying so avoids an implied feature.
3. Line 56 says "Preserve the existing #258 and #260 release dependencies".
   Spell out the intent, which presumably is that the follow-on is not added
   as a prerequisite of #258 or #260. Name the release vehicle for the viewer
   add-on, given that it extends a #251 surface that ships in the M6 release.
4. Say whether cycle detection covers cycles that close only through boundary
   or external edges. If it does not, say that it does not. Line 30 currently
   covers only "the admitted edges".

## Decision

revisions-requested
