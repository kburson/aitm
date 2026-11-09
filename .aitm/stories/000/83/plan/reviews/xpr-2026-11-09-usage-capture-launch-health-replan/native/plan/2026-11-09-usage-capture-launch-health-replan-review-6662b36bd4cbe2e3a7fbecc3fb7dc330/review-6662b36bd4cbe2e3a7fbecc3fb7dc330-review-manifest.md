<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "9fb51b6efcbf85d241f4e4cc7cab853453b1af0d",
      "commit": "e88eb90047db8abfee09cec4d1515ed565bd175f",
      "digest": "sha256:92052b1066427e339601501f3cafcc4b98da89bf6f9a889ede702ac877102dda",
      "path": ".aitm/stories/000/83/plan/usage-capture-launch-health-replan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "c14822dfeeca657b1a20083685ca8fcaabae4e1b",
      "commit": "64e425817c676f8d71fdf0e9cffed749aac367bb",
      "digest": "sha256:a7cdf82a5cb1bf215b13e1b286d38cae55cfc18d2d6007dcb86cd9aef1aa66e6",
      "path": ".aitm/stories/000/83/plan/usage-capture-launch-health-replan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/83/plan/usage-capture-launch-health-replan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-ce7aad0d-b779-48ec-861f-d3567cffcd43",
      "claimed_at": "2026-11-09T20:45:50.492Z",
      "expires_at": "2026-11-10T04:45:50.492Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T20:45:50.492Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:e4fa9f0da9324635d8b92a67b1ff93fb5fb7f68f34b4b3caea236c8cc5903284"
    },
    {
      "claim_id": "claim-888e6df8-19ea-4c3f-9368-364554198818",
      "claimed_at": "2026-11-09T20:48:45.623Z",
      "expires_at": "2026-11-10T04:48:45.623Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T20:48:45.623Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "64e425817c676f8d71fdf0e9cffed749aac367bb",
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
        "joined_at": "2026-11-09T20:45:24.016Z",
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
        "event_log_digest": "sha256:992bf0f566c99a315a9f99b6219535163a2bb2499e65d95e5db3c6d826e75804",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-6662b36bd4cbe2e3a7fbecc3fb7dc330",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-6662b36bd4cbe2e3a7fbecc3fb7dc330",
        "root_review_id": "review-6662b36bd4cbe2e3a7fbecc3fb7dc330",
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
      "joined_at": "2026-11-09T20:45:24.016Z",
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
          "fingerprint": "sha256:e4fa9f0da9324635d8b92a67b1ff93fb5fb7f68f34b4b3caea236c8cc5903284",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T20:45:50.472Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:e4fa9f0da9324635d8b92a67b1ff93fb5fb7f68f34b4b3caea236c8cc5903284"
    }
  },
  "record_id": "review-6662b36bd4cbe2e3a7fbecc3fb7dc330",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-6662b36bd4cbe2e3a7fbecc3fb7dc330",
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
    "project_root_digest": "c8e90104a9fbb824fd65a388a73c4c264775fe7117fd5a9121162d2d8b8a5c4a",
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
  "startup_commit": "e88eb90047db8abfee09cec4d1515ed565bd175f",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "c14822dfeeca657b1a20083685ca8fcaabae4e1b",
        "digest": "sha256:a7cdf82a5cb1bf215b13e1b286d38cae55cfc18d2d6007dcb86cd9aef1aa66e6",
        "path": ".aitm/stories/000/83/plan/usage-capture-launch-health-replan.md"
      },
      "author_response": {
        "digest": "sha256:5c2d90dd450a0a68a8c2a5275adf8de39e0e65ffc6608b9e17cc83c43335a7e0",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-author-response-1.md"
      },
      "commit": "64e425817c676f8d71fdf0e9cffed749aac367bb",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:dbfee34ec509db7afb0ea93d952b7ae39ee95b0db19eb9741838c4827d7bf9bc",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-response-1.md"
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
        "digest": "sha256:1a0e4eaa6b650015574ade93e0b0925cc28681fb263444977d7924c96480efc8",
        "path": ".aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
