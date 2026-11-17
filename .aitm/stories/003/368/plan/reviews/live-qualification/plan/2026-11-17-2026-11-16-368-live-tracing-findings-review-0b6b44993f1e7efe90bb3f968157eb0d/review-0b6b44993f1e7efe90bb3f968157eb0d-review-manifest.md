<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "6c737a235b31d057135232071db66fdca91807d6",
      "commit": "1ad21a4654234095258cc1f190285405b141b8f6",
      "digest": "sha256:f220ce6cdc5e09c566328e6e2f1460cf68bd4ea7d10280631266790f9cc86ac3",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-live-tracing-findings.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "382dde510369c6c4fd9136b6fa0a6be0cf582633",
      "commit": "31fe732ee3eee8c44223da7924765ee8d30a01d5",
      "digest": "sha256:1a90ea94b51df6eb4d1238cacf51a53eff9d15195c16df47b3c0f37321768db4",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-live-tracing-findings.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-live-tracing-findings.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-d14f4c02-4289-4fc1-a4b6-be0242872ce1",
      "claimed_at": "2026-11-17T03:26:12.872Z",
      "expires_at": "2026-11-17T11:26:12.872Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T03:26:12.872Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:65c6e6a93b23f3d9e2ed4dc77dc4e1db015e70a4506e6e0242517e4f12e4d187"
    },
    {
      "claim_id": "claim-07a9472e-5ccf-47a3-bbaa-58d872592f08",
      "claimed_at": "2026-11-17T03:30:02.244Z",
      "expires_at": "2026-11-17T11:30:02.244Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T03:30:02.244Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "31fe732ee3eee8c44223da7924765ee8d30a01d5",
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
        "joined_at": "2026-11-17T03:25:53.521Z",
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
        "event_log_digest": "sha256:dd7f96cabad31cc61bc1fb3cf6de26dbee860fdeb5b6c22f65134f7dbeb1895a",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-0b6b44993f1e7efe90bb3f968157eb0d",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-0b6b44993f1e7efe90bb3f968157eb0d",
        "root_review_id": "review-0b6b44993f1e7efe90bb3f968157eb0d",
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
      "joined_at": "2026-11-17T03:25:53.521Z",
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
          "fingerprint": "sha256:65c6e6a93b23f3d9e2ed4dc77dc4e1db015e70a4506e6e0242517e4f12e4d187",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T03:26:12.853Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:65c6e6a93b23f3d9e2ed4dc77dc4e1db015e70a4506e6e0242517e4f12e4d187"
    }
  },
  "record_id": "review-0b6b44993f1e7efe90bb3f968157eb0d",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-0b6b44993f1e7efe90bb3f968157eb0d",
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
  "startup_commit": "1ad21a4654234095258cc1f190285405b141b8f6",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "382dde510369c6c4fd9136b6fa0a6be0cf582633",
        "digest": "sha256:1a90ea94b51df6eb4d1238cacf51a53eff9d15195c16df47b3c0f37321768db4",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-live-tracing-findings.md"
      },
      "author_response": {
        "digest": "sha256:eb1e5d3846b9953117b3e1ca233d873263ece59b731abca1ca740416c30b9f59",
        "path": ".aitm/stories/003/368/plan/reviews/live-qualification/plan/2026-11-17-2026-11-16-368-live-tracing-findings-review-0b6b44993f1e7efe90bb3f968157eb0d/review-0b6b44993f1e7efe90bb3f968157eb0d-author-response-1.md"
      },
      "commit": "31fe732ee3eee8c44223da7924765ee8d30a01d5",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:5b33f9c807b47d672dcbcb0f8abab7c4ebe8c4d133fa6999c73f139c9fce6f9b",
        "path": ".aitm/stories/003/368/plan/reviews/live-qualification/plan/2026-11-17-2026-11-16-368-live-tracing-findings-review-0b6b44993f1e7efe90bb3f968157eb0d/review-0b6b44993f1e7efe90bb3f968157eb0d-reviewer-response-1.md"
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
        "digest": "sha256:1600eeb8196e4e9b596fe318db7ac14223b7739ef7cca39b198a939b614ad9dc",
        "path": ".aitm/stories/003/368/plan/reviews/live-qualification/plan/2026-11-17-2026-11-16-368-live-tracing-findings-review-0b6b44993f1e7efe90bb3f968157eb0d/review-0b6b44993f1e7efe90bb3f968157eb0d-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
