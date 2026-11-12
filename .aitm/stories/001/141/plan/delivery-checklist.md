# #141 delivery checklist · Attempt 1

Implementer Codex / story141. The Wave 30 coordinator owns remote
publication, GitHub state, delivery verification and closure. This
checklist is a local candidate handoff for the coordinator.

- [x] Accepted [design](../design/derive-python-package-edges-design.md),
  [refinement](2026-11-11-141-refinement.md),
  [plan](2026-11-11-141-python-package-edges.md) and
  [JIT](2026-11-11-141-jit.md). Exact Plan/JIT acceptance published
  `201d21a0deca8b4a03d39a4ba8b8ba383deee4cd`.
- [x] #139 and #140 Closed as completed and Project Done, with delivered
  commits in the pinned base. Develop checkpoint
  `67e9049aa4c5773720c83d65faaad3e985122e3a`.
- [x] Story branch `codex/aitm-wave30-141`, target `trunk`, base
  `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, base tree
  `b4a757f106b89086a24d0e909bc259d7b5b93c88`.
- [x] Clean head `be8f5bff9311655fb788e597c69069c23609a341`, tree
  `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`. Preflight replaced
  `39d2ef5166db04a1ae9fa3cf24d504b591a7fa18` before Test.
  Behavior red/green, focused collection, 104 related passes, Ruff
  and whitespace checks recorded. Additional local product/CLI/helper diagnostics retained
  with the exact-trunk comparison. [Local validation](2026-11-11-141-local-validation.md)
- [ ] Coordinator pushes the story branch and opens the ordinary PR
  into `trunk`. Record PR, exact remote head/base, tested merge SHA
  with ordered parents and tree, and Project Test.
- [ ] Verify required #103 jobs `python-base`, `python`, `quality`,
  `file-checks`, `collect-evidence`, and `aitm-ci` for the exact
  current candidate and applicable base. Record run, attempt, jobs,
  receipts and observed outcomes. Verify full product/CLI and helper
  scopes, coverage, installed wheel, native child evidence and
  authenticated identity under the applicable workflow.
- [ ] Obtain the gate-defining owner disposition for the exact tested
  tree and a separate independent source review on that same passing
  source and evidence. Record Project Review at the applicable gate,
  any findings, exact verdict and native/off-platform review evidence.
- [ ] Before merge reread live base/head, required jobs, branch
  protection, exact owner and review disposition. Run the trusted
  verifier from current trunk with the exact disposed `--reviewed-tree`.
- [ ] Verify ordinary merge or source-to-target mapping in remote
  `trunk`. Record the delivered commit/tree and observed time.
- [ ] Obtain dated implementer retrospective/sign-off with measured
  or Unknown effort. Publish and link sanitized evidence. Release only
  story-owned resources after evidence retention.
- [ ] Record the last required gate and its time. Verify issue
  Closed as completed and Project Done, record the closure timestamp
  and dependency effects in planning.

Preserve distinct failed, pending and superseded attempts. Changed
head, base or validation inputs require applicable fresh proof.
[Manual delivery checklist](../../../../manual-delivery-checklist.md) · [#103 CI contract](../../103/design/github-ci-quality-gates-design.md)

## Current exact-candidate Test readback

- GitHub Project Test, Rank 30. [PR #262](https://github.com/kburson/aitm/pull/262) targets `trunk` at `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` from exact head `be8f5bff9311655fb788e597c69069c23609a341`.
- GitHub's tested merge is `95f6ebe25c6cca5c67efdc509a617842b729f276` with ordered parents base then head. The tested tree is `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`.
- [CI run 43140853744 attempt 1](https://github.com/kburson/aitm/actions/runs/43140853744/attempts/1) finished with `success`. [Authenticated metadata](hosted-readback-be8f5bff9311.json).
- All six required jobs and the signed subject's custody were independently authenticated for this exact attempt. [Signature readback](hosted-signature-be8f5bff9311.json).
- [Independent source assessment](reviews/2026-11-11-141-source-assessment-r1.md) informs the owner disposition.
- [Independent source assessment](reviews/2026-11-11-141-source-assessment-r2.md) informs the owner disposition.
- Trusted #103 verifier held with `gate controls changed or disposition is stale; provide the exact reviewed tree`. [Verifier receipt](verifier-hold-be8f5bff9311.json).
- The owner decision must bind the exact tested tree and the two gate-defining additions. The authenticated CI diagnostic and source assessment leave the full trusted verifier and formal independent source review pending. The Project stays in Test.

## Formal independent PR review

[Off-platform SAR](reviews/141-formal-sar-r1.md) records **changes-requested** on head `be8f5bff9311655fb788e597c69069c23609a341`, tested tree `ed4ea486732346bfaaf7d518bc91b4d13b555fd5`, after the exact trusted verifier passed.

## Formal independent PR review

[Off-platform SAR](reviews/141-formal-sar-r2.md) records **accepted** on head `8a4d9d5ee81a98596b893c03f43b383fa3acab22`, tested tree `f2c045b29ed4c8f99ba8056de459d17ff340f4d3`, after the exact trusted verifier passed.
