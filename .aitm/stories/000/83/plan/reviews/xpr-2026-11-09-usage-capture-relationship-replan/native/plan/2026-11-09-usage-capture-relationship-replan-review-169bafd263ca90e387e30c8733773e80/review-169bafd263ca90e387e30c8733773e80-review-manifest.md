<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "0d14bcf7f40c3e8b3ad101cb79af54b2ea0cdb71",
      "commit": "cb260cbf200a1dc4a9c9bf51ba3c28446940230a",
      "digest": "sha256:808783745a4d374df12f84505c37b0e0a0d496bdcb263877ef34b579cd1b3c86",
      "path": ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "4a45658eb6427fddfb041f621ea4a9623d0a509e",
      "commit": "2e9b8972e3210ade69ca77ca23db1dd64d3e6f45",
      "digest": "sha256:55eb9f5a6edf6e0d8a63d9bce64979a1d397d5defc7608395511ae13127930c8",
      "path": ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-03726992-b1b1-4a5a-86dc-d61cab10c6bb",
      "claimed_at": "2026-11-09T16:29:24.822Z",
      "expires_at": "2026-11-10T00:29:24.822Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T16:29:24.822Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:b8abc3f5780ff388a9c4be71d3699780de9374625a3555d8e60b340df430ea14"
    },
    {
      "claim_id": "claim-645d63ff-ad8f-404b-bad0-ee13f8b50fa8",
      "claimed_at": "2026-11-09T16:32:37.289Z",
      "expires_at": "2026-11-10T00:32:37.289Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T16:32:37.289Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "2e9b8972e3210ade69ca77ca23db1dd64d3e6f45",
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
        "joined_at": "2026-11-09T16:29:02.361Z",
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
        "event_log_digest": "sha256:b8b6e66320c41d15b576fc5688c4ce605ed8e0eeb6e394067f3e7f260f428975",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-169bafd263ca90e387e30c8733773e80",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-169bafd263ca90e387e30c8733773e80",
        "root_review_id": "review-169bafd263ca90e387e30c8733773e80",
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
      "joined_at": "2026-11-09T16:29:02.361Z",
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
          "fingerprint": "sha256:b8abc3f5780ff388a9c4be71d3699780de9374625a3555d8e60b340df430ea14",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T16:29:24.792Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:b8abc3f5780ff388a9c4be71d3699780de9374625a3555d8e60b340df430ea14"
    }
  },
  "record_id": "review-169bafd263ca90e387e30c8733773e80",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-169bafd263ca90e387e30c8733773e80",
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
    "project_root_digest": "fb3931bbb8012bdab5da5d03feccbea683dea40bf4bc2e9de2e1185c16845b1f",
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
  "startup_commit": "cb260cbf200a1dc4a9c9bf51ba3c28446940230a",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "4a45658eb6427fddfb041f621ea4a9623d0a509e",
        "digest": "sha256:55eb9f5a6edf6e0d8a63d9bce64979a1d397d5defc7608395511ae13127930c8",
        "path": ".aitm/stories/000/83/plan/usage-capture-relationship-replan.md"
      },
      "author_response": {
        "digest": "sha256:ec2150222b62c07cabc3af073543944c31aa4cd3b7d17f0e21d3d6e36ba9d83c",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-relationship-replan/native/plan/2026-11-09-usage-capture-relationship-replan-review-169bafd263ca90e387e30c8733773e80/review-169bafd263ca90e387e30c8733773e80-author-response-1.md"
      },
      "commit": "2e9b8972e3210ade69ca77ca23db1dd64d3e6f45",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:2288c452dedede3fd99ee09a4da650ddd2a93228e21a4b09ae817e7c5958c05d",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-relationship-replan/native/plan/2026-11-09-usage-capture-relationship-replan-review-169bafd263ca90e387e30c8733773e80/review-169bafd263ca90e387e30c8733773e80-reviewer-response-1.md"
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
        "digest": "sha256:cb2aff19b2402b542719baf9dc7ad28985383de7cc592f7720d7fe948b153988",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-relationship-replan/native/plan/2026-11-09-usage-capture-relationship-replan-review-169bafd263ca90e387e30c8733773e80/review-169bafd263ca90e387e30c8733773e80-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
