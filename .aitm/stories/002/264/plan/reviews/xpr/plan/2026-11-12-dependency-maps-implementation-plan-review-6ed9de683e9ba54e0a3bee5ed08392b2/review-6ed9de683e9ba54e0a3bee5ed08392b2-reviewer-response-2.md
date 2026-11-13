<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-6ed9de683e9ba54e0a3bee5ed08392b2"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md"
artifact_commit: "869e0237f13630152fcdec138730398000b7c04d"
artifact_blob: "276e78a1df75a842ec515082cb511e1c49538b18"
artifact_digest: "sha256:01d990bf16e400a6de2e56a5d88467b76c4aa3b56583920e913101f92e71aa5f"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:4f94a9ca3ce36df5862bd1e9007f2569c595c2bad97733e323283998eb0d7963"
  identity_source: "runtime"
started_at: "2026-11-12T15:09:38.164Z"
submitted_at: "2026-11-12T15:16:47.166Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the round-2 review of the revised plan
`.aitm/stories/002/264/plan/dependency-maps-implementation-plan.md` at blob
`276e78a1df75a842ec515082cb511e1c49538b18` (commit `869e023`).

**Read coverage.** I read these documents in full:

- the revised plan (lines 1-121 of 121), in one Read call;
- the author response `review-6ed9de683e9ba54e0a3bee5ed08392b2-author-response-1.md`
  (lines 1-54).

I compared the plan section by section with my round-1 findings and with the
accepted design, which I read in full in round 1. The design SHA-256 on plan
line 11 is the same as in round 1. I did not use Git. Shell access was limited
to the prescribed peer-review command, so I could not recompute the artifact
digest in the author response.

**Source check for the new historical-layout claim (plan line 43).** The plan
now names the `.aitm/stories/001/201/story.md` layout for stories whose
canonical bucket is `002`. I checked the planning worktree:

- `story.md` records exist at `.aitm/stories/001/{201,202,203,204,209,210}/`.
- No canonical `.aitm/stories/002/2xx/` directory exists for those IDs. The
  first `002/` records are #227-#229.

In round 1 I read the trunk `evidence.py` `_facts` code (lines 695-700). It
skips any record whose path is not `_root(story)`, so today's reader silently
drops these six stories. The revised plan uses a new opt-in location map. Its
rules are:

- the numeric path ID must match the header ID;
- exactly one directory may resolve to a story, and a second location is a
  conflict;
- only regular, size-bounded blobs are accepted;
- the lifecycle fold reads the sibling journal in that same directory;
- existing callers keep canonical lookup.

These rules match a layout that really exists, and the round-1 F001 fixture
now has a concrete basis.

**Assessment.** All four round-1 findings are resolved. The author also
applied every round-1 optional suggestion. No new blocking issue appears in
the revision.

## Findings

None.

Round-1 dispositions, checked against the revised text:

- **R1-F001: resolved.**
  - Line 43 lets D1 extend `_header` to read `blocked-by` and `blocking`. The
    new fields get the same duplicate-key rejection and the same header
    eligibility cutoff as existing fields.
  - Line 43 adds the location map at the `_facts` read seam, as described in
    the source check above.
  - The table at lines 49-55 maps every reader gap code that can affect the
    map to one of three outcomes: hold, partial, or Unknown. It covers
    `future-story`, `invalid-story`, `ineligible-header`, the four ancestry
    codes, the journal and state codes, `future-event`, and
    `unbound-draft-event`. It treats an expected child differently from a
    boundary record. It keeps "empty" separate from "unavailable".
  - Line 43 also settles round-1 optional suggestion 1: a valid resolved
    parent wins over a stale child claim.
- **R1-F002: resolved.**
  - Line 62 defines a versioned fixture schema,
    `aitm.dependency-map-fixture/v1`. Its input is the raw `records` before
    admission, plus `profile`, `epic_id`, `coverage` and `expected`.
  - Each case is built into each adapter's own source format: Git blobs for
    Python, and a Core export at the policy boundary for the viewer.
  - Line 67 runs D1 admission before projection for the restricted case.
  - Line 91 loads the canonical fixtures through a repository-relative path.
    It maps each profile to a viewer visibility context with the same
    allowed identities and fields, and it runs the same raw records through
    admission before comparison.
  - Line 92 registers the fixture path so that any fixture change re-runs
    parity in both languages.
- **R1-F003: resolved.**
  - D2 is now hermetic, and the #133 count checks have moved to D4 (line 67).
  - D4 (lines 82-83) does these things:
    - asserts the full set of #133 counts at both full pins;
    - takes the planning repository from `AITM_DEPENDENCY_REPLAY_REPO`;
    - checks that the Git objects and Graphviz are present before running;
    - fails when the replay was requested but its prerequisites are missing;
    - lets the default suite skip the replay only when the replay was not
      requested;
    - states that a skip cannot count as D4 qualification;
    - keeps the repository identity, both pins and the passing result as
      evidence.
- **R1-F004: resolved.** Line 66 adds these fixtures:
  - a selected-epic gate that survives reduction and cannot supply a witness;
  - a known unresolved incoming link;
  - zero known outgoing links with partial coverage;
  - the #227/#193 reverse-field pattern;
  - a reverse-field reference to an excluded story.

  The audit is named as the place where disagreements are reported, and
  excluded IDs must never appear. Line 91 carries the gate, the reverse-field
  audit and directional coverage into D5 parity.

Round-1 optional suggestions are also all applied:

- D6 is split into D6a (model, 2.75 h) and D6b (view and accessibility,
  3.75 h), on lines 22-23 and 94-107.
- The top-to-bottom layout and entry-story alignment are now in D3 (line 76).
- D7 test cases are described as Vitest cases (line 113).
- Line 34 settles readiness: the static bundle shows lifecycle state, and
  readiness appears only in viewer detail. Line 35 withholds affirmative
  readiness when coverage is insufficient.

The revision also improves a few things beyond the findings:

- D3 renders a restricted "canary" record through an attachment profile and
  compares it surface by surface (line 75).
- D7 hides details while a visibility change is unresolved (line 114).
- D8 keeps a prior release available only while it is still authorized for
  the active audience (line 120).

## Required changes

None.

## Optional suggestions

1. **Effect of the `_header` change on existing callers (line 43).**
   `_header` rejects a duplicate key only when it is one of the captured keys.
   Adding `blocked-by` and `blocking` to that set therefore changes behavior
   for the existing dashboard too: a story with a duplicated `blocked-by` line
   would now become `invalid-story` there. Line 43 keeps canonical lookup for
   existing callers but says nothing about header validation. At D1 pickup,
   either make the new key capture opt-in like the location map, or confirm
   that the shipped dashboard suite and a current-pin snapshot are unchanged.
2. **D1 estimate.** D1 is still estimated at 3.75 h, but its scope has grown.
   It now covers the reader seam refactor, the location map, the `_header`
   extension, the gap-outcome table, the profile loader and approval binding,
   and four test groups with many cases. Re-check the estimate at pickup. If
   it is over, a natural split is reader extensions (location map and header
   fields, tested against the existing evidence suite) versus the profile and
   admission layer.
3. **The `coverage` field in fixtures (line 62).** `coverage` is listed
   beside `records` as fixture input. Say in the fixture schema whether it is
   simulated scan completeness given to the loaders, or expected output.
   `expected` already carries coverage, so the input meaning should be
   explicit to keep the two loaders from reading it differently.

## Decision

accepted
