# Phase Review Manifest

```json
{
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
    }
  ],
  "artifact_path": ".aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md",
  "authority": {
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
  "final_commit": "d192607c426d3dc081d104f5ece8dc0d13879417",
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
  "phase_index": 0,
  "phase_kind": "spec",
  "phase_start_commit": "71613ea0a2035e5e1e0ac2be6cfd70cc63b84487",
  "phase_status": "accepted",
  "record_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-d723b3d55991d2c3bf2c78beab9170ef",
  "schema": "ai-peer-review.phase-manifest/v1",
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
    }
  ]
}
```
