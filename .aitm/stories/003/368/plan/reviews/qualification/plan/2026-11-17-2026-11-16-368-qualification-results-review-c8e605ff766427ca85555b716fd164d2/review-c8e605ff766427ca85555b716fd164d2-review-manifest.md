<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "2413d45349bfe0c8426d2aad43c97b25d639aa0b",
      "commit": "834257c9789e9bcef591d629477dc679695bb08a",
      "digest": "sha256:566cc5717ab0f811ff9f6199d1e78a0cdeb637f0ea77cae956da4c03cb0d3c68",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-qualification-results.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "44579a5f89052eac463106f26b3e261a61f4a584",
      "commit": "5d66d3486b8543c5910fc9e78fa9655b6c828901",
      "digest": "sha256:add1b41d5dcccd4f8076d91a156508407cbf09f7b0bb2dd90c9be427e00caab0",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-qualification-results.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-qualification-results.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-b65ec7dd-712c-4252-b080-46c811bac993",
      "claimed_at": "2026-11-17T02:46:58.053Z",
      "expires_at": "2026-11-17T10:46:58.053Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T02:46:58.053Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:4a4e00a67f0d500b2aa384a480bbb27143ca3fa0c72c7558c8ff7105149bd114"
    },
    {
      "claim_id": "claim-058d97a4-d9ac-4fd4-b2d9-c03a88f521c5",
      "claimed_at": "2026-11-17T02:48:30.163Z",
      "expires_at": "2026-11-17T10:48:30.163Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T02:48:30.163Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "5d66d3486b8543c5910fc9e78fa9655b6c828901",
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
            "fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-17T02:46:31.037Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:17024e34590e93476bd5cf980da5907bf4ca4cd9eccd8da942cd576abb497a6d",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-c8e605ff766427ca85555b716fd164d2",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-c8e605ff766427ca85555b716fd164d2",
        "root_review_id": "review-c8e605ff766427ca85555b716fd164d2",
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
          "fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T02:46:31.037Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
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
          "fingerprint": "sha256:4a4e00a67f0d500b2aa384a480bbb27143ca3fa0c72c7558c8ff7105149bd114",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T02:46:58.016Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:4a4e00a67f0d500b2aa384a480bbb27143ca3fa0c72c7558c8ff7105149bd114"
    }
  },
  "record_id": "review-c8e605ff766427ca85555b716fd164d2",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-c8e605ff766427ca85555b716fd164d2",
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
    "project_root_digest": "e9830cc5264cee35051548283974fe72b138184f8ac8a3a2c7c7af8ebcdeb586",
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
  "startup_commit": "834257c9789e9bcef591d629477dc679695bb08a",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "44579a5f89052eac463106f26b3e261a61f4a584",
        "digest": "sha256:add1b41d5dcccd4f8076d91a156508407cbf09f7b0bb2dd90c9be427e00caab0",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-qualification-results.md"
      },
      "author_response": {
        "digest": "sha256:6b3581946d988f10eba1088a717e2b24a37301faed0e11d03c8de9b62c9c9fb7",
        "path": ".aitm/stories/003/368/plan/reviews/qualification/plan/2026-11-17-2026-11-16-368-qualification-results-review-c8e605ff766427ca85555b716fd164d2/review-c8e605ff766427ca85555b716fd164d2-author-response-1.md"
      },
      "commit": "5d66d3486b8543c5910fc9e78fa9655b6c828901",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:5a582cf1398a539c7e62653e0d36ee2e1265f3ca833bde12b830d459887caeb2",
        "path": ".aitm/stories/003/368/plan/reviews/qualification/plan/2026-11-17-2026-11-16-368-qualification-results-review-c8e605ff766427ca85555b716fd164d2/review-c8e605ff766427ca85555b716fd164d2-reviewer-response-1.md"
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
        "digest": "sha256:5793b5dff6ac39d44e7baed3af7c41822ff9b887df20a2f1f215325333f2df01",
        "path": ".aitm/stories/003/368/plan/reviews/qualification/plan/2026-11-17-2026-11-16-368-qualification-results-review-c8e605ff766427ca85555b716fd164d2/review-c8e605ff766427ca85555b716fd164d2-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
