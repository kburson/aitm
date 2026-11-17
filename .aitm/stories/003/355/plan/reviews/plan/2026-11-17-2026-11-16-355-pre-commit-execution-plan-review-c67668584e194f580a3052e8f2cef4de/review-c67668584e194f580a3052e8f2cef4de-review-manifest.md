<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "88b136427216f6b21324b27d9c8545bc3b3e98f5",
      "commit": "db3eb007db8eb004cacf497fd56d372bc579dc8f",
      "digest": "sha256:82d010f80234aed2bace6d51c591ddaec3b03c9b6e38f6295297ad9a56baefbb",
      "path": ".aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "69d3a275f37e103e75208c93b12d99c6b356c2f0",
      "commit": "8e0d41582cb3b61c10d1f63bd1280c3b9a321d3a",
      "digest": "sha256:c9dab6ea4fb421f46dae71e31db4d8dc772528704aea31c451880cc442de56c9",
      "path": ".aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-8e2a7dd8-77b3-48b0-9a59-ee19a878a493",
      "claimed_at": "2026-11-17T00:22:18.577Z",
      "expires_at": "2026-11-17T08:22:18.577Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T00:22:18.577Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:0135f0bf409b44d81249f9ed0ca7917c5525cab72e6b3d74ac0b3c6a2f8231f0"
    },
    {
      "claim_id": "claim-4021f7d0-5b87-4bec-ad6c-e39580bbfe3f",
      "claimed_at": "2026-11-17T00:25:30.881Z",
      "expires_at": "2026-11-17T08:25:30.881Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T00:25:30.881Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "8e0d41582cb3b61c10d1f63bd1280c3b9a321d3a",
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
        "joined_at": "2026-11-17T00:21:48.947Z",
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
        "event_log_digest": "sha256:96c987da31e940a8f303daaf1014e4cac28eef596886cf5b893cf6b76c0580a0",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-c67668584e194f580a3052e8f2cef4de",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-c67668584e194f580a3052e8f2cef4de",
        "root_review_id": "review-c67668584e194f580a3052e8f2cef4de",
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
      "joined_at": "2026-11-17T00:21:48.947Z",
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
          "fingerprint": "sha256:0135f0bf409b44d81249f9ed0ca7917c5525cab72e6b3d74ac0b3c6a2f8231f0",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T00:22:18.541Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:0135f0bf409b44d81249f9ed0ca7917c5525cab72e6b3d74ac0b3c6a2f8231f0"
    }
  },
  "record_id": "review-c67668584e194f580a3052e8f2cef4de",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-c67668584e194f580a3052e8f2cef4de",
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
  "startup_commit": "db3eb007db8eb004cacf497fd56d372bc579dc8f",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "69d3a275f37e103e75208c93b12d99c6b356c2f0",
        "digest": "sha256:c9dab6ea4fb421f46dae71e31db4d8dc772528704aea31c451880cc442de56c9",
        "path": ".aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md"
      },
      "author_response": {
        "digest": "sha256:f857eb71b666b3c6f3e9278613163bb9cbfb952e2c1ef96853235bf07b6be97d",
        "path": ".aitm/stories/003/355/plan/reviews/plan/2026-11-17-2026-11-16-355-pre-commit-execution-plan-review-c67668584e194f580a3052e8f2cef4de/review-c67668584e194f580a3052e8f2cef4de-author-response-1.md"
      },
      "commit": "8e0d41582cb3b61c10d1f63bd1280c3b9a321d3a",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002"
      ],
      "reviewer_response": {
        "digest": "sha256:e96fed8b470da8843d1d5dc61dc702594f337a354769b532f7567617c0fef7f7",
        "path": ".aitm/stories/003/355/plan/reviews/plan/2026-11-17-2026-11-16-355-pre-commit-execution-plan-review-c67668584e194f580a3052e8f2cef4de/review-c67668584e194f580a3052e8f2cef4de-reviewer-response-1.md"
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
        "digest": "sha256:6666f1da009595330d606bb353b38320ab3b528fe20762241e0536eb30b0034b",
        "path": ".aitm/stories/003/355/plan/reviews/plan/2026-11-17-2026-11-16-355-pre-commit-execution-plan-review-c67668584e194f580a3052e8f2cef4de/review-c67668584e194f580a3052e8f2cef4de-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
