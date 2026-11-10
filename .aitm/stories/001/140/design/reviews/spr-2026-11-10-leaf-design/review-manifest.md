---
schema: "aitm.review-manifest/v0"
level: "spr"
story: 140
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "e2411e2082f566c61a3943d293cd6881392c49a4"
artifact_base_blob: "ab9b18f53446bc39ba71e783f3050f9eae774620"
base_digest: "sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55"
final_digest: "sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029"
rounds: 2
outcome: "exhausted"
execution: "manual"
authority_assurance: "declared-manual"
author_session: "codex:sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
reviewer_session: "codex-collaboration:/root/refine_138"
verified_at: "2026-11-10T18:47:33Z"
---

# #140 SPR design review

Accepted after 2 rounds and 1 findings. Every response is bound
to the exact input or resulting raw digest. Reviewer retrieval records are
in the responses. Recorded UTC bounds do not establish engagement duration.

| Round | Reviewer | Author |
| --- | --- | --- |
| 1 | [Response](reviewer-response-1.md) | [Disposition](author-response-1.md) |
| 2 | [Response](reviewer-response-2.md) | [Disposition](author-response-2.md) |

## Patch replay

| Patch | Resulting raw digest | Review worktree source |
| --- | --- | --- |
| [patch-000.diff](patch-000.diff) | `sha256:edbf6cae0ba425d140b57bd881de42ed9c1f27e81398f655ead1e4e2c5014e55` | `e2411e2082f566c61a3943d293cd6881392c49a4` |
| [patch-001.diff](patch-001.diff) | `sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029` | `b9e5e64d9a2fab187e44983ab0d76fcd4c1bf9d4` |
| [patch-002.diff](patch-002.diff) | `sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029` | `b0b25295d5651c5435d1be8ccf1f8926905cb75d` |

Replayed every patch in order from an empty directory and checked each resulting file byte for byte against its source. The final author acknowledgment has an empty patch.
