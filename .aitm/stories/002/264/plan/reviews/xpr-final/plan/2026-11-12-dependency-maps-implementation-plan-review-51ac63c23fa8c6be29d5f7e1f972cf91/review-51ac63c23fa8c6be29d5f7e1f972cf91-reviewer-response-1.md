<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-51ac63c23fa8c6be29d5f7e1f972cf91"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md"
artifact_commit: "e9347ea43609adde86483b16d103c66df4fdf15e"
artifact_blob: "24b9e278c548914d73c996a25143dc09f2a98161"
artifact_digest: "sha256:b82e504caa40e83ee3d7384bfd214678eb97aced688f06ec99b521c596dfd012"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:512bef0fbe910931845325d44760f8e5b697c07b3e91a2ccd5136fb6394d87d2"
  identity_source: "runtime"
started_at: "2026-11-12T15:18:42.731Z"
submitted_at: "2026-11-12T15:22:52.911Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is an independent final review of the implementation plan
`.aitm/stories/002/264/plan/dependency-maps-implementation-plan.md`. It covers
blob `24b9e278c548914d73c996a25143dc09f2a98161` at commit `e9347ea`.

**Read coverage.**

- The whole plan, lines 1-122 of 122, in one Read call.
- The whole accepted design `.aitm/stories/002/264/design/dependency-maps.md`
  (lines 1-61) and `.aitm/stories/002/264/story.md`.
- The earlier plan review `review-6ed9de683e9ba54e0a3bee5ed08392b2`: its
  round-1 reviewer response and its manifest. I used them to confirm that
  each earlier required change (R1-F001 to R1-F004) now appears in the plan.
- The code the plan builds on. It is not in this planning worktree, so I read
  it in the code checkout at `/Users/kpburson/projects/aitm-workspace/trunk`:
  - `tools/story_dashboard/evidence.py` lines 556-1011, which cover
    `_Git.tree`/`read`, `_root`, `_header`, `_header_value`, `_facts`,
    `_graph` and `read_tree`, plus the `ROOT`, `MAX_BLOB` and `as_of` uses;
  - `tools/story_dashboard/README.md` lines 1-45;
  - the imports and runner in `tests/test_evidence.py` and
    `tests/test_render.py`.
- In this planning worktree I searched every `story.md` under `.aitm/stories`
  for `blocked-by:`. I also read the dependency and containment header fields
  of #2, #133 and #201, and listed the historical-layout records
  `.aitm/stories/001/{201,202,203,204,209,210}`.

**Limits.** Shell access was limited to the two prescribed peer-review
commands, and the `help` lookup was denied. So I did not recompute the design
SHA-256 on plan line 11, did not read content at the historical pins
`05d3330`/`ea4a838`, and did not run any tests. I did not use Git.

**Verification of the plan's code premises against trunk.**

- **D1's `_header` opt-in.** `_header` (lines 587-606) keeps a fixed key set
  that excludes `blocked-by`/`blocking`. It rejects duplicate keys
  (line 604). Eligibility is computed in `_facts` from `updated` ≤ `as_of`
  (lines 753-761). The plan's opt-in capture, which keeps the duplicate-key
  rejection and the eligibility cutoff while existing callers keep their
  current field set (plan line 43), fits this seam without a second parser.
- **D1's location map.** `_facts` drops any `story.md` that is not at the
  canonical `_root(story)` path (lines 699-700). It reads the journal only at
  `_root(story) + "events.jsonl"` (line 717). The plan's opt-in location map
  and "actual directory's sibling journal" rule fix both. The historical case
  it names is real. `.aitm/stories/001/201/story.md` exists with `id` 201,
  canonical bucket `002`, and no `002/201` directory. The same holds for 202,
  203, 204, 209 and 210.
- **D1's gap table.** Every gap code in the table (lines 49-55) is emitted by
  trunk `_facts`/`_graph`. These are `future-story` (712), `invalid-story`
  (715), `invalid-journal` (723), `unbound-draft-event` (739),
  `future-event` (743), `invalid-event` (747), `missing-journal` (749),
  `ineligible-header` (761), `invalid-ancestry` (768/780/819/825),
  `invalid-state` (790/806), `ancestry-missing` (843/859),
  `ancestry-conflict` (849) and `ancestry-cycle` (873).
- **Containment.** `_graph` ignores child claims once an explicit
  `core.link.parent-set` exists (lines 845-852). That matches the plan's
  "a stale child claim superseded by a valid parent change cannot resurrect a
  child" (line 43). It also covers the earlier optional note about the
  unfolded `child-removed` event.
- **Cutoff.** `read_tree` parses the committer timestamp and requires
  `as_of >= commit_time` (lines 982-988). Using the exact commit's UTC
  committer time as the cutoff (plan line 33) is accepted by the reader.
- **Header data.** All 214 `story.md` records in the current planning tree
  carry a `blocked-by:` key in JSON-list form, which `_header_value` parses.
  The empty-versus-unavailable distinction (line 51) therefore does not make
  the current tree's records unavailable. #2 has `blocked-by: [100, 133]` and
  #133 has `blocking: [2]`, which matches the separate #133 → #2 gate in D4.
- **Commands.** The test commands (`python3.13 -m unittest discover -s
  tools/story_dashboard/tests -p …`) and the `python -m
  tools.story_dashboard.<module>` CLI form match the existing suite
  (`unittest`, `from tools.story_dashboard import …`) and the README's
  invocation style.

**Assessment against the design.**

- Static, local-viewer and hosted delivery are separately qualifiable. D8 is
  explicitly limited to the follow-on, and the M6 13-item scope is preserved
  (lines 27, 121).
- The earlier required changes are carried in:
  - the fixture input is defined before admission, with a loader per runner,
    profile-to-visibility-context mapping and path-based parity reruns
    (lines 62, 91-92);
  - the #133 replay is hermetic by default, fails when explicitly requested
    without its prerequisites, and a skip cannot qualify D4 (lines 82-83);
  - reverse-field, explicit-gate and incoming/outgoing coverage fixtures are
    present (line 66).
- The graph rules on lines 33-37 match design lines 19-25:
  - edges point prerequisite → dependent;
  - boundaries and gates are never witnesses;
  - the tie-break is numeric lexicographic;
  - witnesses are recomputed after collapse or filter;
  - admission happens before counts and diagnostics;
  - readiness is withheld on insufficient coverage, and the static bundle
    shows lifecycle state only.
- D3's staged, validated, single-rename publish into a new directory meets
  design line 15's "leave the prior valid bundle available".
- D7's tightened transition rule (line 114) meets design line 39 and is
  stricter on a visibility change. On any project or visibility change it
  replaces the whole graph, text, audit and detail surface with an
  unavailable state, keeps only the selection key, and restores selection only
  if the new admitted graph contains the story.
- The five failure cases on line 39 each map to a slice with a named test.
- Leaf estimates are all under four agent-hours. D6 is now split into D6a and
  D6b.

I found no defect that blocks acceptance. The optional suggestions below are
small clarifications that an implementer could otherwise settle at pickup.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Scope of "the affected direction" for an unreadable record (D1 table,
   line 51, right column).** In the Git adapter, the dependent's `blocked-by`
   is the edge authority. A non-excluded record whose identity or
   `blocked-by` cannot be read could name any admitted child as its
   prerequisite. So the outgoing direction is unknown for every child, not
   just one. Say whether this marks outgoing coverage partial for every
   admitted child, or for the map as a whole. Also say that a record already
   excluded by the profile allowlist (by path ID) does not change admitted
   coverage. The D2 `expected.coverage` fixtures and D5 parity then pin one
   shared granularity, and the static adapter cannot reveal that an excluded
   record exists through a partial label.
2. **The word "destination" means two things (lines 45, 73, 76).**
   "Destination" names the approved attachment audience or location
   (`--attachment-destination`, profile `destination`). It also names the
   CLI's `--output` directory ("Stage … under the destination's parent";
   "Reject an occupied destination"). Call the second one "output directory"
   so the profile-approval match and the atomic-publish rule cannot be
   confused.
3. **The occupied-output rule against SVG that is not byte-reproducible
   (line 76).** "Reject an occupied destination with different contents"
   implies that an identical rerun succeeds. Design line 15 notes that SVG
   bytes depend on renderer and font versions. Say how "different contents"
   is judged. One option is Markdown bytes plus SVG graph content. Another is
   to always require a non-existent output path. Either avoids a rerun on
   another host failing for reasons unrelated to the graph.
4. **Read-only assertion for the static command (D3/D4).** The design says
   the command "does not change issues, planning records, or the checkout"
   (design line 13). D3 states that the command has no issue or publication
   API, but no test asserts it. Consider adding to `test_cli_bundle_renderers_agree`,
   or to the D4 replay, a check that the source repository's refs, index and
   worktree are unchanged after a run, and that only the output directory
   is written.

## Decision

accepted
