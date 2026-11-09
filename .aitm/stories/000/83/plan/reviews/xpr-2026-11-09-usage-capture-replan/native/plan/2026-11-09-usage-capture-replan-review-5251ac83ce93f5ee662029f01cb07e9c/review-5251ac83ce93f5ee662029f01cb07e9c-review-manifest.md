<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "60e80e32c0318687fe3c113424756653326a186d",
      "commit": "76a9cfd325d507523d18e6c83620b1a927f83605",
      "digest": "sha256:45eb4be3089c1eeaa744f98b1c90e2c1329364e682492b0e8e8c363807ef0d44",
      "path": ".aitm/stories/000/83/plan/usage-capture-replan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "17114b365b823c3060e01d776ea6bb34593ced7d",
      "commit": "fa3fa0f4fd68e40c0fb53c641bb8263326458088",
      "digest": "sha256:7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239",
      "path": ".aitm/stories/000/83/plan/usage-capture-replan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/83/plan/usage-capture-replan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-cfe7a48f-41a7-4599-807e-66a1a4e6d18e",
      "claimed_at": "2026-11-09T15:09:08.428Z",
      "expires_at": "2026-11-09T23:09:08.428Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T15:09:08.428Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:be2e1af31a171c19a3157ffccc748eaf9c79acb8ac3da44acd18b46ef3aa1d6e"
    },
    {
      "claim_id": "claim-f35907aa-17e7-4b64-856d-2a901fdb98c8",
      "claimed_at": "2026-11-09T15:12:58.833Z",
      "expires_at": "2026-11-09T23:12:58.833Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T15:12:58.833Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "fa3fa0f4fd68e40c0fb53c641bb8263326458088",
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
            "fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-09T15:08:26.364Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:8fcfce8735cb3346b537a0ad5b6856fc218fe98aef52f9562342a76deed46dac",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-5251ac83ce93f5ee662029f01cb07e9c",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-5251ac83ce93f5ee662029f01cb07e9c",
        "root_review_id": "review-5251ac83ce93f5ee662029f01cb07e9c",
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
          "fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T15:08:26.364Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
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
          "fingerprint": "sha256:be2e1af31a171c19a3157ffccc748eaf9c79acb8ac3da44acd18b46ef3aa1d6e",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T15:09:08.408Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:be2e1af31a171c19a3157ffccc748eaf9c79acb8ac3da44acd18b46ef3aa1d6e"
    }
  },
  "record_id": "review-5251ac83ce93f5ee662029f01cb07e9c",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-5251ac83ce93f5ee662029f01cb07e9c",
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
    "project_root_digest": "d345db57fa6c5be45ad9026a3f28d8080f44cacfbc27f14a7b45c9524eba1f6c",
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
  "startup_commit": "76a9cfd325d507523d18e6c83620b1a927f83605",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "17114b365b823c3060e01d776ea6bb34593ced7d",
        "digest": "sha256:7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239",
        "path": ".aitm/stories/000/83/plan/usage-capture-replan.md"
      },
      "author_response": {
        "digest": "sha256:fbf511426feb08dbd8115cd17034c520d895c9a5b4027e2ab8ff962c69f96ff7",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-replan/native/plan/2026-11-09-usage-capture-replan-review-5251ac83ce93f5ee662029f01cb07e9c/review-5251ac83ce93f5ee662029f01cb07e9c-author-response-1.md"
      },
      "commit": "fa3fa0f4fd68e40c0fb53c641bb8263326458088",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:fa5ee309e3f5afbd4eea59cfecbc643dfc892cda91d5c9714f8439e0d76b29e0",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-replan/native/plan/2026-11-09-usage-capture-replan-review-5251ac83ce93f5ee662029f01cb07e9c/review-5251ac83ce93f5ee662029f01cb07e9c-reviewer-response-1.md"
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
        "digest": "sha256:e5d8ea56cd6b733d14f456a26cf0d04b22353d0a264690cad1fd10f23b24a585",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-replan/native/plan/2026-11-09-usage-capture-replan-review-5251ac83ce93f5ee662029f01cb07e9c/review-5251ac83ce93f5ee662029f01cb07e9c-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
