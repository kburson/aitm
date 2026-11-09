<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "6eede19cdef846e435bdc17d094ccf2ef42494e1",
      "commit": "276b85a797c2d72a9919d2d06a2f1b48f8e7c478",
      "digest": "sha256:d4c46b81bb889277cd5a8563251317bfa15788081e9471c4a014d473eb378cdb",
      "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "a31e8b1db2a9536495629a11f5995dc97bcc1cfb",
      "commit": "cc1dc6c099cbd3ad7282feea51c8725f94491437",
      "digest": "sha256:07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5",
      "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-f1bf744c-c32c-4496-8c7c-dee2bae4002d",
      "claimed_at": "2026-11-09T14:33:55.569Z",
      "expires_at": "2026-11-09T22:33:55.569Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T14:33:55.569Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:e57e6bd4e0710d76019f34694d7770a7c6f05803339de1ab2574fa46eddeaab4"
    },
    {
      "claim_id": "claim-d1ce9c93-d81e-451a-9541-803a6833a745",
      "claimed_at": "2026-11-09T14:37:10.995Z",
      "expires_at": "2026-11-09T22:37:10.995Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T14:37:10.995Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "cc1dc6c099cbd3ad7282feea51c8725f94491437",
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
        "joined_at": "2026-11-09T14:33:35.682Z",
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
        "event_log_digest": "sha256:6ce9601d6375b5f805dc448a7f712d53d31b3ae52b6db6063265b62cdc0f168b",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-b9866e55f23b9f43821dd6b765321caa",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-b9866e55f23b9f43821dd6b765321caa",
        "root_review_id": "review-b9866e55f23b9f43821dd6b765321caa",
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
      "joined_at": "2026-11-09T14:33:35.682Z",
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
          "fingerprint": "sha256:e57e6bd4e0710d76019f34694d7770a7c6f05803339de1ab2574fa46eddeaab4",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T14:33:55.533Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:e57e6bd4e0710d76019f34694d7770a7c6f05803339de1ab2574fa46eddeaab4"
    }
  },
  "record_id": "review-b9866e55f23b9f43821dd6b765321caa",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-b9866e55f23b9f43821dd6b765321caa",
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
    "project_root_digest": "e9c69f8fda423c009d3ad44f7280976207b26e16bafc44246abea9fb95d93125",
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
  "startup_commit": "276b85a797c2d72a9919d2d06a2f1b48f8e7c478",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "a31e8b1db2a9536495629a11f5995dc97bcc1cfb",
        "digest": "sha256:07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5",
        "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:f3064d97d6aa800450ba8bb30895059bca9af0f6970fc05de3f57146634dad3b",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-plan/native/plan/2026-11-09-usage-capture-implementation-plan-review-b9866e55f23b9f43821dd6b765321caa/review-b9866e55f23b9f43821dd6b765321caa-author-response-1.md"
      },
      "commit": "cc1dc6c099cbd3ad7282feea51c8725f94491437",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:267247574b117615e064fad00e9cb88095a6c18a55fd348a2e6241c232546acf",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-plan/native/plan/2026-11-09-usage-capture-implementation-plan-review-b9866e55f23b9f43821dd6b765321caa/review-b9866e55f23b9f43821dd6b765321caa-reviewer-response-1.md"
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
        "digest": "sha256:43770d34a33a327e7713790dfe52ba0837dbec11163314d0094b00e15bb4da13",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-plan/native/plan/2026-11-09-usage-capture-implementation-plan-review-b9866e55f23b9f43821dd6b765321caa/review-b9866e55f23b9f43821dd6b765321caa-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
