# #292 independent formal review of the shadow deployment

**Verdict: ACCEPTED for shadow deployment of this exact tree.** Signed by OpenAI Codex, independent review agent `/root/review148`. Hosted selected and fallback qualification remain open for #292. [PR #314](https://github.com/kburson/aitm/pull/314) · [#292](https://github.com/kburson/aitm/issues/292)

| Verified identity | Value |
| --- | --- |
| Repository and target | `kburson/aitm` (`1450406435`), protected `trunk` |
| Base | `1ae0c08c9fc2a4c884800c663ba42cc4a6bb37a2` |
| Candidate head | `3cb2ba833a81edf663d00e1898789a371358bf80` |
| Tested synthetic merge | `401a1e5bcf4c35025eadd59c60b49a0b63bf278f` |
| Candidate and tested tree | `acbbc009f9a2ea03969df2aedbe8b0645520f248` |
| Canonical #103 CI | [Run 43720329396, attempt 1](https://github.com/kburson/aitm/actions/runs/43720329396/attempts/1), suite `118368014927`, workflow `412848571` |
| Signed evidence artifact | `14164217793`, archive `sha256:21aa6754796500815082952b14bf6fc4d50b004cb68eff875057b78f6e955c4a`, subject `f5150f7dad6bba2affa9465e7edad48c471c1874ca0421f18c4feae3cee17d36` |
| [Trusted-verifier record](trusted-verifier.json) | SHA-256 `e4fb5be586ce6af115f8a6994c0bb7c19a548ebb3d1d3a82ea0f5b5dae2a2322` |
| [Exact tree disposition](tree-disposition.json) | SHA-256 `6f82bbbff5b2dde2222b907969e527321e732dad1dcbeec041366bfe2316fc15` |

GitHub confirms the synthetic merge has the exact base and candidate as its ordered parents. All six authenticated #103 jobs completed successfully. They are `quality` 132830799425, `file-checks` 132830799670, `python` 132830799537, `python-base` 132830799580, `collect-evidence` 132833785060 and `aitm-ci` 132833843789. I independently reran the delivered trusted verifier from a clean protected-base checkout using pinned GitHub CLI 2.97.0. That pass reproduced the reviewed tuple, job identities, signed artifact, subject digest and gate-control blobs. The three source additions leave the existing production controls unchanged. [#103](https://github.com/kburson/aitm/issues/103)

The original implementation authenticated Markdown bytes against a manifest that did not establish review identity. The replacement validates an OpenSSH detached signature over the exact admission JSON before parsing. It pins the independent reviewer key with fingerprint `SHA256:yx7w2D8hvFnca/QiBvmq5Z6EQPf0/AaGPAxikt0DLXU`, principal `aitm-fast-shadow-sar` and namespace `aitm-fast-story-admission`. The signed fields bind the exact PR/base/head/tested/tree tuple and the independently reviewed Markdown digest. The selected path also verifies the complete materialized Git path, file-mode and blob inventory before dependency setup or pytest. It rejects archive differences, including case aliases, and rechecks source and provider state after execution.

The workflow dispatch uses the protected default branch and a read-only token. Candidate Python processes receive an explicit environment instead of the controller's GitHub token. The selected class is regular additions or modifications of Markdown under `docs/` with unchanged executable inputs. Everything outside the class returns `full-required` and retains existing #103 authority. This evidence supports the bounded trust model for protected source. Operating-system isolation for arbitrary candidate code is outside scope.

I independently ran 46 focused tests from the exact candidate archive, including altered manifest, alternate signer, wrong-content and case-alias controls. Actionlint and Git whitespace checks passed. The independent exact candidate collection contains 1,825 ordered IDs, including 1,280 product and 545 helper IDs, with ordered digest `3bd40aba2a597b4db58dfad16ba5a16d2d38f8b23b828d20887fb6a624e9b37f`. The local selected control passed all seven mandatory tests and both native child witnesses. A genuine hosted admitted docs candidate, exact unsupported fallback, and independent hosted artifact review remain required for story closure. [Corrected local control](local-corrected.json) · [Shadow plan](2026-11-15-292-fast-story-shadow-plan.md)
