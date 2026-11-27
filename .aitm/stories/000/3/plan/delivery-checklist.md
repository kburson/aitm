# #3 Delivery checklist

Attempt 1. Implementer and closure owner are this Codex delivery agent. [Accepted pickup](2026-11-27-pickup.md) · [Grok 4.7 pickup review](2026-11-27-pickup-review.md) · [#83 activation receipt](../../83/attachments/activation-receipt.json).

- [x] Opened [draft PR #526](https://github.com/kburson/aitm/pull/526) from `codex/core-3-foundation` to `codex/core-470-integration`.
- [x] Verified base `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67`, head `c71dcc263505bb7b9f3ca19c3750ad1c3f15c2e2` and clean source tree `1955953ea2569f3a97bb288f90ae17b59cd1ac70`.
- [x] Ran locked local package tests and Ruff under Python 3.13.9 and uv 0.10.6. Four Core tests passed, including the installed wheel and unit isolation probes. The pre-implementation run failed on the missing package and test isolation files.
- [ ] Verify hosted Core CI for the exact candidate. The existing CI workflow exercises the usage package and tooling. The accepted pickup holds draft removal for a hosted run that exercises Core on the exact base and head.
- [ ] Remove the draft state after passing hosted evidence. Obtain Grok 4.7 source SAR against the passing candidate.
- [ ] Verify merge to the integration branch, publish delivery mapping, sign-off and Agent Cost, and close the issue and Project item.

## Hosted run readback

[GitHub Actions run 45953064630](https://github.com/kburson/aitm/actions/runs/45953064630) passed all six jobs on the recorded PR head and base. Its synthetic merge `6ab626c83f3fed6f30ad00ba36d4f7e608b04f9b` has the same tree as the story head. The Python jobs cover the usage package and tooling. The suite has no Core run. The corresponding local full usage suite reported 1,779 passed and one skipped.

The trusted verifier held on a changed gate-control input. The root workspace `pyproject.toml` is part of C01 and is classified as CI configuration. Re-run the verifier after an independent source verdict on the same exact tree and a recorded coordinator disposition. This is separate from hosted Core coverage.

PR #526 remains draft and #3 remains in Test. The accepted pickup requires applicable hosted proof before draft removal and the Grok 4.7 source SAR. A separate Core validation prerequisite or a change to the reviewed test basis requires a scope decision.

## Separate hosted Core prerequisite

The owner authorized [#527](https://github.com/kburson/aitm/issues/527). Its reviewed workflow landed through [PR #528](https://github.com/kburson/aitm/pull/528) in `34fd11588a1fecf3d04f16a311f1be9bd2f33c3b`. The story branch merged that integration base in `9b34623e`. The package and workspace changes are identical to the previous revision. Fresh repository CI and the new Core Python job are required for this updated candidate.
