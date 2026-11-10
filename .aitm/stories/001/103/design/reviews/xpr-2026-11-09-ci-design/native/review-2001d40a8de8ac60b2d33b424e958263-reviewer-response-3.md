<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-2001d40a8de8ac60b2d33b424e958263"
role: "reviewer"
turn: 3
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/103/design/github-ci-quality-gates-design.md"
artifact_commit: "144133b12dfb0fe62644c8359550c92abd4333c2"
artifact_blob: "47890eb1d11573112ec1bd7e5b3400ba9363c27d"
artifact_digest: "sha256:d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:3bae1567c47b4a0eb7bcaa003c3fee94a2ce29d930504d00aa989d4aa5887226"
  identity_source: "runtime"
started_at: "2026-11-10T02:45:49.379Z"
submitted_at: "2026-11-10T02:53:23.793Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Read coverage: I freshly read the current `.aitm/stories/001/103/design/github-ci-quality-gates-design.md` (artifact blob `47890eb1…`) in contiguous Read ranges of at most 20 lines: lines 1–20, 21–40 and 41–55. The third read asked for 41–60 and returned only through line 55, which is EOF. No range was marked truncated, and the read is complete through EOF. I also freshly read the preceding author dispositions in `review-2001d40a8de8ac60b2d33b424e958263-author-response-2.md`, lines 1–52 (EOF, complete). I did not edit the artifact or run Git.

Both round-2 findings are resolved in the current text:

- **R2-F1 (live base source and trusted identity), resolved at lines 19 and 51.** The verifier reads the declared target's live branch ref directly. It requires the live tip, the event base and the raw test-merge first parent to agree, and the live head to agree with the event head and the second parent. It binds the tested commit through GitHub metadata and its raw commit object. The candidate record is limited to lane outputs (inventory, coverage counts, digests) and "cannot supply trusted identity". Any mismatch, or missing fork linkage, holds the gate. Leaf 3 now explicitly exercises "stale live base without a fresh PR event", "absent fork identity" and "invalid merge parents".
- **R2-F2 (acceptance mapped to leaves), resolved at lines 21 and 47–54.** The acceptance section is now an ordered delivery plan:
  1. a conditional coverage prerequisite with its own reviewed route;
  2. workflow bootstrap, using the manual evidence procedure and closing on its own evidence;
  3. the verifier, using the proven route with manual readback until it is delivered, and owning the identity, partial-rerun and gate-change refusal fixtures;
  4. file quality and the future TypeScript contract.

  Each leaf has its own refusal demonstrations and its own closure gate. Leaves delivered before the verifier use the documented manual procedure. The comparison between the manual and trusted verifiers is assigned to the parent on a named exact candidate. The four-agent-hour limit per leaf is restated.

The round-2 optional suggestions were also taken up. The wheel-smoke environment now explicitly excludes the editable project (line 33). Runner label, image, Xcode/CLT version and projected hosted minutes are carried into refinement and pickup evidence (line 54).

Re-checking the full current text against the review focus, I found no new blocking issue:

- **Gate integrity** (lines 15, 17, 21): fail-closed aggregate, gate-defining blob IDs, owner disposition, fixed floor.
- **CI bootstrap** (lines 21, 27, 49–50).
- **Exact candidate binding** (lines 19, 23).
- **Hosted macOS versus Linux** (lines 9, 44, 54).
- **90% per product package** (lines 42–43: policy file, integer arithmetic, 89.5/90 demonstrations, named subprocess sources).
- **Behavioral tests** (lines 43, 49, 51).
- **Full inventory under parallelization** (lines 44–45: candidate completeness plus comparison with the trusted base inventory, missing and duplicate shard detection, coverage merged from the same candidate).
- **Standalone scope and protection of unrelated work** (lines 11, 36, 38: Core exclusions, exact fixture exemptions, baseline-first linting, separately scoped cleanup).

## Findings

None.

## Required changes

None.

## Optional suggestions

1. The live-tip equality rule (line 19) is correct for exact-candidate evidence, but on an active target every intervening push re-opens the gate and needs a branch update or reopen. When the separately authorized ruleset action is decided (line 27), consider a merge queue or strict up-to-date branches so this churn is absorbed mechanically. Record the expected re-run cost in refinement.
2. Leaf 2 (line 50) introduces `tools/ci/policy.json` and the workflow, but its refusal list no longer has the round-1 "malformed configuration" case; leaf 4's file-quality failures cover only maintained docs and data. Consider adding to leaf 2 a refusal for a malformed or missing `policy.json`, or a policy that declares an unknown package, so the gate's own control file fails closed from the first delivery.
3. In leaf 1 (line 49), name what evidence the conditional coverage prerequisite closes on before CI exists, for example a recorded local run of the exact candidate with integer counts. That makes "explicitly reviewed bootstrap test route" checkable at pickup.

## Decision

accepted
