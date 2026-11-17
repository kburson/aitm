<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "6f026669ea35c1c5661af7b9d4ce1c9e37b27b66",
      "commit": "b3c025146fffc29ac3cef328819b46f868f8b715",
      "digest": "sha256:e5b0a68a1c222db44adce3490a9331b8eea22506bb7198544f89bda3f5c9d360",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-run-findings.md",
      "snapshot": null,
      "turn": 0
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-run-findings.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-3455cd05-5dc0-408c-90dc-34b7094a3d93",
      "claimed_at": "2026-11-17T13:19:21.928Z",
      "expires_at": "2026-11-17T21:19:21.928Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T13:19:21.928Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:1a4b5871d0ae663f960edb235062db5a061cf86161c6214f1801fff2d8265c30"
    },
    {
      "claim_id": "claim-35631f12-6f64-44cb-b87a-2c1185406803",
      "claimed_at": "2026-11-17T13:22:35.267Z",
      "expires_at": "2026-11-17T21:22:35.267Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T13:22:35.267Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "b3c025146fffc29ac3cef328819b46f868f8b715",
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
        "joined_at": "2026-11-17T13:18:16.673Z",
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
        "event_log_digest": "sha256:6fc8028a825789cc3b50c7d0448d5971ebc3245420350e618514024d3417149a",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-878d48dc52fb7e3aa45b7e4d0000888f",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-878d48dc52fb7e3aa45b7e4d0000888f",
        "root_review_id": "review-878d48dc52fb7e3aa45b7e4d0000888f",
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
      "joined_at": "2026-11-17T13:18:16.673Z",
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
          "fingerprint": "sha256:1a4b5871d0ae663f960edb235062db5a061cf86161c6214f1801fff2d8265c30",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T13:19:21.906Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:1a4b5871d0ae663f960edb235062db5a061cf86161c6214f1801fff2d8265c30"
    }
  },
  "record_id": "review-878d48dc52fb7e3aa45b7e4d0000888f",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-878d48dc52fb7e3aa45b7e4d0000888f",
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
  "startup_commit": "b3c025146fffc29ac3cef328819b46f868f8b715",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": null,
      "author_response": null,
      "commit": null,
      "decision": "accepted",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:7d314d5dde3dc99158740a5c47187757d2b771359ba6f83074082db4a80ce865",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-queue-results/plan/2026-11-17-2026-11-17-368-queue-inclusive-run-findings-review-878d48dc52fb7e3aa45b7e4d0000888f/review-878d48dc52fb7e3aa45b7e4d0000888f-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    }
  ]
}
```
