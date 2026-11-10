<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "7c7d4c65971b8424b6feb2189fb885d2b35c530a",
      "commit": "3c4815fb6e42a5372f9f99fad5453c4a535e0169",
      "digest": "sha256:e8e051336de6976db1a3cc87f42610cc6614d0946df9ac76d06773b4151e7b93",
      "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "04540fae5d2c669a087bb47c312f5f6fa984c3e3",
      "commit": "aa2ae50f99be443860fc8effc09c620755519585",
      "digest": "sha256:147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80",
      "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-6d8eaee1-24cd-4b72-b428-1bf14376711c",
      "claimed_at": "2026-11-10T20:58:00.074Z",
      "expires_at": "2026-11-11T04:58:00.074Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T20:58:00.074Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:ff8a11f512bd9ed26aac55367574791ae964359ddeb6d2365a98f8fe2916149f"
    },
    {
      "claim_id": "claim-5c3a68d0-45ba-43c1-9df2-4df36639bd99",
      "claimed_at": "2026-11-10T20:59:47.259Z",
      "expires_at": "2026-11-11T04:59:47.259Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T20:59:47.259Z",
      "role": "author",
      "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "aa2ae50f99be443860fc8effc09c620755519585",
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
            "fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-10T20:57:42.673Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:dd722924c033f03fedd842d7097fc313e5ad5a6517d6154bcef4423707e7b115",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-f5ba57dde8773c6e0ff6937ff556822e",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-f5ba57dde8773c6e0ff6937ff556822e",
        "root_review_id": "review-f5ba57dde8773c6e0ff6937ff556822e",
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
          "fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T20:57:42.673Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
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
          "fingerprint": "sha256:ff8a11f512bd9ed26aac55367574791ae964359ddeb6d2365a98f8fe2916149f",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T20:58:00.039Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:ff8a11f512bd9ed26aac55367574791ae964359ddeb6d2365a98f8fe2916149f"
    }
  },
  "record_id": "review-f5ba57dde8773c6e0ff6937ff556822e",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-f5ba57dde8773c6e0ff6937ff556822e",
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
    "project_root_digest": "0d6aba82b036c0b3ebbbab4e88351ff76ef325c2cdb0bce7576fa3c0a5f5bb95",
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
  "startup_commit": "3c4815fb6e42a5372f9f99fad5453c4a535e0169",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "04540fae5d2c669a087bb47c312f5f6fa984c3e3",
        "digest": "sha256:147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80",
        "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:50f55cf9d516e338f817cc7582b9e50c6d73529b03262e2c7ebd74e675668ecf",
        "path": ".aitm/stories/001/181/plan/reviews/xpr-2026-11-10-dashboard-plan-sealed/native/plan/2026-11-10-story-timing-dashboard-implementation-plan-review-f5ba57dde8773c6e0ff6937ff556822e/review-f5ba57dde8773c6e0ff6937ff556822e-author-response-1.md"
      },
      "commit": "aa2ae50f99be443860fc8effc09c620755519585",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:798a98a1caa0f6f8f03947d36ac5b658413d2673c48098ab450ba66ba3f85363",
        "path": ".aitm/stories/001/181/plan/reviews/xpr-2026-11-10-dashboard-plan-sealed/native/plan/2026-11-10-story-timing-dashboard-implementation-plan-review-f5ba57dde8773c6e0ff6937ff556822e/review-f5ba57dde8773c6e0ff6937ff556822e-reviewer-response-1.md"
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
        "digest": "sha256:10ff9f23fcd1d32f45186cfc296df59c8b4952b8b31047685bc52774441aab15",
        "path": ".aitm/stories/001/181/plan/reviews/xpr-2026-11-10-dashboard-plan-sealed/native/plan/2026-11-10-story-timing-dashboard-implementation-plan-review-f5ba57dde8773c6e0ff6937ff556822e/review-f5ba57dde8773c6e0ff6937ff556822e-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
