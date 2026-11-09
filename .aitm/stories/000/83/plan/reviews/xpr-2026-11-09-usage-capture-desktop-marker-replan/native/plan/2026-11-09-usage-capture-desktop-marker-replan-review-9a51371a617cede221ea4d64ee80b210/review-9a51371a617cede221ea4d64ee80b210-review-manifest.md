<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "9c4b3d3a8aaa03eed901b9166f271cfe065f4f78",
      "commit": "37eb09413d7b96d34b5e1219abedf400bfc1cd3f",
      "digest": "sha256:b09cb8ee3dfee4b2af7b0773fa3a2b8dc54b68ba2d1287e17563eaf6da5abd90",
      "path": ".aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "2061d457edce4d7738a00072bd0b05d44e235b47",
      "commit": "5e4628835c246bed52938c76f370a0491670ad8e",
      "digest": "sha256:fb4a62308fb971dc8862d16175a0cb1c5cac3be69f96500f748895ad50ea135f",
      "path": ".aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-a6bacedb-cf98-43f4-a8bb-b65dc0eef4cd",
      "claimed_at": "2026-11-09T22:14:19.222Z",
      "expires_at": "2026-11-10T06:14:19.222Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T22:14:19.222Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:9cec225cc3095656c7d62b2ee43a2ad3b6ff7fc0d1605ea367ee75313ed320c6"
    },
    {
      "claim_id": "claim-f74f1942-448c-4969-81a9-afd9d6f86f43",
      "claimed_at": "2026-11-09T22:16:37.707Z",
      "expires_at": "2026-11-10T06:16:37.707Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T22:16:37.707Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "5e4628835c246bed52938c76f370a0491670ad8e",
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
        "joined_at": "2026-11-09T22:13:32.206Z",
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
        "event_log_digest": "sha256:d4fdcbfa377398a8060c01f27f5858a8cca72b635c7f8cbcfb21bfb841299a50",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-9a51371a617cede221ea4d64ee80b210",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-9a51371a617cede221ea4d64ee80b210",
        "root_review_id": "review-9a51371a617cede221ea4d64ee80b210",
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
      "joined_at": "2026-11-09T22:13:32.206Z",
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
          "fingerprint": "sha256:9cec225cc3095656c7d62b2ee43a2ad3b6ff7fc0d1605ea367ee75313ed320c6",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T22:14:19.201Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:9cec225cc3095656c7d62b2ee43a2ad3b6ff7fc0d1605ea367ee75313ed320c6"
    }
  },
  "record_id": "review-9a51371a617cede221ea4d64ee80b210",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-9a51371a617cede221ea4d64ee80b210",
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
    "project_root_digest": "ba43c9325f53c640bb4b89b2b9a13e10b28ef6d912cd9669a5a77ab4728a2adc",
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
  "startup_commit": "37eb09413d7b96d34b5e1219abedf400bfc1cd3f",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "2061d457edce4d7738a00072bd0b05d44e235b47",
        "digest": "sha256:fb4a62308fb971dc8862d16175a0cb1c5cac3be69f96500f748895ad50ea135f",
        "path": ".aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md"
      },
      "author_response": {
        "digest": "sha256:d3bda9ac6fe14ef90b6272241c49190e63ff13cf78d648d54dfeba8cdfab702c",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-desktop-marker-replan/native/plan/2026-11-09-usage-capture-desktop-marker-replan-review-9a51371a617cede221ea4d64ee80b210/review-9a51371a617cede221ea4d64ee80b210-author-response-1.md"
      },
      "commit": "5e4628835c246bed52938c76f370a0491670ad8e",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:cc8104b732a76d573f786b8e5dabd77c7ce0422b669d916162a76beb62ce2f75",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-desktop-marker-replan/native/plan/2026-11-09-usage-capture-desktop-marker-replan-review-9a51371a617cede221ea4d64ee80b210/review-9a51371a617cede221ea4d64ee80b210-reviewer-response-1.md"
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
        "digest": "sha256:b2b5538fb64aa39e0145b7bc439a213c725ebc510daddf1cd5b8fc1ecb181241",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-desktop-marker-replan/native/plan/2026-11-09-usage-capture-desktop-marker-replan-review-9a51371a617cede221ea4d64ee80b210/review-9a51371a617cede221ea4d64ee80b210-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
