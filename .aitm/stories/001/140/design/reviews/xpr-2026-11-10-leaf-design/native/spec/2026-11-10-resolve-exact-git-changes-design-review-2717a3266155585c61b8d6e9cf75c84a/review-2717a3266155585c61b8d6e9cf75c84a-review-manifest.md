<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "fc752b3eeff4aa622960c46ab8f4a1be19be4392",
      "commit": "9308cffd586c003c5ce8112ab3c91d1088999db8",
      "digest": "sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029",
      "path": ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "d3c7ccce15ec822ca38d582d7c42cdd99dba0694",
      "commit": "87c3f104e7349fcc6b77c67ec5ae2fb0f664469a",
      "digest": "sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248",
      "path": ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-46194394-fd6f-4011-ac77-4bb668b5de2a",
      "claimed_at": "2026-11-10T18:55:56.453Z",
      "expires_at": "2026-11-11T02:55:56.453Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T18:55:56.453Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:c8254d8e818025ffb23e08bc62f632a5bcbb5293376cd944530280a09f8db56e"
    },
    {
      "claim_id": "claim-fdb10d76-59ef-4499-bb42-53cfd28126e5",
      "claimed_at": "2026-11-10T18:58:06.532Z",
      "expires_at": "2026-11-11T02:58:06.532Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T18:58:06.532Z",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "87c3f104e7349fcc6b77c67ec5ae2fb0f664469a",
  "human_decision": null,
  "identity_changes": [
    {
      "identity": {
        "evidence": {
          "model": {
            "assurance": "declared",
            "conflict": false,
            "declared_id": null,
            "observed_id": null,
            "requested_id": "gpt-6.1-sol",
            "source": "launch-request"
          },
          "session": {
            "assurance": "declared",
            "fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-10T18:55:35.533Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:d4b9150bbe32cab673ad13b52391d9eaa7524e099dd753a0576aaf63bb5da9c6",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-2717a3266155585c61b8d6e9cf75c84a",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-2717a3266155585c61b8d6e9cf75c84a",
        "root_review_id": "review-2717a3266155585c61b8d6e9cf75c84a",
        "successor_review_id": null
      }
    ],
    "complete": true,
    "schema": "ai-peer-review.lineage-receipt/v1"
  },
  "participants": {
    "author": {
      "evidence": {
        "model": {
          "assurance": "declared",
          "conflict": false,
          "declared_id": null,
          "observed_id": null,
          "requested_id": "gpt-6.1-sol",
          "source": "launch-request"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T18:55:35.533Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
    },
    "reviewer": {
      "evidence": {
        "model": {
          "assurance": "declared",
          "conflict": false,
          "declared_id": "claude-opus-5-5",
          "observed_id": null,
          "requested_id": null,
          "source": "environment-declaration"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:c8254d8e818025ffb23e08bc62f632a5bcbb5293376cd944530280a09f8db56e",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T18:55:56.402Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:c8254d8e818025ffb23e08bc62f632a5bcbb5293376cd944530280a09f8db56e"
    }
  },
  "record_id": "review-2717a3266155585c61b8d6e9cf75c84a",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-2717a3266155585c61b8d6e9cf75c84a",
  "runtime": {
    "adapter_version": "1.0.0",
    "author": {
      "effort": "high",
      "host": "codex",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai"
    },
    "classification": "XPR",
    "ownership": "broker",
    "project_root_digest": "dc959db10c1aa72b4332f328152a59bac7a4b7a24b8143e5502c2a6c05f77357",
    "reviewer": {
      "effort": "high",
      "host": "claude-code",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "selector": "claude"
    },
    "schema": "ai-peer-review.runtime/v1",
    "transport_mode": "manual"
  },
  "schema": "ai-peer-review.manifest/v1",
  "startup_commit": "9308cffd586c003c5ce8112ab3c91d1088999db8",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "d3c7ccce15ec822ca38d582d7c42cdd99dba0694",
        "digest": "sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248",
        "path": ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
      },
      "author_response": {
        "digest": "sha256:441f2d7384c8b819b2527a95111cb2129886a7718b4bb38305204a04e9280c42",
        "path": ".aitm/stories/001/140/design/reviews/xpr-2026-11-10-leaf-design/native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-author-response-1.md"
      },
      "commit": "87c3f104e7349fcc6b77c67ec5ae2fb0f664469a",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003"
      ],
      "reviewer_response": {
        "digest": "sha256:127f5b0daf8bf014f3278e3170a3ab82af5b811f07c75e3e82edb95db0f27801",
        "path": ".aitm/stories/001/140/design/reviews/xpr-2026-11-10-leaf-design/native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": null,
      "author_response": null,
      "commit": null,
      "decision": "accepted",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:0e06cf276783ca5009f80474740c281ef45622457587c4827ce95ca09b66cd78",
        "path": ".aitm/stories/001/140/design/reviews/xpr-2026-11-10-leaf-design/native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
