---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 133
artifact_path: ".aitm/stories/001/133/design/test-impact-analysis-design.md"
artifact_base_commit: "06eb425c91e94f838942ef39baa6fa641a56ffca"
artifact_base_blob: "ae10ab6c1a4b552be834a33b8ac7f443a707425d"
base_digest: "sha256:8c99b0029127336f941c5ba79baee0e26ebb2a3627a43b8397b5bab5f05307dc"
final_digest: "sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928"
rounds: 2
outcome: "exhausted"
native_review_id: "review-d895f6d52c2abd3dcb7ec33bd40b2bee"
native_status: "accepted"
commit_mode: "normal"
authority_assurance: "unavailable"
author_model_id: "gpt-6.1-sol"
author_effort: "high"
author_session: "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
reviewer_session: "sha256:94d6b7014ee526a5269981b34d8de38170e07567d6d2a536b45e04fa57b35e99"
session_identity_kind: "native-fingerprint"
native_revision_commit: "dd6df92579e9f09a64747135170a1d66509553ba"
native_finalization_commit: "c9c681a6a0b7b87b1c8bfe22178a75db1a403e1b"
verified_at: "2026-11-10T16:19:10Z"
---
# XPR review record

## Outcome and authority
Exhausted in 2 rounds with 3 sealed findings. Native reviewer consensus and author finalization bind exactly the final raw digest above. This record accepts only the named document; it does not authorize implementation, epic closure or a trunk merge.
Used installed ai-peer-review 0.4.1, native Claude, project-local broker, manual invitation transport and normal commit mode. The requested author/reviewer selections are recorded above. Native authority assurance is unavailable, with declared participant/model evidence; this is not independent execution attestation. Participant fingerprints are not raw private provider handles.

## Reconstruction
Apply patches in numerical order to an empty directory; empty patches use git apply --allow-empty. Every intermediate and final version was checked byte for byte against its recorded artifact and by raw SHA-256. Source commits are provenance; reconstruction does not depend on retaining their Git objects.
| Patch | Resulting raw digest | Bytes | Source commit |
| --- | --- | --- | --- |
| [patch-000.diff](patch-000.diff) | sha256:8c99b0029127336f941c5ba79baee0e26ebb2a3627a43b8397b5bab5f05307dc | 31065 | 06eb425c91e94f838942ef39baa6fa641a56ffca |
| [patch-001.diff](patch-001.diff) | sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928 | 9642 | dd6df92579e9f09a64747135170a1d66509553ba |
| [patch-002.diff](patch-002.diff) | sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928 | 0 | c9c681a6a0b7b87b1c8bfe22178a75db1a403e1b |

## Native mapping and timing
Portable reviewer digests retain native inputs. Portable author digests name outgoing artifacts from native artifact history; native protected author headers name incoming artifacts. The final author acknowledgement is explicitly post-finalization and produces no FUR edit. Native final_commit can name the last artifact revision, so the actual finalization commit is recorded separately.
Native started_at fields may reuse participant registration across rounds. The exports use the first exact role claim where available, otherwise the prior submitted response as a qualified outer bound. These spans are not measured continuous engagement or necessarily response-writing duration; setup, waiting, pre-claim reading and publication remain exclusions/Unknown unless separately observed. No story timing events are silently rewritten by this export.
| Response | Start basis | Public anchor |
| --- | --- | --- |
| [reviewer-response-1.md](reviewer-response-1.md) | claim | native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-review-manifest.md#claim-claim-4382ea1e-9b3d-4dd9-96be-cf021787f843 |
| [author-response-1.md](author-response-1.md) | claim | native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-review-manifest.md#claim-claim-c783398b-01c0-42d0-8fb7-ee7fba991f3c |
| [reviewer-response-2.md](reviewer-response-2.md) | prior-submit | author-response-1.md |
| [author-response-2.md](author-response-2.md) | prior-submit | reviewer-response-2.md |

## Native original hashes
| File | Raw SHA-256 |
| --- | --- |
| [review-d895f6d52c2abd3dcb7ec33bd40b2bee-author-response-1.md](native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-author-response-1.md) | sha256:e8c200fb2dff08df346f5820b3e3cfa64e3b7f9f93e90d76ad7831c9cada24b2 |
| [review-d895f6d52c2abd3dcb7ec33bd40b2bee-review-manifest.md](native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-review-manifest.md) | sha256:49f32ef87ce2a7ff1b85c759fa1b43d7555bb010202a1cfb7e4c27549faa7aa1 |
| [review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-1.md](native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-1.md) | sha256:d49fa0ce8c2b5a740362aa592f9476edc628d02d6fc7d51ab29efe8792403d5b |
| [review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-2.md](native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-2.md) | sha256:5a36cc9a4d14082e50de3e097d6d2187692a55723caecdbe224e0919915ab639 |

## Verification and publication boundary
Validated submitted response hashes against the terminal manifest, model/effort and participant continuity, complete sealed finding dispositions, per-turn input/output digests, exact final acceptance and unchanged native originals. Replayed all patches and compared every intermediate byte sequence. Check Markdown whitespace/links and scoped changes before import; preserve Git's single-space blank-context patch syntax and verify patches by replay. No product implementation tests are claimed.
Publication imports only the final FUR and this review folder into refreshed planning after its base/content preconditions are checked. The containing planning commit identifies publication without a self-referential manifest hash. Earlier levels accept their own bytes and do not retroactively approve these revisions.

## Full-file retrieval

Both rounds passed the [retrieval audit](retrieval-audit.md) before finalization. All three sealed findings were resolved and accepted.
