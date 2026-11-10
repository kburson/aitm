---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 140
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "9308cffd586c003c5ce8112ab3c91d1088999db8"
artifact_base_blob: "fc752b3eeff4aa622960c46ab8f4a1be19be4392"
base_digest: "sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029"
final_digest: "sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248"
rounds: 2
outcome: "exhausted"
native_review_id: "review-2717a3266155585c61b8d6e9cf75c84a"
native_status: "accepted"
commit_mode: "normal"
authority_assurance: "unavailable"
author_model_id: "gpt-6.1-sol"
author_effort: "high"
author_session: "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
reviewer_session: "sha256:c8254d8e818025ffb23e08bc62f632a5bcbb5293376cd944530280a09f8db56e"
session_identity_kind: "native-fingerprint"
native_revision_commit: "87c3f104e7349fcc6b77c67ec5ae2fb0f664469a"
native_finalization_commit: "7a4582ccb1a08c1637226e15d2f14ca8530583d8"
verified_at: "2026-11-10T19:00:43Z"
---
# XPR review record

## Outcome and authority
Exhausted in 2 rounds with 3 sealed findings. Native reviewer consensus and author finalization bind exactly the final raw digest above. This record accepts only the named document; it does not authorize implementation, epic closure or a trunk merge.
Used installed ai-peer-review 0.4.1, native Claude, project-local broker, manual invitation transport and normal commit mode. The requested author/reviewer selections are recorded above. Native authority assurance is unavailable, with declared participant/model evidence; this is not independent execution attestation. Participant fingerprints are not raw private provider handles.

## Reconstruction
Apply patches in numerical order to an empty directory; empty patches use git apply --allow-empty. Every intermediate and final version was checked byte for byte against its recorded artifact and by raw SHA-256. Source commits are provenance; reconstruction does not depend on retaining their Git objects.
| Patch | Resulting raw digest | Bytes | Source commit |
| --- | --- | --- | --- |
| [patch-000.diff](patch-000.diff) | sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029 | 10273 | 9308cffd586c003c5ce8112ab3c91d1088999db8 |
| [patch-001.diff](patch-001.diff) | sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248 | 13197 | 87c3f104e7349fcc6b77c67ec5ae2fb0f664469a |
| [patch-002.diff](patch-002.diff) | sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248 | 0 | 7a4582ccb1a08c1637226e15d2f14ca8530583d8 |

## Native mapping and timing
Portable reviewer digests retain native inputs. Portable author digests name outgoing artifacts from native artifact history; native protected author headers name incoming artifacts. The final author acknowledgement is explicitly post-finalization and produces no FUR edit. Native final_commit can name the last artifact revision, so the actual finalization commit is recorded separately.
Native started_at fields may reuse participant registration across rounds. The exports use the first exact role claim where available, otherwise the prior submitted response as a qualified outer bound. These spans are not measured continuous engagement or necessarily response-writing duration; setup, waiting, pre-claim reading and publication remain exclusions/Unknown unless separately observed. No story timing events are silently rewritten by this export.
| Response | Start basis | Public anchor |
| --- | --- | --- |
| [reviewer-response-1.md](reviewer-response-1.md) | claim | native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-review-manifest.md#claim-claim-46194394-fd6f-4011-ac77-4bb668b5de2a |
| [author-response-1.md](author-response-1.md) | claim | native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-review-manifest.md#claim-claim-fdb10d76-59ef-4499-bb42-53cfd28126e5 |
| [reviewer-response-2.md](reviewer-response-2.md) | prior-submit | author-response-1.md |
| [author-response-2.md](author-response-2.md) | prior-submit | reviewer-response-2.md |

## Native original hashes
| File | Raw SHA-256 |
| --- | --- |
| [review-2717a3266155585c61b8d6e9cf75c84a-author-response-1.md](native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-author-response-1.md) | sha256:441f2d7384c8b819b2527a95111cb2129886a7718b4bb38305204a04e9280c42 |
| [review-2717a3266155585c61b8d6e9cf75c84a-review-manifest.md](native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-review-manifest.md) | sha256:b5cecd9ce5c6064b6f8a5af73daec88705668391c85ab4ee54f0deed8c69af43 |
| [review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-1.md](native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-1.md) | sha256:127f5b0daf8bf014f3278e3170a3ab82af5b811f07c75e3e82edb95db0f27801 |
| [review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-2.md](native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-2.md) | sha256:0e06cf276783ca5009f80474740c281ef45622457587c4827ce95ca09b66cd78 |

## Verification and publication boundary
Validated submitted response hashes against the terminal manifest, model/effort and participant continuity, complete sealed finding dispositions, per-turn input/output digests, exact final acceptance and unchanged native originals. Replayed all patches and compared every intermediate byte sequence. Check Markdown whitespace/links and scoped changes before import; preserve Git's single-space blank-context patch syntax and verify patches by replay. No product implementation tests are claimed.
Publication imports only the final FUR and this review folder into refreshed planning after its base/content preconditions are checked. The containing planning commit identifies publication without a self-referential manifest hash. Earlier levels accept their own bytes and do not retroactively approve these revisions.

Verified full-file retrieval for every round before finalization. [Retrieval audit](retrieval-audit.md).
