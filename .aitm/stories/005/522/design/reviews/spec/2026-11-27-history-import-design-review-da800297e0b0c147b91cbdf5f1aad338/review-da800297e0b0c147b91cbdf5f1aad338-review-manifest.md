<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "7eaa5a2ebba5e647ff6fe4651a89efd5cf4f3842",
      "commit": "8862808e2dd2062df1c0d2e156e6711c2dbaabbb",
      "digest": "sha256:d44646dd8a917a4ff7588d3582503604514bc869db24e219c43a5aba455a7556",
      "path": ".aitm/stories/005/522/design/history-import-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "5cac02dcdf9249ee8dc9628490f9690b11cf7947",
      "commit": "24b64a383b3acce48f502ff391f777bc0ed0fffd",
      "digest": "sha256:5d414016baf1d3c68360808d831cdc95d7198f25856c44230ee5b183394a5109",
      "path": ".aitm/stories/005/522/design/history-import-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/005/522/design/history-import-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-ecd2b01b-6712-4485-b0b3-cc311f245a70",
      "claimed_at": "2026-11-27T06:13:32.052Z",
      "expires_at": "2026-11-27T14:13:32.052Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-27T06:13:32.052Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:95893d0f86ac4fe1742705c376e1ca0f6d6c9a5fed1c21c230c0310a96695d6b"
    },
    {
      "claim_id": "claim-a2c353b1-73a4-437b-b6d8-54a8464a940a",
      "claimed_at": "2026-11-27T06:14:36.517Z",
      "expires_at": "2026-11-27T14:14:36.517Z",
      "host": "codex",
      "last_activity_at": "2026-11-27T06:14:36.517Z",
      "role": "author",
      "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "24b64a383b3acce48f502ff391f777bc0ed0fffd",
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
            "requested_id": "gpt-6.2-sol",
            "source": "launch-request"
          },
          "session": {
            "assurance": "declared",
            "fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-27T06:12:53.107Z",
        "model_display": "gpt-6.2-sol",
        "model_id": "gpt-6.2-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:0fc1d411f34b5837eb036e664d5c03c35343f82686d249033f00ce4c5485e8e3",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-da800297e0b0c147b91cbdf5f1aad338",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-da800297e0b0c147b91cbdf5f1aad338",
        "root_review_id": "review-da800297e0b0c147b91cbdf5f1aad338",
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
          "requested_id": "gpt-6.2-sol",
          "source": "launch-request"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-27T06:12:53.107Z",
      "model_display": "gpt-6.2-sol",
      "model_id": "gpt-6.2-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
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
          "fingerprint": "sha256:95893d0f86ac4fe1742705c376e1ca0f6d6c9a5fed1c21c230c0310a96695d6b",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-27T06:13:32.030Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:95893d0f86ac4fe1742705c376e1ca0f6d6c9a5fed1c21c230c0310a96695d6b"
    }
  },
  "record_id": "review-da800297e0b0c147b91cbdf5f1aad338",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-da800297e0b0c147b91cbdf5f1aad338",
  "runtime": {
    "adapter_version": "1.0.0",
    "author": {
      "effort": "medium",
      "host": "codex",
      "model_display": "gpt-6.2-sol",
      "model_id": "gpt-6.2-sol",
      "provider": "openai"
    },
    "classification": "XPR",
    "ownership": "broker",
    "project_root_digest": "d870bfc2684c68c456b37308f6556bf80b6157f17726ce7e07681bb6fa0e974a",
    "reviewer": {
      "effort": "medium",
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
  "startup_commit": "8862808e2dd2062df1c0d2e156e6711c2dbaabbb",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "5cac02dcdf9249ee8dc9628490f9690b11cf7947",
        "digest": "sha256:5d414016baf1d3c68360808d831cdc95d7198f25856c44230ee5b183394a5109",
        "path": ".aitm/stories/005/522/design/history-import-design.md"
      },
      "author_response": {
        "digest": "sha256:2dc5f8a4994ba4fbcbc4a11b98bd55705a15fee8a145864c53874515e5d963a3",
        "path": ".aitm/stories/005/522/design/reviews/spec/2026-11-27-history-import-design-review-da800297e0b0c147b91cbdf5f1aad338/review-da800297e0b0c147b91cbdf5f1aad338-author-response-1.md"
      },
      "commit": "24b64a383b3acce48f502ff391f777bc0ed0fffd",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:792ff6ef3ce82bf9684de166a189d85df7f2e67777c07cf66a150f7d5e262507",
        "path": ".aitm/stories/005/522/design/reviews/spec/2026-11-27-history-import-design-review-da800297e0b0c147b91cbdf5f1aad338/review-da800297e0b0c147b91cbdf5f1aad338-reviewer-response-1.md"
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
        "digest": "sha256:37a78956a4e8ebd566328ac3e07d68c48f458df3be11bd2f55765a86feead6fd",
        "path": ".aitm/stories/005/522/design/reviews/spec/2026-11-27-history-import-design-review-da800297e0b0c147b91cbdf5f1aad338/review-da800297e0b0c147b91cbdf5f1aad338-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
