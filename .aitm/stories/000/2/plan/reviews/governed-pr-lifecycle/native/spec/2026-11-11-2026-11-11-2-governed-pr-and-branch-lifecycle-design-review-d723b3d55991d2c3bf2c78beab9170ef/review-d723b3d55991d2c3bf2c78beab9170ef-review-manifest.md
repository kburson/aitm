<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "4cfedfcbfbb7815aa2c5ddfa8aae80881b00e526",
      "commit": "71613ea0a2035e5e1e0ac2be6cfd70cc63b84487",
      "digest": "sha256:71dae425e57507082796dc4e8f475eadb4201de4eb0ead5d74c64942e6be419c",
      "path": ".aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "dfbf240cd8754be0974a6c6657033d98441009eb",
      "commit": "d192607c426d3dc081d104f5ece8dc0d13879417",
      "digest": "sha256:a8ebc9a9fb27ba705e63b467ed6ac3f920b75697fc01cd965aadb87f7a48d938",
      "path": ".aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "cd1d14285b8272dad0acbbdb19e5928dc8471c89",
      "commit": "2304562f53bbf47448d77ec9f07178d73036fffd",
      "digest": "sha256:e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3",
      "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md",
      "snapshot": null,
      "turn": 3
    }
  ],
  "artifact_path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-50ee9df4-42bc-46d8-829a-3ce96e2e41d6",
      "claimed_at": "2026-11-11T15:04:43.126Z",
      "expires_at": "2026-11-11T23:04:43.126Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-11T15:04:43.126Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4"
    },
    {
      "claim_id": "claim-44f37f3e-d8fd-43e7-b8a2-8d96f7750eef",
      "claimed_at": "2026-11-11T15:08:18.729Z",
      "expires_at": "2026-11-11T23:08:18.729Z",
      "host": "codex",
      "last_activity_at": "2026-11-11T15:08:18.729Z",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "2304562f53bbf47448d77ec9f07178d73036fffd",
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
        "joined_at": "2026-11-11T15:04:12.514Z",
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
        "event_log_digest": "sha256:e058c88dcc14edf67646c2e799fa580d8b3550a56b8b4ee38b30634db3d9b99d",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
        "root_review_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
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
      "joined_at": "2026-11-11T15:04:12.514Z",
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
          "fingerprint": "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-11T15:04:43.089Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4"
    }
  },
  "record_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
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
    "project_root_digest": "f55982b460b48963fb0246888183fd3bd58c6946c3b506d0e764e511b1bdcd20",
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
  "startup_commit": "71613ea0a2035e5e1e0ac2be6cfd70cc63b84487",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "dfbf240cd8754be0974a6c6657033d98441009eb",
        "digest": "sha256:a8ebc9a9fb27ba705e63b467ed6ac3f920b75697fc01cd965aadb87f7a48d938",
        "path": ".aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md"
      },
      "author_response": {
        "digest": "sha256:8ddc6b8d342a5d32656c9abb0bb7ad77fc92e5f848d1b5a15c0edf52a2321e7b",
        "path": ".aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-author-response-1.md"
      },
      "commit": "d192607c426d3dc081d104f5ece8dc0d13879417",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004",
        "R1-F005"
      ],
      "reviewer_response": {
        "digest": "sha256:faea01195ceba31b4b7d53c589f290ba7f64bb147cf7a95487ee669b8636adc4",
        "path": ".aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-response-1.md"
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
        "digest": "sha256:e041e5a6bf56e9a94406b56b0cfb08ee2e738a0e1d272bbfb37c0b59e6a1561f",
        "path": ".aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    },
    {
      "artifact": {
        "blob": "cd1d14285b8272dad0acbbdb19e5928dc8471c89",
        "digest": "sha256:e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3",
        "path": ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md"
      },
      "author_response": {
        "digest": "sha256:914b307f87baa773a66575e613d4e7ab232e4b34f1fda112d7a7abe2393e6d04",
        "path": ".aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-author-response-3.md"
      },
      "commit": "2304562f53bbf47448d77ec9f07178d73036fffd",
      "decision": "revisions-requested",
      "finding_ids": [
        "R3-F001",
        "R3-F002",
        "R3-F003",
        "R3-F004",
        "R3-F005"
      ],
      "reviewer_response": {
        "digest": "sha256:8f90a35c8f38ffdd2f7acfa6830c4134c1a310168112529ba46bfee28d37cadd",
        "path": ".aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    },
    {
      "artifact": null,
      "author_response": null,
      "commit": null,
      "decision": "accepted",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:38551e4949f01dc366e2b29d20cedd6b1d5962f8ecd9a0a99435de018215968f",
        "path": ".aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-response-4.md"
      },
      "snapshot": null,
      "turn": 4
    }
  ]
}
```
