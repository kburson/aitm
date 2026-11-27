<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "f995dee4153dfa571e63ab7ddbaa6e6ae7cc7f92",
      "commit": "8862808e2dd2062df1c0d2e156e6711c2dbaabbb",
      "digest": "sha256:c1b737d1b81f0627f046b2bea35e5e1561336a5af5f8ea0165a2e0dd65d2c3d6",
      "path": ".aitm/stories/005/523/design/rubric-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "af48d426f0f66147dc84b9975018df8191c4362c",
      "commit": "321f4a60d1d1d869544d2c4a9fdd8ee2e5bc9d4e",
      "digest": "sha256:282f7ac2895191588bd4a269b27cb31ac48d9f8a4949680b82c97fc72f970197",
      "path": ".aitm/stories/005/523/design/rubric-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/005/523/design/rubric-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-0bb83617-8082-4286-a572-dfbb075f9cd0",
      "claimed_at": "2026-11-27T06:13:28.231Z",
      "expires_at": "2026-11-27T14:13:28.231Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-27T06:13:28.231Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:ccfbf0dbfc3eb87af66bc7531a32efd2cbe447123438520bcef6f325dd23dfdc"
    },
    {
      "claim_id": "claim-317b204c-00cd-4512-a7f0-1cf6119f62ef",
      "claimed_at": "2026-11-27T06:14:52.890Z",
      "expires_at": "2026-11-27T14:14:52.890Z",
      "host": "codex",
      "last_activity_at": "2026-11-27T06:14:52.890Z",
      "role": "author",
      "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "321f4a60d1d1d869544d2c4a9fdd8ee2e5bc9d4e",
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
        "joined_at": "2026-11-27T06:12:53.105Z",
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
        "event_log_digest": "sha256:9fd1bf32c492b616f1704072b3be64cb448ac2690f93edcfbd8b3871980f5c23",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-e3cc08fe8be7c89350666f9039583e47",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-e3cc08fe8be7c89350666f9039583e47",
        "root_review_id": "review-e3cc08fe8be7c89350666f9039583e47",
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
      "joined_at": "2026-11-27T06:12:53.105Z",
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
          "fingerprint": "sha256:ccfbf0dbfc3eb87af66bc7531a32efd2cbe447123438520bcef6f325dd23dfdc",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-27T06:13:28.208Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:ccfbf0dbfc3eb87af66bc7531a32efd2cbe447123438520bcef6f325dd23dfdc"
    }
  },
  "record_id": "review-e3cc08fe8be7c89350666f9039583e47",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-e3cc08fe8be7c89350666f9039583e47",
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
    "project_root_digest": "37d8c029bfc03c5e9f7655ee21f5e3d2199d6778a502f5308e6abab8416177d4",
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
        "blob": "af48d426f0f66147dc84b9975018df8191c4362c",
        "digest": "sha256:282f7ac2895191588bd4a269b27cb31ac48d9f8a4949680b82c97fc72f970197",
        "path": ".aitm/stories/005/523/design/rubric-design.md"
      },
      "author_response": {
        "digest": "sha256:bd8a62e69234b3a1c06f52914e02b76303bed13c440f248751115d2f2ec1d8f6",
        "path": ".aitm/stories/005/523/design/reviews/spec/2026-11-27-rubric-design-review-e3cc08fe8be7c89350666f9039583e47/review-e3cc08fe8be7c89350666f9039583e47-author-response-1.md"
      },
      "commit": "321f4a60d1d1d869544d2c4a9fdd8ee2e5bc9d4e",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:95606407b84a6a2fe00c25b71c01e23e16f7441a683bc5360d6c40b8ce299c24",
        "path": ".aitm/stories/005/523/design/reviews/spec/2026-11-27-rubric-design-review-e3cc08fe8be7c89350666f9039583e47/review-e3cc08fe8be7c89350666f9039583e47-reviewer-response-1.md"
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
        "digest": "sha256:36a52368dcfb9a3f9b2f6f31e408d8e4a60aa6ff25b270603106b2ffc838c31c",
        "path": ".aitm/stories/005/523/design/reviews/spec/2026-11-27-rubric-design-review-e3cc08fe8be7c89350666f9039583e47/review-e3cc08fe8be7c89350666f9039583e47-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
