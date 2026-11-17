# #368 hosted image re-admission

The [reviewed restore retry](2026-11-16-368-hosted-restore-retry-packet.md) reached a fresh
[Stage B job](https://github.com/kburson/aitm/actions/runs/44024727968/attempts/1).
The job reported image `20261112.0504.1` while its admitted runtime was tied to `20261102.0473.1`.
The rejected job's full `identity` matches every new `image_identity` key. The job correctly produced a `job-identity` HOLD before
runtime loading and ran zero product tests. Its [authenticated receipt archive](https://github.com/kburson/aitm/actions/runs/44024727968/artifacts/14302935823) is retained.

The original Stage A workflow and all probe source blobs ran again unchanged on a fresh job, with identical Git tree
`672758a41be247be759c5671d3dc09173d94fc65`. The [re-admission run](https://github.com/kburson/aitm/actions/runs/44024930299/attempts/1)
passed under image `20261112.0504.1`, with macOS 26.7.2 build `25G332`, ARM64 and SIP disabled (stock runner setting, unchanged).
The trusted side matched the authenticated [artifact 14302787413](https://github.com/kburson/aitm/actions/runs/44024930299/artifacts/14302787413),
validated every export hash, and independently reparsed the protected positive and negative worker controls, the process lifecycle and USDT.
The new runtime was built in the admitted job and its manifest, probe table and interpreter readbacks are bound below.

| Field | Exact value |
| --- | --- |
| archive sha256 | `3841df4cfeca31523065b63d6b66ba72aec58aad4041e91854225d36564936ca` |
| artifact | `14302787413` |
| attempt | `1` |
| head | `e38d67d0254c0bac77761a48561c7ee5ecad315e` |
| manifest sha256 | `1a5e9f5df23ffba83417532c4d67e9f51bb72f78570c7078027712fa238f11fd` |
| probe table sha256 | `6f92128660113f8fc0396fc0e02abb0a2ba9e26598f3aef28f063f2b11707b06` |
| python sha256 | `a6d5935b3937d7f11b10059b9ce6cd2a03b3919e17c6ffda0326afd06491f734` |
| receipt sha256 | `a363e0a3f15683ce2c0c57302c528e80781e1ef30916c67a13b0c54bb1da2b4e` |
| run | `44024930299` |
| runtime archive sha256 | `402dda5423f9a0f97cf3b7c3ca25228503a101d552c4772b68ee5d0bc3d441dd` |

The ordinary-account dry restore extracted and copied the new archive under the reviewed installer and compared the
complete runtime manifest and Mach-O probe table before stopping without interpreter execution. The manifest scan found
8,973 entries, with 8,570 files, 393 directories, and ten symlinks. Zero regular files lack other-read access and zero
directories lack other-read or traverse access. [Refreshed-image dry restore receipt](../attachments/2026-11-16-368-refreshed-image-dry-restore.json)
at SHA-256 `329e3e18dae985b4bd844424392ce18736fa741a009ab23ea4c847860681c3bb`. Eleven offline harness tests passed at `ffe77e3e2d8f5eac625add23b37c30f40025b4ec`.
The stage independently recomputed the same Mach-O `__dof_python` table digest from the fresh build. The complete
interpreter digest changed even though the section output was identical.

## Exact integrated authority

Workflow head `ffe77e3e2d8f5eac625add23b37c30f40025b4ec` and tree `65dccbb1fbe2b70fa248b8e175570c1d2bc3a401`. Compared with the accepted restore retry head `3a0859d163681562b0aeb96c3330846224bb8cc6`,
the only different blob is `.github/spikes/368/stage-b-inputs.json`, blob `732535f0f6da39b4f644ff8f2f34ffd3144af004` at SHA-256 `f9b00f7cd31db3e8ecae89350b2b71f6e0d9b12f564823fe3e5e48017327a96d`.
Only its authenticated admission keys and `image_identity.image` changed. Every other bound identity key, including the native keygen digest, matches the previous admission. The exact scope, 30 ordered IDs, 148-file product manifest,
native policy, launcher, instrumentation, restore correction, controls and workflow are unchanged.
Read the exact delta in the held worktree using `git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff 3a0859d163681562b0aeb96c3330846224bb8cc6 ffe77e3e2d8f5eac625add23b37c30f40025b4ec -- .github/spikes/368/stage-b-inputs.json`.

The conservative cumulative charge is 1.708 agent-hours before this review.
A newly assigned job must match this admitted image and authenticate this specific runtime before any calibration or product test.
Any additional drift, including a return to the earlier image during rollout, produces a new admission HOLD before product execution. #355 remains blocked.
