<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-93e744c9779ee4cd9f592c59ba00364a"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/264/design/dependency-maps.md"
artifact_commit: "d5c1413a0658f904de7ed921bec872797a376f15"
artifact_blob: "06aabce1e95b449363555dc3dad4ce3a368ec7bb"
artifact_digest: "sha256:f8d229b076947ac00fae768ea4f0df566ecabb5e74fae50ce3c1192388724ddf"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:2d641c6d7af179cf4dd5a85a3bdc8bfac47ffaf80a900a255d16eb349a917115"
  identity_source: "runtime"
started_at: "2026-11-12T15:03:40.810Z"
submitted_at: "2026-11-12T15:06:06.243Z"
finding_ids: ["R1-F001"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is an independent round-1 review of the graduated design
`.aitm/stories/002/264/design/dependency-maps.md` at blob
`06aabce1e95b449363555dc3dad4ce3a368ec7bb` (commit `d5c1413`).

**Read coverage.** I read the whole artifact (lines 1-61 of 61) in one Read
call. I also read the pre-graduation `draft.md` attachment (68 lines) and
compared the two. The body is the same as the accepted draft except for
three changes. The YAML frontmatter is gone, including
`package: aitm-viewer`. The sentence "The frontmatter package identifies the
viewer feature" is gone. "Status. Design review candidate…" now reads
"Scope." No graph, lifecycle, publication or qualification rule changed in
graduation. For context I read the pre-graduation builder check
(`attachments/pre-graduation-review/review.md`), both reviewer responses from
the earlier XPR draft review, the M6 read-only preview plan
(`.aitm/stories/002/247/attachments/2026-11-11-1-m6-read-only-preview-plan.md`)
and the #264 `story.md`. I did not use Git, so I could not check content at
the historical pins.

**Source checks (working tree at the current head).**

- **#133 counts (line 56).** `.aitm/stories/001/133/story.md` lists 41
  `children` (138-178). Each child's `story.md` `blocked-by` gives 64 edges,
  all between children. These match `leaf-issue-receipt.json`
  (`leaf_count: 41`, `dependency_count: 64`) edge for edge. I did the
  transitive reduction by hand from the `blocked-by` lists. Exactly nine edges
  are implied by longer paths: 139→142, 144→146, 139→148, 152→160, 146→168,
  162→169, 162→173, 162→174 and 170→176. That leaves 55 displayed arrows.
  #162's `blocked-by` is `[161]`, so #160 → #162 is not in the source. I
  searched every `story.md` for a `blocked-by` that names a #133 child. Only
  the 38 non-root children matched, so at this head the epic has no outgoing
  or incoming child boundary links.
- **#133 → #2 gate.** #133 has `blocking: [2]` and
  `.aitm/stories/000/2/story.md` has `blocked-by: [100, 133]`. The gate
  therefore comes from the dependent's `blocked-by`, which agrees with the
  edge-source rule on line 20.
- **#227 / #193 (line 20).** #227 has `blocked-by: [193]` and #193 has
  `blocking: []`. The two records sit under different shard directories
  (`002/` and `001/`), which supports the line 20 requirement to index every
  supported record location.
- **Sibling tool precedent.** In the M6 preview plan, Leaf B line 34 requires
  "a required local-review or synthetic visibility profile" as an explicit
  CLI input. It uses an "explicit reviewed allowlist of story IDs and approved
  display titles" for real-data profiles (Leaf A line 25). This matters for
  F001 below.

**Assessment.** The graph semantics are complete and consistent. These
include arrow direction, a single edge-source field, boundary versus internal
witnesses, nested-descendant labelling, reduction scope, one-hop layers on
declared edges, hidden-path marking, coverage states, atomic last-valid
bundles and visibility before projection. The qualification numbers check out
against the source. One interface gap remains. Several rules depend on a
visibility profile, but the static command never takes one, and the outputs
do not record it. Two wording points carried over from the draft are listed
as optional.

## Findings

### R1-F001 — The static command interface has no visibility profile input, and the outputs do not record one

**Where.** Line 13 defines the command contract: "Take an epic number and an
exact Git planning commit. Read only that snapshot and write a bundle to an
explicit output path." Line 14: "Put the full planning commit on all three
outputs." Line 25: "Apply the visibility policy before graph construction,
reduction, path selection, counts, and details." Line 29: "generate the
bundle from a projection admitted for the plan's audience and destination
under the owning project's visibility policy. Record the authorized source
pin, lifecycle cutoff, and visibility profile." Line 31 keys the bundle path
by `<source-planning-commit>/<visibility-profile>/`. Line 15: "The two
Markdown files are byte reproducible for the same admitted input."

**Problem.** Lines 25, 29 and 31 all need a visibility profile, but line 13
does not take one. An implementer who follows line 13 has no way to choose an
admitted projection. The command would either always produce an unfiltered
bundle or need a profile mechanism that the design never defines. The design
also does not say which profile the private local bundle (line 29) uses. If
it is unfiltered, the line 31 path still needs a profile key for it, and line
25's "before graph construction" rule needs a named no-op profile. Line 29
says to record the profile, but line 14 places only the planning commit on
the outputs, so the reviewed Markdown, SVG and audit do not show which
admission produced them. The attachment review on line 29 checks those exact
files against the destination, so the profile needs to be on them. The
"same admitted input" reproducibility claim on line 15 also depends on the
profile.

There is also no stated source for "the owning project's visibility policy"
in the static Git adapter. The sibling M6 preview (the same
`tools/story_dashboard/` package) solved this with a required explicit
profile argument and a reviewed allowlist pinned in the planning project.
Without a similar decision, the Python and TypeScript implementations could
admit different record sets. That would break the shared-fixture conformance
contract on lines 7 and 59. Restricted-record fixtures in particular would
have no defined admission input.

## Required changes

1. **R1-F001.** Make the visibility profile an explicit, required input of
   the static command on line 13. Name the profile used for the private local
   bundle, for example a versioned private or local-review key, so that line
   25 and the line 31 path apply to every bundle. Put the profile key, and
   its version or digest, on all three outputs beside the planning commit on
   line 14. State where the static adapter gets the policy that a profile
   resolves to. Either reuse the M6 preview's reviewed allowlist mechanism or
   name another pinned source. In the line 59 qualification, state that the
   Python and TypeScript fixtures use the same profile input.

## Optional suggestions

1. Line 35 still says "outside this draft". Now that the document is the
   graduated design, use "outside this design".
2. Line 22 says to reduce "ordinary prerequisites between displayed
   children" and to preserve "epic gates". Line 21 shows that "epic gates"
   means explicit gates of the *selected* epic. A declared edge between a
   sibling story and a displayed *child epic* node is still an ordinary,
   reducible prerequisite, but the text could also be read as an epic gate.
   One clause would remove the ambiguity.
3. Carry the earlier XPR round-2 optional suggestions into the Plan as
   explicit decisions:
   - an indicator on the parent map for descendant-level links between two
     child epics;
   - a fully lexicographic witness tie-break by ordered story-ID sequence
     after path length;
   - readiness display;
   - the release vehicle for the viewer add-on;
   - cycles that close only through boundary edges.

## Decision

revisions-requested
