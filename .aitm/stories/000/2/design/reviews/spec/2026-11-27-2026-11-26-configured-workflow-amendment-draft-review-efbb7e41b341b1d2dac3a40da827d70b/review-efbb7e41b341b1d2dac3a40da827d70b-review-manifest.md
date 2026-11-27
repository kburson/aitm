<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "c88410d3418c671cbd5a3f2f25b5f9526696db88",
      "commit": "27c54333856e11b8453b9f3a09b4458e89c99756",
      "digest": "sha256:330c2351403277f8845b6dd162472a7844ba0ac7e944ce60f7dae8f13589a1d5",
      "path": ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "5a81dcba27f16370b2428262095fd409d6b091d8",
      "commit": "c25f0562b1ba64785c960118396403ef8ebfb95d",
      "digest": "sha256:3a1ce63175d7eb446fc9514b394c3c4916ef7a0adc22234ac6e62170fc70f004",
      "path": ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-5da38898-e0ae-4c4f-ade7-70f9c7e4e72c",
      "claimed_at": "2026-11-27T03:30:37.794Z",
      "expires_at": "2026-11-27T11:30:37.794Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-27T03:30:37.794Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:4a404e4d685336b447771b3d5eceaa0ba37b0cc7a6f54d991bd8e177c503acc6"
    },
    {
      "claim_id": "claim-dab708f5-9ed8-4242-9d73-c27405cac597",
      "claimed_at": "2026-11-27T03:32:23.967Z",
      "expires_at": "2026-11-27T11:32:23.967Z",
      "host": "codex",
      "last_activity_at": "2026-11-27T03:32:23.967Z",
      "role": "author",
      "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "c25f0562b1ba64785c960118396403ef8ebfb95d",
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
        "joined_at": "2026-11-27T03:30:02.221Z",
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
        "event_log_digest": "sha256:8736dafbae75c34f4734405a145c8143ff03dfaec40bb1e412e337812342f63f",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-efbb7e41b341b1d2dac3a40da827d70b",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-efbb7e41b341b1d2dac3a40da827d70b",
        "root_review_id": "review-efbb7e41b341b1d2dac3a40da827d70b",
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
      "joined_at": "2026-11-27T03:30:02.221Z",
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
          "fingerprint": "sha256:4a404e4d685336b447771b3d5eceaa0ba37b0cc7a6f54d991bd8e177c503acc6",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-27T03:30:37.750Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:4a404e4d685336b447771b3d5eceaa0ba37b0cc7a6f54d991bd8e177c503acc6"
    }
  },
  "record_id": "review-efbb7e41b341b1d2dac3a40da827d70b",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-efbb7e41b341b1d2dac3a40da827d70b",
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
    "project_root_digest": "e9830cc5264cee35051548283974fe72b138184f8ac8a3a2c7c7af8ebcdeb586",
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
  "startup_commit": "27c54333856e11b8453b9f3a09b4458e89c99756",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "5a81dcba27f16370b2428262095fd409d6b091d8",
        "digest": "sha256:3a1ce63175d7eb446fc9514b394c3c4916ef7a0adc22234ac6e62170fc70f004",
        "path": ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md"
      },
      "author_response": {
        "digest": "sha256:3e804d679d84f1d38951dbb430b2c32d9b6aa20693575e4991093b7b96c9b19b",
        "path": ".aitm/stories/000/2/design/reviews/spec/2026-11-27-2026-11-26-configured-workflow-amendment-draft-review-efbb7e41b341b1d2dac3a40da827d70b/review-efbb7e41b341b1d2dac3a40da827d70b-author-response-1.md"
      },
      "commit": "c25f0562b1ba64785c960118396403ef8ebfb95d",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:c3e18f78c40746b3ada8428a6fe292bf19fd8a5d9b8b94eddaf5aeb4e30407b1",
        "path": ".aitm/stories/000/2/design/reviews/spec/2026-11-27-2026-11-26-configured-workflow-amendment-draft-review-efbb7e41b341b1d2dac3a40da827d70b/review-efbb7e41b341b1d2dac3a40da827d70b-reviewer-response-1.md"
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
        "digest": "sha256:aeb3b584dce536cbbf5e1d58eb6b9c75e1325ebcb544ddc7f62e0c4de842d817",
        "path": ".aitm/stories/000/2/design/reviews/spec/2026-11-27-2026-11-26-configured-workflow-amendment-draft-review-efbb7e41b341b1d2dac3a40da827d70b/review-efbb7e41b341b1d2dac3a40da827d70b-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
