<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "d4519756d4bf65a56a6f2d636e7104f9154ff637",
      "commit": "82535b53a0d4efd26a66d528f8d4c60b79500c62",
      "digest": "sha256:d16be608871c267227c3ed63d3ebcfab9049f68a9abcb0056069885359b1e7e8",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-execution-packet.md",
      "snapshot": null,
      "turn": 0
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-execution-packet.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-fe60b007-0ed4-45d4-bed3-505fc3c40fe9",
      "claimed_at": "2026-11-17T12:36:58.839Z",
      "expires_at": "2026-11-17T20:36:58.839Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T12:36:58.839Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:9158ee2a1df867609e500da50f790e8fb88b27bbb5887d66955626f990108822"
    },
    {
      "claim_id": "claim-0f043441-4873-48ec-aeed-cba868663774",
      "claimed_at": "2026-11-17T12:40:31.001Z",
      "expires_at": "2026-11-17T20:40:31.001Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T12:40:31.001Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "82535b53a0d4efd26a66d528f8d4c60b79500c62",
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
        "joined_at": "2026-11-17T12:36:03.255Z",
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
        "event_log_digest": "sha256:b69e86bedb91d7e99c1a4f25b50cdf6d7515fea7f5201d4cabfb9c0b691f6ed5",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-ec49706b90ee3a43948821a58ed164a5",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-ec49706b90ee3a43948821a58ed164a5",
        "root_review_id": "review-ec49706b90ee3a43948821a58ed164a5",
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
      "joined_at": "2026-11-17T12:36:03.255Z",
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
          "fingerprint": "sha256:9158ee2a1df867609e500da50f790e8fb88b27bbb5887d66955626f990108822",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T12:36:58.818Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:9158ee2a1df867609e500da50f790e8fb88b27bbb5887d66955626f990108822"
    }
  },
  "record_id": "review-ec49706b90ee3a43948821a58ed164a5",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-ec49706b90ee3a43948821a58ed164a5",
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
  "startup_commit": "82535b53a0d4efd26a66d528f8d4c60b79500c62",
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
        "digest": "sha256:60dcacae1626c009b8448e40c0fcbb158fc3a6785ef42717bd9a616bae1c4753",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry-packet/plan/2026-11-17-2026-11-17-368-hosted-ancestry-execution-packet-review-ec49706b90ee3a43948821a58ed164a5/review-ec49706b90ee3a43948821a58ed164a5-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    }
  ]
}
```
