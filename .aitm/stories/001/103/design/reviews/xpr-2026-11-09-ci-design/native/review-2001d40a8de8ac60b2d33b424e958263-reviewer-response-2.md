<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-2001d40a8de8ac60b2d33b424e958263"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/103/design/github-ci-quality-gates-design.md"
artifact_commit: "dc507c8017ed6fb01cb39c561cec77a6959fb206"
artifact_blob: "0fe509aa14e59d00553fe94170bdb30188b624a4"
artifact_digest: "sha256:96ef0fb0019e82c3ed43387c6e9efedc83bfeeae6a9094ac4de42980009d120b"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:3bae1567c47b4a0eb7bcaa003c3fee94a2ce29d930504d00aa989d4aa5887226"
  identity_source: "runtime"
started_at: "2026-11-10T02:45:49.379Z"
submitted_at: "2026-11-10T02:51:38.067Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Read coverage: I freshly read the current `.aitm/stories/001/103/design/github-ci-quality-gates-design.md` (artifact blob `0fe509aa…`) in contiguous Read ranges of at most 20 lines: lines 1–20, 21–40 and 41–53. The third read asked for 41–60 and returned only through line 53, which is EOF. No range was marked truncated, and the read is complete through EOF. I also freshly read the preceding author dispositions in `review-2001d40a8de8ac60b2d33b424e958263-author-response-1.md`, lines 1–58 (EOF, complete). I did not edit the artifact or run Git.

All eight round-1 findings are substantively resolved in the current text:

- **R1-F1 (gate self-modification), resolved at lines 17, 21 and 50.** The design adds trusted-target comparison of gate-defining paths, recorded blob IDs, owner disposition plus independent review, a fixed 90% floor, and "candidate output alone cannot approve" changes to its own controls.
- **R1-F2 (evidence verifier and run selection), resolved at line 19.** It names `tools/ci/verify_pr.py`, run from the trusted target and kept outside candidate execution. It states deterministic newest-run selection, says a newer failed or pending run holds the gate, and treats older runs as history instead of disqualifying "duplicates". It requires each job exactly once in the same attempt, rejecting partial reruns, with API fixtures and a 90% floor for the verifier.
- **R1-F3 (`edited` and cancellation), resolved at lines 23 and 25.** It drops `edited`, routes retargeting through an ordinary push or an authorized reopen, makes metadata edits start no run, and gives the concurrency keys.
- **R1-F4 (targets and bootstrap), resolved at lines 15 and 27.** It removes branch and path filters, blocks a declared target that lacks a result, updates a pre-existing integration parent and proves it, and rewords the bootstrap sentence correctly.
- **R1-F5 (inventory baseline), resolved at lines 44, 45 and 50.** It adds both in-run completeness and a comparison with the trusted base inventory, surfaces removed, deselected, newly skipped and newly xfailed IDs, and adds a refusal demonstration.
- **R1-F6 (coverage arithmetic and scope), resolved at lines 42, 43 and 50.** It specifies integer arithmetic, demonstrations at 89.5% and 90%, `tools/ci/policy.json`, and named subprocess sources with a hard-kill carve-out.
- **R1-F7 (wheel smoke), resolved at line 33.** It verifies the digest immediately before install, installs `--no-deps` into a locked environment, and checks the command and import resolution.
- **R1-F8 (file sets and existing work), resolved at lines 36 and 38.** It adds exact reviewed fixture exclusions, a baseline measured on the exact base, and separately scoped cleanup.

The proposed split into bounded leaves (line 52) also takes up round-1 optional suggestion 1.

Two new issues emerge from the revised text. Both concern exact candidate binding and testable closure, and both are small.

## Findings

1. **The source of the "live base" identity is not specified, and the candidate record must not supply trusted identities (exact candidate binding, lines 19, 21 and 23).** Line 23 says "a moved base … needs a fresh event and fresh applicable evidence." Line 19 has the verifier match the run against the "exact live … target, head and base" from "live PR … metadata", plus "the workflow's sanitized candidate record". Two gaps follow:
   - (a) The PR object's `base.sha` is not documented as the current tip of the target branch. GitHub can leave it at the value from the PR's last update. If the verifier compares the run's base with `pull.base.sha`, a target that has advanced since the last event can still look current, and a stale candidate passes. The verifier should read the target branch tip directly (`git/ref/heads/<target>`, or the trusted target checkout's HEAD when it is fetched fresh). It should require that tip to equal the run's event base and the merge commit's first parent.
   - (b) The design does not say which identities come from trusted GitHub metadata and which from the candidate-produced record. The workflow-run API's `pull_requests` array is empty for fork PRs. That tempts the verifier to fall back on the candidate record for head, base and tested commit, but the record is written by candidate-controlled code. State that repository, workflow, run, attempt, event, head and base come from authenticated API metadata, plus the verifier's own reading of the raw merge-commit parents. The candidate record supplies only lane outputs: coverage counts, inventory and digests. Any mismatch between the record's identities and the API identities blocks the gate. Add a refusal demonstration for "base advanced without a fresh event" to acceptance 2.

2. **The acceptance items are written for one delivery, but line 52 splits the work into four leaves (testable closure, lines 21, 27 and 49–52).** Acceptance 1 requires "the read-only verifier agrees with the manual bootstrap readback". Acceptance 2 requires refusing partial-rerun, ambiguous and different-workflow evidence, which only the verifier can show. Line 52 makes the verifier, file-quality checks, the coverage prerequisite, and workflow bootstrap and live proof separate leaves, each with its own closure target. Line 21 says the verifier comes "through separately reviewed delivery". As written, it is unclear:
   - which leaf owns which acceptance demonstration;
   - what order the leaves go in;
   - which leaf the line 27 bootstrap conditions belong to: a real passing result, 90% coverage, and trunk and integration-parent proof;
   - how leaves merged before the verifier exists are verified.

   Without that mapping, a leaf can close against acceptance items that belong to another leaf, or none can close. Add a short mapping from leaf to acceptance item, with the intended order. For example: coverage prerequisite (if needed), then workflow bootstrap and live proof (manual verification per line 21), then the verifier (its fixtures prove refusal cases, and it is compared with the manual readback), then file-quality checks. State that leaves merged before the verifier use the documented manual procedure.

## Required changes

1. In the verifier contract (line 19 and/or 23), take the live base from the target branch ref tip and require it to equal the run's event base and the raw merge-commit first parent. State that all candidate identities come from authenticated API metadata and the verifier's own commit-object read. Limit the candidate record to lane outputs, and make any identity mismatch block. Add an acceptance 2 refusal for a base that advanced without a fresh event (finding 1).
2. Add a mapping from leaf to acceptance item, with the delivery order, and state how leaves merged before the verifier exists are verified (finding 2).

## Optional suggestions

1. In the wheel-smoke row (line 33), name how the locked environment excludes the project itself, for example `uv sync --no-install-project` or `uv export --no-emit-project`. A default `uv sync` installs the project editable, which could shadow the wheel. The import-location check would catch this, but naming it prevents a confusing failure.
2. The candidate's tests run in the same job that writes coverage data and the candidate record. Under the stated threat model, that is acceptable: an owner and agents, fixture-only, read-only. Consider stating that assumption, so a later move to untrusted contributors prompts producing the coverage and inventory data in a separate step or job.
3. Round-1 suggestion 4 (pinned runner image and Xcode version per run, and a macOS minute budget) is deferred to refinement at author line 53. Carry it into the leaf plan so it is not lost.

## Decision

revisions-requested
