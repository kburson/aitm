<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-169bafd263ca90e387e30c8733773e80"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md"
artifact_commit: "2e9b8972e3210ade69ca77ca23db1dd64d3e6f45"
artifact_blob: "4a45658eb6427fddfb041f621ea4a9623d0a509e"
artifact_digest: "sha256:55eb9f5a6edf6e0d8a63d9bce64979a1d397d5defc7608395511ae13127930c8"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:b8abc3f5780ff388a9c4be71d3699780de9374625a3555d8e60b340df430ea14"
  identity_source: "runtime"
started_at: "2026-11-09T16:29:24.792Z"
submitted_at: "2026-11-09T16:35:16.687Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 2 of the independent XPR review of `.aitm/stories/000/83/plan/usage-capture-relationship-replan.md` at sealed digest `sha256:55eb9f5a6edf6e0d8a63d9bce64979a1d397d5defc7608395511ae13127930c8` (commit `2e9b897`, blob `4a45658`).

**Read evidence.** I read the current artifact fresh with the Read tool in two contiguous chunks of at most 20 lines: lines 1–20, then 21–26. The second chunk reached EOF at line 26. Neither chunk was truncated or replaced by an omission marker. I read the author's turn-1 response (`author-response-1.md`, lines 1–54, EOF) and checked each disposition against the revised text rather than the author's summary. My turn-1 response, with F1, F2 and O1–O4, is the basis for that check.

Only the join and submit commands were available to me, so I did not run Git or recompute digests. The product source is not in this worktree.

**Unchanged and still sound.** Lines 1–13 are unchanged apart from item 1's new module reference, as are lines 23–25 and the regression intro. That includes:

- the candidate `544844a…` and integration base `67e888d…`;
- the prior-amendment pin `7df41b26…`;
- the 45-minute forecast within U13's three-hour cap, the 48.5-hour, thirteen-leaf aggregate, the four-hour leaf cap and the stop rule;
- the hold on other leaves;
- Epic #2 left unstarted, Core C01 blocked on qualified #83 activation, and the lifetime design.

The added proofs plausibly still fit the 45-minute forecast, given the observed nine-minute interval. Line 9's stop rule covers it if they do not.

**Disposition verification.**

- **F1: resolved.** Line 15 now names the U13-owned module `relationships.py` as the single static validator.
  - It depends only on typed records and the fixed read-only view, and does not import `ledger.py`. That removes the cycle and the inverted layering.
  - The bound ledger supplies project reference derivation internally, so callers cannot supply it.
  - The ledger and the dispatcher call the validator directly. Callers "cannot inject a validator or select another path".
  - The "verified equivalent" alternative is gone.
  - The validator owns graph validity, the alias and parent values and canonical child normalization. The ledger change remains a narrow admission check, and line 13 still bounds `ledger.py` to two checks.
- **F2: resolved.** Line 16 now states the drain rule I asked for:
  - relationship commands are processed strictly in publication order;
  - the drain stops at the first command that fails to reach a committed disposition, and that command and all later relationship commands stay queued;
  - a missing, malformed, duplicate or unclassifiable order halts the relationship drain with a sanitized diagnostic and never reorders;
  - independent non-relationship commands continue.

  Line 21 adds the two required regressions. A transient failure on the first of two dependent commands must leave the second without a final disposition. Duplicate and malformed order must lead to no later consumption. The line 7 failure, where a valid graduation is permanently rejected after an earlier failure, is now excluded by the text and covered by a test.
- **O1: adopted.** Line 15 validates "every new final relationship disposition", so rejections are included. Line 20 adds "a forged final rejection of a valid proposal".
- **O2: adopted.** Line 16 limits a reset of the queue-local order to the moment no relationship files remain outstanding, and counts committed items awaiting acknowledgment or retirement as outstanding. Line 21 interleaves a publisher with a captured snapshot and with partial and full retirement, and kills the process between commit and retirement. This matches the four cases I traced in turn 1.
- **O3: adopted.** Line 16 says all non-relationship commands, including the later U08 anchor command, keep their existing shape without a relationship order. U08 needs no edit to the ordering path.
- **O4: deferred to pickup, acceptable.** The author commits the #86 repair plan and JIT to retaining the exact source-finding evidence and the pinned accepted amendment, with the disposable probes held separately. Line 25 already requires the exact accepted amendment to be pinned. This is a pickup record, not amendment content.

**Lineage observation, carried from turn 1 and not a finding.** The SAR record still binds the earlier digest `2e2d9eea…`. Line 3 and the resume gate require SAR, SPR and XPR acceptance of the exact accepted bytes. The author must close that gate on the final digest before resuming, and the #86 repair plan and JIT must pin the final digest.

## Findings

None. No required findings remain.

## Required changes

None.

## Optional suggestions

1. **O5 (view type without importing the ledger).** If `LedgerView` is defined in `ledger.py`, `relationships.py` can still annotate against it. It can use a typing-only import or a read-only Protocol in `types.py`, which keeps the "does not import `ledger.py`" rule true at runtime. A one-line note in the #86 repair plan would prevent a mistaken runtime import.
2. **O6 (recovery from a halted relationship queue).** A malformed or duplicate-order entry now halts the relationship drain, which is correct fail-closed behaviour. The #86 repair plan should name the operator-visible state, for example in the sanitized diagnostic or later U08 status. It should also name the supported recovery, so that a halted queue is never cleared by deleting inbox files by hand. This can stay at the pickup level.

## Decision

accepted
