<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "53345663dd176a1c51703ad26ce34ae791ca83f8",
      "commit": "42c19d20382c324703e791390a6f8747640974b9",
      "digest": "sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba",
      "path": ".aitm/stories/000/1/design/architecture.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "74dfc233067be07a20d73623c50e7587fbd5104c",
      "commit": "572a1772005290bcfcee8531bf5955f7b7d7bbed",
      "digest": "sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93",
      "path": ".aitm/stories/000/1/design/architecture.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/1/design/architecture.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-38f83002-6a0b-4957-95df-f212085ea73a",
      "claimed_at": "2026-11-09T03:53:44.290Z",
      "expires_at": "2026-11-09T11:53:44.290Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T03:53:44.290Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:767689f69b20228949123d8faba84671fb404a4027e939125a5f4ad422c4d3a4"
    },
    {
      "claim_id": "claim-67fbcf4f-c563-4996-849d-5bf009d92617",
      "claimed_at": "2026-11-09T03:57:41.019Z",
      "expires_at": "2026-11-09T11:57:41.019Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T03:57:41.019Z",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "572a1772005290bcfcee8531bf5955f7b7d7bbed",
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
            "requested_id": "gpt-6-astra",
            "source": "launch-request"
          },
          "session": {
            "assurance": "declared",
            "fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-09T03:52:36.704Z",
        "model_display": "gpt-6-astra",
        "model_id": "gpt-6-astra",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:9749343f49052db351b1b7edd733d162337dddf19d70f5929d9081cd174cbed5",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-19d319c42ae6474b0b404114fd611a9c",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-19d319c42ae6474b0b404114fd611a9c",
        "root_review_id": "review-19d319c42ae6474b0b404114fd611a9c",
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
          "requested_id": "gpt-6-astra",
          "source": "launch-request"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T03:52:36.704Z",
      "model_display": "gpt-6-astra",
      "model_id": "gpt-6-astra",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
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
          "fingerprint": "sha256:767689f69b20228949123d8faba84671fb404a4027e939125a5f4ad422c4d3a4",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T03:53:44.261Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:767689f69b20228949123d8faba84671fb404a4027e939125a5f4ad422c4d3a4"
    }
  },
  "record_id": "review-19d319c42ae6474b0b404114fd611a9c",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-19d319c42ae6474b0b404114fd611a9c",
  "runtime": {
    "adapter_version": "1.0.0",
    "author": {
      "effort": "xhigh",
      "host": "codex",
      "model_display": "gpt-6-astra",
      "model_id": "gpt-6-astra",
      "provider": "openai"
    },
    "classification": "XPR",
    "ownership": "broker",
    "project_root_digest": "57e1fd60e20d02ec69af0b39dc81e76b723cb965c43c6245734d1687d71fb677",
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
  "startup_commit": "42c19d20382c324703e791390a6f8747640974b9",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "74dfc233067be07a20d73623c50e7587fbd5104c",
        "digest": "sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93",
        "path": ".aitm/stories/000/1/design/architecture.md"
      },
      "author_response": {
        "digest": "sha256:420de6e0751b3e86c51859fb92878bd17f8f8878a703618145c342d0ba24038b",
        "path": ".aitm/stories/000/1/design/reviews/xpr-2026-11-08-architecture/native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-author-response-1.md"
      },
      "commit": "572a1772005290bcfcee8531bf5955f7b7d7bbed",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004",
        "R1-F005"
      ],
      "reviewer_response": {
        "digest": "sha256:c38dbea3193984a27be1b4af6bd3c50ed71195446d4049c524de5cadda3b05e4",
        "path": ".aitm/stories/000/1/design/reviews/xpr-2026-11-08-architecture/native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-reviewer-response-1.md"
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
        "digest": "sha256:c0644aa843e02c1deb96540993cb9e5ea1764e1ae7609088d8a3dd079c42d586",
        "path": ".aitm/stories/000/1/design/reviews/xpr-2026-11-08-architecture/native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
