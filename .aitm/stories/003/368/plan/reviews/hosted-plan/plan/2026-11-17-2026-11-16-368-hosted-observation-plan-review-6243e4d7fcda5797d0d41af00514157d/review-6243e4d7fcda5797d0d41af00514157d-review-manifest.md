<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "8e0f7b28e339217ece9de4b8aeba6dd5bf692459",
      "commit": "0213ea4d15c36f157390dcd5557c3cd402b7142e",
      "digest": "sha256:1972d91495d2e241c47da58e61302d478b589c82c01198ec5e76f5066a79b423",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-observation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "b3525957973846479093ef5313165a08d2c92443",
      "commit": "4d4458ddb0a50da9f68c7cceee61d03a23d2dadf",
      "digest": "sha256:51f56908994e273e9adce20f5d60813cb7b45cddd52051580241f9119e47bba9",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-observation-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-observation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-874d731f-3d77-4f07-9589-e842500db0ec",
      "claimed_at": "2026-11-17T04:30:53.861Z",
      "expires_at": "2026-11-17T12:30:53.861Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T04:30:53.861Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:8fc7ae3d6719f6e60e348c7e1e29c6f1abc1a36bb6a271375be89095a109ecba"
    },
    {
      "claim_id": "claim-c61ff81a-3f9e-4542-a1c1-d444e16edacf",
      "claimed_at": "2026-11-17T04:33:35.359Z",
      "expires_at": "2026-11-17T12:33:35.359Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T04:33:35.359Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "4d4458ddb0a50da9f68c7cceee61d03a23d2dadf",
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
        "joined_at": "2026-11-17T04:30:34.938Z",
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
        "event_log_digest": "sha256:2233b85cf875ad58dc7c8c4e8de1cd4a9f4e4370b9c3a7989385c2206c6f2a61",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-6243e4d7fcda5797d0d41af00514157d",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-6243e4d7fcda5797d0d41af00514157d",
        "root_review_id": "review-6243e4d7fcda5797d0d41af00514157d",
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
      "joined_at": "2026-11-17T04:30:34.938Z",
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
          "fingerprint": "sha256:8fc7ae3d6719f6e60e348c7e1e29c6f1abc1a36bb6a271375be89095a109ecba",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T04:30:53.831Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:8fc7ae3d6719f6e60e348c7e1e29c6f1abc1a36bb6a271375be89095a109ecba"
    }
  },
  "record_id": "review-6243e4d7fcda5797d0d41af00514157d",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-6243e4d7fcda5797d0d41af00514157d",
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
  "startup_commit": "0213ea4d15c36f157390dcd5557c3cd402b7142e",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "b3525957973846479093ef5313165a08d2c92443",
        "digest": "sha256:51f56908994e273e9adce20f5d60813cb7b45cddd52051580241f9119e47bba9",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-observation-plan.md"
      },
      "author_response": {
        "digest": "sha256:cd9fd7e3ed62ced9815755d442136bd5894ed0731414a417adaaab48527833f9",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-plan/plan/2026-11-17-2026-11-16-368-hosted-observation-plan-review-6243e4d7fcda5797d0d41af00514157d/review-6243e4d7fcda5797d0d41af00514157d-author-response-1.md"
      },
      "commit": "4d4458ddb0a50da9f68c7cceee61d03a23d2dadf",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:29b307c298f0a927d3253c5c263a5488c81878eae954ae5815717db66664f992",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-plan/plan/2026-11-17-2026-11-16-368-hosted-observation-plan-review-6243e4d7fcda5797d0d41af00514157d/review-6243e4d7fcda5797d0d41af00514157d-reviewer-response-1.md"
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
        "digest": "sha256:856efb51a30d00d4b334d8567f579c1d741fe9711cd2d72e125c19613b0b5680",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-plan/plan/2026-11-17-2026-11-16-368-hosted-observation-plan-review-6243e4d7fcda5797d0d41af00514157d/review-6243e4d7fcda5797d0d41af00514157d-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
