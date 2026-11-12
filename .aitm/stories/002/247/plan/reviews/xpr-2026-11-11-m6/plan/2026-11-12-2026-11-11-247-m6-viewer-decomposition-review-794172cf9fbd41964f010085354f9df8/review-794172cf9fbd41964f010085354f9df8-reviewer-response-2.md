<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-794172cf9fbd41964f010085354f9df8"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
artifact_commit: "aa9f8a486c4510fa7568d60bfd6405ac0d0dae2e"
artifact_blob: "08f197f3492bbb3f7c799dc3c0cad814b603b578"
artifact_digest: "sha256:4be08e201c73d239ab2147ecd861000e7e0f1812a81f31b66fb1bc0bef514fd6"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:a9ddb00c18bf95949c28df14c6e2ddb64131150db394d645b943157c0af3d18e"
  identity_source: "runtime"
started_at: "2026-11-12T00:44:08.587Z"
submitted_at: "2026-11-12T00:49:30.626Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the round 2 independent XPR plan review of `.aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md`. The revision is at commit `aa9f8a486c4510fa7568d60bfd6405ac0d0dae2e`, blob `08f197f3492bbb3f7c799dc3c0cad814b603b578`. The digest `sha256:4be08e201c73d239ab2147ecd861000e7e0f1812a81f31b66fb1bc0bef514fd6` comes from this response's protected frontmatter. The scope is Backlog decomposition only. Acceptance grants no pickup, Develop entry, early bootstrap sequencing authorization, hosting, Pages enablement or Core child work.

### Full-file read record

- **Tool and range.** One Read call returned lines 1–152 with no truncation. Line 152 (the "Aggregate review and evidence" paragraph) is the last content line.
- **Hashing.** Shell hashing was not available to this reviewer, because Bash is limited to the package submit command. The digest above was not independently computed.
- **Author response.** I also read `review-794172cf9fbd41964f010085354f9df8-author-response-1.md` in full, lines 1–50.

### R1-F001 closure verification

The round 1 closure criteria are met:

- **(a) Concrete inherited outputs.** V05 bullet 2 (line 82) names what V05 consumes from V02:
  - V02's versioned preview JSON schema;
  - the controlled reason-code and precedence table;
  - the pinned #139 before/after and synthetic fixtures, as compatibility inputs.

  This is consistent with what V01/V02 actually produce: V01's versioned allowlisted view (line 49) and V02's rendered JSON and fixture rebuild (lines 57–59).
- **(b) Contract relationship.** Line 82 states that the product view is a separate Core-backed contract. It has a deterministic mapping from the supported preview schema for shared values, coverage, reasons and evidence times. Unsupported versions and lossy mappings are rejected, and the mapped fixtures serve as regressions. The legacy reader and bundle stay off the production runtime path. V05 bullet 3 (line 83) still owns the single approved metric payload shared by the local viewer, the hosted build and the M2 readback comparison. That resolves the one-contract ambiguity for V11/V12 parity.
- **(c) Narrative consistency.**
  - Line 37 now says the preview chain V01 → V02 supplies V05, so V05 waits for both V02 and V04.
  - Line 9 now says both preview leaves follow M1 in the normal sequence, with pre-M1 pickup as an optional, separately authorized exception.
  - Line 37 also gives the reconciliation criterion I asked for: removing the preview dependency requires a reviewed scope change that shows how the compatibility evidence is retained.

  The narrative now matches the native V02 → V05 edge.

### Regression checks on the revision

- **Graph unchanged.** Table predecessors (lines 23–35) are identical to round 1. That gives 19 edges, consistent with the hydration receipt and the child `blocked-by`/`blocking` mirrors I verified in round 1. The graph is still acyclic.
- **Estimates unchanged.** The total is still 43.5 h, and every leaf is still ≤ 4 h.
- **Only the V08 gate text changed in the table (line 30).** It now names released Core C18 `discuss`, which matches core plan line 116. The harness alternative is now explicitly conditioned on separate qualification.
- **Optional suggestions taken up:**
  - Line 11 assigns framework selection and local refresh behavior to V03 JIT and retains the rationale for V13. That closes my optional suggestions 2 and 3.
  - V05 bullet 4 (line 84) adds a pre-declared split path, with dependency review, if the view contract and UI exceed four hours at JIT. That closes optional suggestion 5.
- **Declined suggestions.** The author kept the preview file locations and the shared workflow name as JIT decisions (optional suggestions 4 and 7). Both are acceptable: the paths are labelled candidate paths, and JIT owns file ownership (line 15).
- **No new inconsistency.**
  - The #230 hold (line 41) is unchanged.
  - The V12/V13 holds and the #228/#229 alternative are unchanged.
  - Path-overlap ordering is unchanged: V03 → V05 for `src/aitm_viewer/`, and V09 → V10 for the workflow.
  - The added V05 text introduces no new file path.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Wording on line 82.** It says "V02's versioned preview JSON schema". The schema is defined by V01's projection (line 49), and V02 publishes and validates it. "The V01/V02 versioned preview schema as published in the V02 bundle" would be more precise. This is wording only; the dependency is already transitive through V01 → V02.

## Decision

accepted
