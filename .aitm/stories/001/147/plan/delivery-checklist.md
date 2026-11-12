# #147 Wave 30 delivery checklist

**Attempt 1** · **Implementer** Codex / story147 · **Closure owner** Wave 30 coordinator Codex / root.

- Repository `kburson/aitm`, story branch `codex/aitm-wave30-147`, literal target `trunk`, pinned base `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, tree `b4a757f106b89086a24d0e909bc259d7b5b93c88`.
- Exact independent Design, Plan and JIT acceptance recorded before Develop. Native #139 and #140 are Closed as completed, Project Done, and delivered to the pinned baseline. [Accepted Design](../design/2026-11-11-147-bind-gate-changes-design.md) · [Plan](2026-11-11-147-bind-gate-changes.md) · [JIT](2026-11-11-147-jit.md)
- Accepted JIT SHA-256 `f70f836effa5e66c30acc0be0f53ca38a19501a62511055748f47d7b389300c2`, publication `4a56ad67541ae17d9b90fd05d633124711ed210a`. Live Dev and attempt 1 checkpoint `da9f2bf8c6716390903c566de8e192e2e3ef1755`.
- The qualified route is the current #103 workflow ID `412848571` and manual gate. [Baseline push 43138335027 attempt 1](https://github.com/kburson/aitm/actions/runs/43138335027/attempts/1) succeeded on `71aa5c8` for the four applicable jobs. It supplies baseline evidence. The #147 local proof and future #147 hosted proof apply to their exact candidates.

- Local commit `a9f97f937369192b6f565f6d5cec1e26340358ab`, tree `b3aef9e5f6b75aa987f443bc6133d5a243147011`, clean at the pinned parent. Focused 41 passed, combined 217 passed, Ruff and whitespace checks passed. [Exact local proof](local-validation.md)

## Develop → Test

- [ ] Coordinator verifies the local candidate identity and two-file scope, then pushes the exact branch and opens its PR into `trunk`. Record the PR's exact base, head, and tree and read back Test on the Project.
- [ ] Obtain the existing owner disposition for the exact hosted tested tree. Both new paths are #103 gate-defining under `tools/ci/`. Reconcile base and head with the ordered test-merge parents and record the tested commit/tree and canonical run and attempt.

## Test → Review

- [ ] Verify `python-base`, `python`, `quality`, `file-checks`, `collect-evidence` and `aitm-ci` for the exact candidate and current base. From protected trunk outside candidate execution, run the trusted verifier with the independently obtained exact owner-disposed `--reviewed-tree` value. Retain attempt identities, required job evidence, coverage and outcome checks. The local focused tests remain separate from #103's existing four-helper scope.
- [ ] After exact hosted evidence passes, obtain separate independent source review of the same head and tree. Link the verdict and its provenance on the PR and record Review. Preserve failures, stale runs and superseded candidates with their own attempts.

## Review → Done

- [ ] Reread exact PR eligibility, approved identity, latest run and effective protection. Merge through the existing authorized route. Independently verify delivery on remote `trunk`, including source-to-target tree mapping, ancestry, merge identity and observed time.
- [ ] Keep the implementing agent available for the signed post-delivery retrospective. Publish that and the verified delivery record, then close the issue and move the Project item to Done under coordinator ownership. Read back each state and preserve the closure record.

[Manual delivery checklist](../../../../manual-delivery-checklist.md) · [#103 gate contract](../../103/design/github-ci-quality-gates-design.md)

## Current exact-candidate Test readback

- GitHub Project Test, Rank 30. [PR #261](https://github.com/kburson/aitm/pull/261) targets `trunk` at `71aa5c880fc6a1db1cf676dfc663373f02ef7b16` from exact head `0d8f8ea353d71ab19802e882ceecbd105e6837ae`.
- GitHub's tested merge is `348932349a6d19f8d4aaf150eb683b4c9311418f` with ordered parents base then head. The tested tree is `9699130f9be8411cb2a5646197e803956b1ef1b3`.
- [CI run 43142104151 attempt 1](https://github.com/kburson/aitm/actions/runs/43142104151/attempts/1) finished with `success`. [Authenticated metadata](hosted-readback-0d8f8ea353d7.json).
- All six required jobs and the signed subject's custody were independently authenticated for this exact attempt. [Signature readback](hosted-signature-0d8f8ea353d7.json).
- [Independent source assessment](reviews/2026-11-11-147-source-owner-assessment-r2.md) informs the owner disposition.
- Trusted #103 verifier held with `gate controls changed or disposition is stale; provide the exact reviewed tree`. [Verifier receipt](verifier-hold-0d8f8ea353d7.json).
- The owner decision must bind the exact tested tree and the two gate-defining additions. The authenticated CI diagnostic and source assessment leave the full trusted verifier and formal independent source review pending. The Project stays in Test.

## Formal independent PR review

[Off-platform SAR](reviews/147-formal-sar-r1.md) records **changes-requested** on head `0d8f8ea353d71ab19802e882ceecbd105e6837ae`, tested tree `9699130f9be8411cb2a5646197e803956b1ef1b3`, after the exact trusted verifier passed.

## Formal independent PR review

[Off-platform SAR](reviews/147-formal-sar-r2.md) records **accepted** on head `26e8ba1aa41eb8eb1c26d963a189c5cc43771a85`, tested tree `cab945d1c8bdd14bab3b1f7aa06fde7b023f9357`, after the exact trusted verifier passed.
