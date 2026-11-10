<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "ae10ab6c1a4b552be834a33b8ac7f443a707425d",
      "commit": "06eb425c91e94f838942ef39baa6fa641a56ffca",
      "digest": "sha256:8c99b0029127336f941c5ba79baee0e26ebb2a3627a43b8397b5bab5f05307dc",
      "path": ".aitm/stories/001/133/design/test-impact-analysis-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "82581ae31746d3ddfbd5701568533d476daa15d2",
      "commit": "dd6df92579e9f09a64747135170a1d66509553ba",
      "digest": "sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928",
      "path": ".aitm/stories/001/133/design/test-impact-analysis-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/001/133/design/test-impact-analysis-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-4382ea1e-9b3d-4dd9-96be-cf021787f843",
      "claimed_at": "2026-11-10T16:13:06.376Z",
      "expires_at": "2026-11-11T00:13:06.376Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T16:13:06.376Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:94d6b7014ee526a5269981b34d8de38170e07567d6d2a536b45e04fa57b35e99"
    },
    {
      "claim_id": "claim-c783398b-01c0-42d0-8fb7-ee7fba991f3c",
      "claimed_at": "2026-11-10T16:15:46.326Z",
      "expires_at": "2026-11-11T00:15:46.326Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T16:15:46.326Z",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "dd6df92579e9f09a64747135170a1d66509553ba",
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
        "joined_at": "2026-11-10T16:12:32.298Z",
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
        "event_log_digest": "sha256:af65761bfb1544734007a07421c44613900027c8614a4742bdb19d66deb3a0ea",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-d895f6d52c2abd3dcb7ec33bd40b2bee",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-d895f6d52c2abd3dcb7ec33bd40b2bee",
        "root_review_id": "review-d895f6d52c2abd3dcb7ec33bd40b2bee",
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
      "joined_at": "2026-11-10T16:12:32.298Z",
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
          "fingerprint": "sha256:94d6b7014ee526a5269981b34d8de38170e07567d6d2a536b45e04fa57b35e99",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T16:13:06.356Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:94d6b7014ee526a5269981b34d8de38170e07567d6d2a536b45e04fa57b35e99"
    }
  },
  "record_id": "review-d895f6d52c2abd3dcb7ec33bd40b2bee",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-d895f6d52c2abd3dcb7ec33bd40b2bee",
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
    "project_root_digest": "824cca7a94524e6e923bb229220e7efbec22f069cee8a0cd72e235e175f339b5",
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
  "startup_commit": "06eb425c91e94f838942ef39baa6fa641a56ffca",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "82581ae31746d3ddfbd5701568533d476daa15d2",
        "digest": "sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928",
        "path": ".aitm/stories/001/133/design/test-impact-analysis-design.md"
      },
      "author_response": {
        "digest": "sha256:e8c200fb2dff08df346f5820b3e3cfa64e3b7f9f93e90d76ad7831c9cada24b2",
        "path": ".aitm/stories/001/133/design/reviews/xpr-2026-11-10-tia-design/native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-author-response-1.md"
      },
      "commit": "dd6df92579e9f09a64747135170a1d66509553ba",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003"
      ],
      "reviewer_response": {
        "digest": "sha256:d49fa0ce8c2b5a740362aa592f9476edc628d02d6fc7d51ab29efe8792403d5b",
        "path": ".aitm/stories/001/133/design/reviews/xpr-2026-11-10-tia-design/native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-1.md"
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
        "digest": "sha256:5a36cc9a4d14082e50de3e097d6d2187692a55723caecdbe224e0919915ab639",
        "path": ".aitm/stories/001/133/design/reviews/xpr-2026-11-10-tia-design/native/spec/2026-11-10-test-impact-analysis-design-review-d895f6d52c2abd3dcb7ec33bd40b2bee/review-d895f6d52c2abd3dcb7ec33bd40b2bee-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
