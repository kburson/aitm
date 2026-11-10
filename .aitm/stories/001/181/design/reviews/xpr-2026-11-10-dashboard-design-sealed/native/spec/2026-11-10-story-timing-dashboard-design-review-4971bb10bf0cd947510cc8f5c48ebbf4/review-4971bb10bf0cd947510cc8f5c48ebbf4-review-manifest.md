<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "9da51a9bfa253bbbd107bf712e7c581d737d49af",
      "commit": "307c2577e2848331f29bbd16402d82e5d95a3403",
      "digest": "sha256:3edf5b36d09c7832c31d69fdbce42391d28aecdaccf21d8bed3fbc25b84b6ccb",
      "path": ".aitm/stories/001/181/design/story-timing-dashboard-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "e5443575d6b93d2dd35165ef7cf9264628fd460e",
      "commit": "8be219e115777c05fa19f989bf77c5533ebf1df7",
      "digest": "sha256:ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5",
      "path": ".aitm/stories/001/181/design/story-timing-dashboard-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/001/181/design/story-timing-dashboard-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-98ae9636-41be-49f7-b64e-4e471b2d1fc6",
      "claimed_at": "2026-11-10T20:41:33.219Z",
      "expires_at": "2026-11-11T04:41:33.219Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T20:41:33.219Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:349b0f6682b403a7d39e3a413ed147008f5b5220a8e947a14d1ba9881a0c1098"
    },
    {
      "claim_id": "claim-fc6049e8-3c20-4353-83cc-3544ee5e41cb",
      "claimed_at": "2026-11-10T20:42:36.976Z",
      "expires_at": "2026-11-11T04:42:36.976Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T20:42:36.976Z",
      "role": "author",
      "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "8be219e115777c05fa19f989bf77c5533ebf1df7",
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
        "joined_at": "2026-11-10T20:41:07.560Z",
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
        "event_log_digest": "sha256:40aad85dd80f7a2fcd4537c3762960517a386a7a42c470293bc6f39769d0b4f6",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-4971bb10bf0cd947510cc8f5c48ebbf4",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-4971bb10bf0cd947510cc8f5c48ebbf4",
        "root_review_id": "review-4971bb10bf0cd947510cc8f5c48ebbf4",
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
      "joined_at": "2026-11-10T20:41:07.560Z",
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
          "fingerprint": "sha256:349b0f6682b403a7d39e3a413ed147008f5b5220a8e947a14d1ba9881a0c1098",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T20:41:33.197Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:349b0f6682b403a7d39e3a413ed147008f5b5220a8e947a14d1ba9881a0c1098"
    }
  },
  "record_id": "review-4971bb10bf0cd947510cc8f5c48ebbf4",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-4971bb10bf0cd947510cc8f5c48ebbf4",
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
    "project_root_digest": "b8f5cfdc5602cb75286c5c0daf948aee37c7e33ca668e362196d1752cc0eaf4e",
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
  "startup_commit": "307c2577e2848331f29bbd16402d82e5d95a3403",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "e5443575d6b93d2dd35165ef7cf9264628fd460e",
        "digest": "sha256:ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5",
        "path": ".aitm/stories/001/181/design/story-timing-dashboard-design.md"
      },
      "author_response": {
        "digest": "sha256:0f00ed8b162f12da4a8bddd527846b5e5c9f7a84321ced84804ca45b38cb685e",
        "path": ".aitm/stories/001/181/design/reviews/xpr-2026-11-10-dashboard-design-sealed/native/spec/2026-11-10-story-timing-dashboard-design-review-4971bb10bf0cd947510cc8f5c48ebbf4/review-4971bb10bf0cd947510cc8f5c48ebbf4-author-response-1.md"
      },
      "commit": "8be219e115777c05fa19f989bf77c5533ebf1df7",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:bbdabcfeb6c1682c2b3b970c6f82e2352f3151974e8957bfc743a754ef6ad537",
        "path": ".aitm/stories/001/181/design/reviews/xpr-2026-11-10-dashboard-design-sealed/native/spec/2026-11-10-story-timing-dashboard-design-review-4971bb10bf0cd947510cc8f5c48ebbf4/review-4971bb10bf0cd947510cc8f5c48ebbf4-reviewer-response-1.md"
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
        "digest": "sha256:5f92376f1b514abc25e057a84c2ddd476fb951f5e906caf46329ec353ee02fef",
        "path": ".aitm/stories/001/181/design/reviews/xpr-2026-11-10-dashboard-design-sealed/native/spec/2026-11-10-story-timing-dashboard-design-review-4971bb10bf0cd947510cc8f5c48ebbf4/review-4971bb10bf0cd947510cc8f5c48ebbf4-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
