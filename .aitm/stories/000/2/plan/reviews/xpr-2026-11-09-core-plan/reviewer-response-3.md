---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 3
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0"
artifact_digest: "sha256:327af4d64a202e06183491be50b620786681df8dd73f6a0d0265a262f8c7f5be"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T07:46:23.013Z"
submitted_at: "2026-11-09T07:47:55.873Z"
start_basis: "prior-submit"
start_source: "author-response-2.md"
finding_ids: ["R3-F001", "R3-F002"]
answered_finding_ids: []
native_source: "native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-3.md"
native_source_digest: "sha256:bd9d8d20bfda376376c9a6be004785989c58698827689b6265ab774418cf7034"
---

Mode: `normal`

## Summary

Round 3 reviews the current `core-implementation-plan.md` (digest `sha256:327af4d6…f5be`, 69 leaves / 217.5 h), checked against the round-2 dispositions.

The decomposition table, estimates and Depends on rows are unchanged from round 2. My earlier sum/topology/overlap checks still hold: 217.5 h, every leaf within 2.5–4 h, every row's dependencies earlier in the table, and every shared touched path ordered.

Round-2 dispositions:

- R2-F001 is resolved. Line 60 now states one global rule: negative vectors use an explicit test composition with the slot deliberately unregistered, and wiring leaves prove production registration in their own test files. The rule is applied in:
  - C04, C06, C11, C12, C17 and C28 (negative vectors);
  - C10, C12, C14, C31, C35 and C43 (positive production-resolution proofs);
  - C01 (the catalog's missing-module vectors).

  C46's pre-declaration "unavailable output hashes" remains true after C48, because it is conditioned on the absence of a declaration rather than on missing wiring. No predecessor test file has to be edited later.
- R2-F002 is resolved semantically. `attempt reconcile` and `expand` are category `normal`, always require preflight and never borrow stop or recovery categories. C27 and C30 inject the declared fixture in test-only composition, and C31 repeats their vectors with the real preflight.
- R2-F003 is resolved. C01 owns `tests/conftest.py`, all `__init__.py` markers and `--import-mode=importlib` in its existing `pyproject.toml` allowlist, with qualified `tests.support.*` imports. C64 consumes them, and C59 copies the skeleton.
- R2-F004 is resolved. `test_default_publication_pending` is separate and uses a remote; the local-only walk asserts N/A. A scenario-map row was added.

One residual defect: the R2-F002 fix moved a large proof burden into C31 without re-estimating or splitting it. This is the same class of defect as R1-F007, which was accepted.

## Findings

### R3-F001 — C31 now carries three predecessor leaves' integration re-proofs on top of its own scope, with its 3.5 h estimate unchanged

Evidence:

- C31's original scope (line 744), unchanged:
  - trip precedence for confirmed overrun and second/nested expansion, including atomic fencing of origin and child plus enforce-mode demotion;
  - rework vs accepted-replacement budget rules;
  - continue/fold/abandon coherence;
  - `pivot` with the `--as-human` refusal;
  - `decide_trip`;
  - wiring AttemptPreflight at three call sites (CommandService before sync/mutation, backend retry before every CAS, before effective completion);
  - the stop/reconciliation category;
  - preserving unsynced workspace bytes after a trip.

  It touches 8 files.
- Round 1 added a re-run of C28's real pipeline-order, provisional-attempt and reconcile cases.
- Round 2 added, all "with the actual installed implementation" in `test_c31.py`:
  - C27 reconcile positive and refusal behavior;
  - C30 local *and shared* expand construction-failure, **competing-clone** and **lost-ACK** vectors;
  - second/nested expansion and CAS-retry stops.

  The author response states "No decomposition, estimate or dependency change was necessary" (author response 2, Changes made). C31 remains 3.5 h (line 167/736).
- The shared-store competing-clone and lost-ACK expand vectors need two-clone/remote construction with deterministic barriers. The plan builds that infrastructure as a separate 2.5 h leaf (C64), which depends on C43 and therefore comes after C31. So C31 must either rebuild an ad hoc two-clone harness or import C30's private test helpers. The plan explicitly disallows the first ("no duplicate harness", C64/C68 boundaries).
- The plan's own rule (line 41): if the proof burden makes four hours implausible, split before Develop. Changing leaf scope later invalidates the accepted decomposition. The R1-F007 resolution applied exactly this reasoning to C49/C50/C60.

Failure scenario: the C31 attempt either trips the four-hour clock, consumes its one expansion as planned overflow (forbidden by line 41), or silently drops the shared-store expand re-proof. In the last case, the real-preflight behavior of `expand` under competing clones and lost ACK, the path most exposed to trip/expansion ordering bugs (review focus item 4), is never proved with the production preflight before Gate B.

## Required changes

1. R3-F001: Re-scope C31 to its own trip/pivot/decision work, the three AttemptPreflight wiring points, a production-resolution proof, and one representative real pipeline-order case (the C28 promote path with a qualifying stop). Move the remaining post-installation consumer re-proofs to a leaf that runs after C31 and can reuse C64's two-clone fixtures, with explicit Depends on edges and a re-estimate. The re-proofs to move:
   - C27 reconcile positive/refusal;
   - the C28 provisional-attempt/reconcile cases;
   - C30 local/shared construction-failure, competing-clone and lost-ACK expand vectors.

   For example, add a new leaf such as "C70: Post-preflight consumer re-proof" depending on C31 and C64, or extend C65 with a corresponding estimate change if it stays ≤4 h. Update the table, total estimate and leaf count, scenario map and Gate B wording accordingly. If C31 keeps any of these vectors, state a credible estimate split for them instead of the unchanged 3.5 h.

## Optional suggestions

### R3-F002 — Make the copied harness's pytest import mode explicit in C59's runner

C01 sets `--import-mode=importlib` in `packages/aitm-core/pyproject.toml`. C59 copies the `tests` skeleton, but not that `pyproject.toml`, into the isolated harness and says "preserve C01 importlib mode". Without the ini file, pytest in the copied location falls back to its default `prepend` mode, and to default marker/collection settings. That would include the marker C69 relies on to exclude live `test_published_release` from ordinary collection. Consider having `run_installed_suites` pass `--import-mode=importlib` and any required ini options explicitly (or copy a dedicated minimal pytest ini into the harness), and assert the effective import mode in `test_wheel.py`.

## Decision

revisions-requested
