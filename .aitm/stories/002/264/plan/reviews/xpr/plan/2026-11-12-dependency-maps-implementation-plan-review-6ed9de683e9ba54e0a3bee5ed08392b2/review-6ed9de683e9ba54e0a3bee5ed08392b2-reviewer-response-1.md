<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-6ed9de683e9ba54e0a3bee5ed08392b2"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md"
artifact_commit: "f785e3d7f5f703fe5ddc9c100df5a081db1c392f"
artifact_blob: "8841c7ca0c0edf28613459ccd6038ab71bff758b"
artifact_digest: "sha256:fd559940fee27e8095da863a840d10a5d8d0ff2816ea8efd5c635ecc214c22ed"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:4f94a9ca3ce36df5862bd1e9007f2569c595c2bad97733e323283998eb0d7963"
  identity_source: "runtime"
started_at: "2026-11-12T15:09:38.164Z"
submitted_at: "2026-11-12T15:13:27.211Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is an independent round-1 review of the implementation plan
`.aitm/stories/002/264/plan/dependency-maps-implementation-plan.md`. It covers
blob `8841c7ca0c0edf28613459ccd6038ab71bff758b` at commit `f785e3d`.

**Read coverage.** I read the whole plan (lines 1-107 of 107) in one Read
call. I also read these:

- the whole accepted design `.aitm/stories/002/264/design/dependency-maps.md`
  (lines 1-61), which is the spec the plan cites;
- `.aitm/stories/002/264/story.md`;
- the round-1 design review response
  (`review-93e744c9779ee4cd9f592c59ba00364a-reviewer-response-1.md`), to check
  how its optional items were carried into the plan.

The plan names the existing reader `tools/story_dashboard/evidence.py`. That
code is not in this planning worktree, so I read it in the code checkout at
`/Users/kpburson/projects/aitm-workspace/trunk`. I read
`tools/story_dashboard/evidence.py` lines 40-160 (record types and
`PlanningTree`) and lines 500-1011 (`_Git`, `_header`, `_facts`, `_graph`,
`read_tree`). I also read `tests/test_evidence.py` lines 270-310, and I
searched the dashboard README and tests for how they handle real planning
pins. In the planning worktree, I searched every story journal under
`.aitm/stories/001` for `core.link.*` event types. I also checked the
`predecessor-added` and `child-removed` events against the affected
`story.md` headers. I did not use Git. Shell access was limited to the two
prescribed peer-review commands, so I could not recompute the design SHA-256
cited on plan line 11 or read content at historical pins.

**Assessment.** The plan follows the design closely.

- The slice order separates static, local-viewer and hosted delivery.
- Pickup gates hold the viewer slices on #250/#251 contract readback and
  hold attachment on profile-approval binding.
- The five named failure cases (plan line 38) each map to a slice.
- The round-1 design review's optional items are now explicit decisions:
  - a numeric lexicographic tie-break (line 36);
  - direct-child scope with no descendant indicator (line 35);
  - readiness from the released detail contract (line 33);
  - cycles through external chains outside the validation claim (line 35);
  - the release vehicle pinned at D8 pickup (line 106).
- The #133 numbers and pins match the design.

The plan has four gaps:

- D1 assumes that the existing reader already supplies what the dependency
  snapshot needs. It does not read dependency fields or non-canonical record
  locations (F001).
- The shared conformance fixtures do not say which side of the admission
  boundary they sit on, or how the TypeScript suite reaches them (F002).
- The real-pin #133 assertions have no defined repository source in a test
  suite that is otherwise hermetic (F003).
- Two qualification cases the design requires are not in any slice's test
  list (F004).

## Findings

### R1-F001 — D1's "reuse the reader" premise does not hold for dependency fields or historical record locations

**Where.** Plan line 42: "Reuse the pinned Git reader and lifecycle fold in
`tools/story_dashboard/evidence.py`. Refactor the reader's public surface only
where the exact graph snapshot needs access to existing indexed records."
Line 46: "Read supported historical record locations by identity and flag
conflicts … The dependent's `blocked-by` supplies each declaration." Line 48
names `test_dependency_source_indexes_historical_ids`. Design line 20: "Index
the pinned story records by identity, including supported historical record
locations."

**Evidence (trunk `evidence.py`).**

- `_header` (lines 587-606) keeps only `id`, `title`, `state`, `parent`,
  `children`, `estimate`, `updated` and `created`. It drops `blocked-by` and
  `blocking`. `PlanningTree` (lines 139-153) has no raw header. Story blobs are
  reachable only through the private `_blobs` field. Dependency fields are
  therefore not "existing indexed records".
- The reader applies eligibility rules to header fields. A header whose
  `updated` is after the cutoff is ignored and recorded as an
  `ineligible-header` gap (lines 753-761). Duplicate keys are rejected
  (line 604). If D1 parses `blocked-by` outside `_header`, it would need to
  repeat these rules exactly. Otherwise a snapshot could take edges from a
  header whose state and parent the reader withheld. The design forbids this
  ("Take state from the same source snapshot as the graph", line 23).
- `_facts` (lines 695-700) reads only the canonical
  `.aitm/stories/<id//100:03d>/<id>/story.md`. It skips any other `story.md`
  with `continue` and records no gap. The reader has no "historical location".
  Neither the plan nor the design names which locations are supported. With
  the plan as written, `test_dependency_source_indexes_historical_ids` has no
  defined fixture, and the lifecycle fold that D1 reuses would not cover such
  records.
- The reader reports problems as `Gap` codes and does not raise. Examples are
  `invalid-story`, `ancestry-conflict`, `ancestry-missing`,
  `ineligible-header`, `invalid-state` and `missing-journal`. Design line 24
  needs three outcomes: hold, partial, or display as Unknown. The plan never
  maps the reader's gap codes to those outcomes. Two implementers could map
  `ancestry-conflict` or `ineligible-header` on an expected child differently.
  One would hold the replacement; the other would render a partial map.

A related fact supports the header-based source. In the journals,
`core.link.dependency-added` and `core.link.predecessor-added` events carry
the same `blocked-by` IDs as the headers. For example, #182's
`predecessor-added` `{"blocked-by":117}` matches `blocked-by: [117]`. So no
second event fold is needed. The header path still has to go through the
reader's eligibility rules.

**Risk.** D1 cannot be delivered within its stated refactor limit. The likely
workaround is a second, partial header parser, which breaks the design's
same-snapshot rule. The historical-location requirement cannot be tested as
written.

### R1-F002 — The shared fixture contract does not fix which side of the admission boundary the input sits on, or how the viewer suite consumes it

**Where.** Line 7: "Each adapter admits data before graph construction …
Shared fixtures define the expected graph and audit results." Line 53: "Each
case contains the same explicit profile input and expected output for both
test runners." Line 55:
`project_dependencies(snapshot, epic_id)` takes the Git `AdmittedSnapshot`.
Line 80: `projectDependencyMap(snapshot: AdmittedCoreSnapshot, …)` takes the
#250 export type, whose schema is checked only at D5 pickup (line 28). Line 82
asks for parity over "every D2 fixture, including … restricted witness and
counts cases". Design line 59 asks for a restricted-record test and "the same
profile input" in both languages.

**Problem.** D2 writes the fixtures before the Core export schema is known,
and the plan does not define the fixture input format. Each choice leaves a
hole:

- **Fixture input already admitted.** A restricted record is already gone
  before either runner sees it. The "restricted intermediate cannot affect
  counts or audit" case (line 57) then tests nothing: neither adapter's
  admission runs. Plan line 38 calls false witnesses from restricted records
  a key failure case for D2 and D5.
- **Fixture input before admission (records plus profile).** Each runner
  needs a loader that builds its native source. Python needs a temporary Git
  tree, and TypeScript needs a Core-export document. The plan names neither
  loader. It also never says how a static `dependency-map-profiles` profile
  maps to the viewer's visibility context. Line 39 of the design says the
  viewer uses "the existing viewer refresh and visibility policies", not
  static profiles.

The fixtures live in `tools/story_dashboard/tests/fixtures/dependency-maps/`
(line 53). The parity test lives in `packages/aitm-viewer/web/tests/` (line
81). The M6 decomposition plan makes `packages/aitm-viewer/web` its own
package with its own `package.json`. The plan does not say whether Vitest
reads the fixtures across the package boundary or uses a copy with a digest
check. It also does not say whether a D2 fixture change must re-run D5 parity.
Without this, the two fixture sets can drift while both suites stay green.
That would break the conformance contract on design line 7.

### R1-F003 — #133 real-pin assertions have no defined repository source in a hermetic unit suite

**Where.** Line 58 (D2): "Implement projection and assert #133 has 41 direct
children, 64 declared internal edges …". No pin or source is named. Line 71
(D4) adds `tests/test_dependency_map_replay.py` "for the pinned
qualification". Line 73 requires running it at `05d3330…` and `ea4a838…`
together with "the four dependency map test modules and the shipped dashboard
suite".

**Evidence.** The existing dashboard tests are hermetic. `test_evidence.py`
builds temporary repos, and no test reads a real planning pin. The
`tools/story_dashboard/README.md` (lines 13-34) treats real-pin builds as an
operator procedure. It fetches `origin/planning` and passes `--repo` and
`--commit`. The planning commits live on the `planning` branch history. That
history is not the code checkout the suite runs in.

**Risk.** Either the default `pytest` run fails where planning history is not
fetched, or the test is skipped quietly. A skipped test could then be cited as
the D4 qualification. The D2 assertion gives no pin, so the expected counts
are not tied to a specific snapshot. The design ties them to `ea4a838`
(design line 56).

### R1-F004 — Two qualification cases the design requires are missing from the slice test lists

**Where.** Design line 58: "Use boundary and nested-epic fixtures to prove
containment, crossing gates, shared nodes, and reverse-field diagnostics …
Test an unresolved incoming link and an incomplete outgoing scan with zero
known edges." Design line 20 keeps a declared edge and reports the
reverse-field disagreement (#227 → #193).

**Problem.**

- **Reverse-field disagreement.** No slice tests it. D1's case list (line 48)
  and D2's fixture list (line 57) leave it out. No plan line names the output
  surface for the disagreement (audit, diagnostics, or story detail). The
  admission question is also open. An admitted story's `blocking` field can
  name an excluded story, and the diagnostic must not reveal that ID.
- **Explicit epic gate.** No synthetic fixture covers it. The only gate case
  is the real #133 → #2 assertion (line 58), which F003 already finds
  unreliable. D2 has no fixture for a gate of the selected epic, so nothing
  shows that a gate is rendered separately, never reduced, and never used as
  a witness.
- **Unresolved incoming link.** D2 lists "zero known outgoing edges with
  partial coverage". The incoming-direction case appears only as "unresolved
  link" in D1 and "unresolved boundary" in D5. It is not in the shared
  fixtures, so the two runners are not held to the same incoming-coverage
  result.

## Required changes

1. **R1-F001.** Make these changes in D1:
   - Allow extending `evidence.py` header parsing to `blocked-by` and
     `blocking`. Keep the same eligibility rule (`updated` ≤ cutoff), the same
     duplicate-key rejection and the same gap reporting as `state` and
     `parent`. Run the existing dashboard tests as the regression check, which
     line 49 already partly does.
   - Name the supported historical record locations. Alternatively, state
     that only the canonical shard path is supported. In that case, a
     non-canonical `story.md` claiming an in-scope identity becomes a reported
     conflict, not a silent skip. Define the fixture for
     `test_dependency_source_indexes_historical_ids` to match.
   - Add a table that maps each reader `Gap` code that can affect an epic,
     expected child, boundary endpoint or lifecycle label to its outcome:
     hold, partial, or Unknown.
2. **R1-F002.** Define the shared fixture schema as adapter-neutral input
   *before* admission: the story records, a profile or visibility input, and
   the expected outputs. Specify the loader in each runner. The Python loader
   builds a temporary Git tree, and the TypeScript loader builds a
   Core-export-shaped document after D5 pickup. Both loaders must go through
   their adapter's admission step. State how the static profile in a fixture
   maps to the viewer's visibility context. State how the viewer suite finds
   the fixtures, either by a shared path or by a digest-checked copy, and
   require D5 parity to re-run whenever a D2 fixture changes.
3. **R1-F003.** In D2, either pin the #133 assertion to `ea4a838` as a
   digest-pinned fixture extracted from that commit, or move the assertion to
   D4. In D4, state how `test_dependency_map_replay.py` gets the planning
   repository, for example through a required path or environment variable.
   It must be skipped with a stated reason in the default suite and never
   pass vacuously. The qualification record must hold the repository, both
   pins and the passing run. A skip is not qualification evidence.
4. **R1-F004.** Make these changes in D2, and carry them into D5 parity:
   - Add a reverse-field disagreement fixture modelled on #227/#193, including
     a variant whose reverse field names a restricted story.
   - Name the output surface where the disagreement is reported.
   - Add a synthetic explicit-gate fixture showing that the gate is separate,
     not reduced, and never a witness.
   - Add an unresolved incoming boundary-link case alongside the outgoing
     zero-edge case.

## Optional suggestions

1. `evidence.py` does not fold `core.link.child-removed`. One such event
   exists, at `.aitm/stories/001/100/events.jsonl:32`, where #230 moves to #2.
   The explicit `parent-set` in #230's journal resolves #230's parent correctly
   today. The stale child claim from #100 is still kept and reported nowhere.
   Define D2's "inconsistent containment" against the reader's resolved
   `parents` and gaps, not against raw `children` lists. Otherwise maps such
   as #100's could be held, or not held, depending on which source an
   implementer compares.
2. D6 is estimated at 4.00 h, at the split limit. It covers the exploration
   model, the graph view, the text view, the detail pane, keyboard access,
   focus recovery, the narrow layout and accessibility checks. Consider
   splitting it now into an exploration-model leaf (`exploration.ts`) and a
   view-and-accessibility leaf.
3. D3 leaves out the design's rendering preference (design line 14): "Prefer a
   top-to-bottom overview and align the entry stories where the renderer
   supports it". Add it to D3 so the Mermaid and Graphviz outputs follow the
   same orientation rule.
4. D7's test names (`test_older_refresh_cannot_replace_current_context`, line
   98) are Python-style names in a Vitest file. Use `describe`/`it` names that
   follow the viewer's test conventions.
5. Say whether the static outputs show readiness. Line 33 sends readiness to
   the viewer's detail contract. One sentence saying that the static bundle
   shows only lifecycle state, and no readiness, would prevent the static
   bundle from implying readiness.

## Decision

revisions-requested
