---
schema: "aitm.review-manifest/v0"
level: "sar"
story: 140
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "c3d1b82a7b25eb275f6c3c352a5c2b64317e0a8a"
artifact_base_blob: "ab9b18f53446bc39ba71e783f3050f9eae774620"
base_digest: "sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55"
final_digest: "sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55"
rounds: 1
outcome: "exhausted"
execution: "manual"
authority_assurance: "declared-manual"
author_session: "codex:sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
reviewer_session: "codex:sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
verified_at: "2026-11-10T18:44:06Z"
---

# #140 SAR design review

Accepted after 1 rounds and 0 findings. Every response is bound
to the exact input or resulting raw digest. Reviewer retrieval records are
in the responses. Recorded UTC bounds do not establish engagement duration.

| Round | Reviewer | Author |
| --- | --- | --- |
| 1 | [Response](reviewer-response-1.md) | [Disposition](author-response-1.md) |

## Patch replay

| Patch | Resulting raw digest | Review worktree source |
| --- | --- | --- |
| [patch-000.diff](patch-000.diff) | `sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55` | `c3d1b82a7b25eb275f6c3c352a5c2b64317e0a8a` |
| [patch-001.diff](patch-001.diff) | `sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55` | `2dcdbbc7deed229479ad928e4184932ff8ad20df` |

Replayed every patch in order from an empty directory and checked each resulting file byte for byte against its source. The final author acknowledgment has an empty patch.
