# Story #264 Plan same-provider review, round 1

**Decision — REQUEST REVISIONS** for the exact Plan candidate identified below.

## Review evidence

- Read physical lines 1–106, including blank lines, of `.aitm/stories/002/264/plan/dependency-maps-implementation-plan.md` in the isolated review worktree. The supplied candidate commit is `f785e3d7f5f703fe5ddc9c100df5a081db1c392f`. Independently computed raw SHA-256 `fd559940fee27e8095da863a840d10a5d8d0ff2816ea8efd5c635ecc214c22ed` and rechecked it at submission.
- Read the accepted Design, lines 1–60, at raw SHA-256 `50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7`, and the #264 story, lines 1–27, at raw SHA-256 `9045ef945b49a0f7d2fc862a9854b684cd0350d26b3a774e504f786d11887529`.
- Inspected the relevant frontmatter of #72, #247, #250, #251, #258 and #260 in the planning worktree, the M6 scope and preview provisions, and the dashboard reader, test layout and CI configuration in the source checkout. No implementation or test execution was part of this review.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 15:09:24 UTC and was submitted 2026-11-12 15:11:27 UTC.

## Required changes

### R1-F001 — Specify the reader integration and retain required-input failures

Plan lines 42–49 propose access to existing indexed records, but the current reader's `_facts` ignores records outside the canonical sharded location (`tools/story_dashboard/evidence.py` lines 691–717), `_header` omits `blocked-by` and `blocking` (587–617), and its normalized ancestry can discard problematic edges while recording gaps (836–880). Exposing `PlanningTree` alone would therefore lose data needed for historical replay or turn an unreadable declaration into an empty one. Specify the bounded reader change or adapter seam that feeds historical path normalization into the existing lifecycle fold and passes the admitted raw declarations, expected containment and relevant gaps through to validation. Assign that change and regression coverage to D1. Make explicit in D1/D2/D5 that a missing selected epic or expected admitted child, unreadable required dependency field, or invalid admitted containment holds the result, while an incomplete external direction can remain an explicitly partial graph. Add a case with an unreadable direct child's declaration and an unreadable external record. Preserve valid declarations and withhold readiness when coverage is insufficient, including when the released detail carries an otherwise affirmative readiness value.

### R1-F002 — Exercise the visibility profile at both production admission boundaries

Plan lines 53–57 and 78–83 compare outputs from pure projectors that accept already-admitted snapshots. The tests can pass with a shared profile stored as unused fixture metadata, even if the production adapters admit different records. The restricted-intermediate fixture and static/hosted scope checks should include the same logical source records and explicit profile upstream of admission. Drive the Git-side and released Core-side production admission boundaries, mapping the common input to each transport, and compare the resulting graph and audit against the same expectations. At D3/D4, render an attachment-profile canary and check the exact Markdown, SVG including metadata and links, audit, and shareable diagnostics for prohibited identifiers or effects on counts and paths. The manually reviewed attachment procedure at line 74 remains a separate action.

### R1-F003 — Carry the separate early-pickup decision into the static gates

The Design at line 52 makes early static pickup a separate sequencing decision. Plan lines 17 and 26 list no predecessor for D1 and specify static independence from the viewer runtime, but they omit that sequencing disposition. Carry the Design condition into the D1 gate or common pickup rules. Record any proposed early sequence and its authorization at pickup. Static qualification remains independent of the viewer package, and #264 remains outside M6 completion accounting.

### R1-F004 — Reconcile refresh selection and authorization with the accepted Design

Plan line 99 clears both stale data and selection whenever authorization or visibility changes. Design lines 39 and 44 require previous data to be withheld when it loses authorization and selection to persist if the story remains visible and admitted on the new snapshot. Specify the transition explicitly. Do not show old details while eligibility is unresolved, then retain the selected ID only when the newly admitted snapshot still contains it, or clear it when it does not. Add cases for a visibility transition that still admits the selected story and one that removes it. D8 lines 105–106 should verify that hosted fallback only retains a release that remains authorized for the active audience, including a failed or superseded refresh after an audience change. This applies the existing scope rule to the hosted path.

### R1-F005 — Use an executable dashboard test command and declare its prerequisites

D1–D3 lines 49, 58 and 67 use bare `python -m pytest` for the dashboard. The dashboard source documents Python 3.13+ and its current tests use standard-library `unittest`. The current CI pytest environment is provisioned for the separate `aitm-usage` package, so it does not establish a dashboard pytest dependency. Specify the supported Python executable and the dashboard's existing discovery commands for focused and full-suite checks, or name the approved test environment and dependency if pytest is intended. Give D4 a concrete aggregate command and state where the historical planning objects and Graphviz must be available so clean qualification can distinguish missing prerequisites from a failed replay.

## Scope check

The proposed slice graph is acyclic. Each preliminary estimate is at or below four agent-hours, with renewed estimates and splitting at JIT. The story is in Backlog with no parent or dependency edge to #247. The planning records still give #247 its 13 accepted children and #260 its existing #258/#257/#259 predecessors. The local viewer remains gated on the released Core contract and #250/#251. Hosted qualification is conditional on the follow-on's authorized route and applicable #258 and M2 contracts. These checks concern the planning records and gates. Released compatibility, live route eligibility and execution of the fixtures are pickup or delivery evidence.
