<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "79d94debb1a418e4b86302dfbfcf2336364353f1",
      "commit": "eaa2e3f06a464ec4275946add0c094f96d322c50",
      "digest": "sha256:1b9afd6e13275d1a35ef3be66c8ca98ac4186d0ce94f49257909b2731bb5c20f",
      "path": ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "9d6cd7ed0c822f4f70a9f1a3e0eddb20ac9627cc",
      "commit": "eb8ab8f471f33cdc52c1e67e01283ab8bc50cdd2",
      "digest": "sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0",
      "path": ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-04a1871e-43b8-47a1-811d-4a5919819418",
      "claimed_at": "2026-11-10T04:18:50.242Z",
      "expires_at": "2026-11-10T12:18:50.242Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T04:18:50.242Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:19aba777a140232c905945ba92b3184a1498366bb62ff2b21341e5c323631b7f"
    },
    {
      "claim_id": "claim-086a287e-dd69-4f27-88b0-b824749261a5",
      "claimed_at": "2026-11-10T04:23:06.724Z",
      "expires_at": "2026-11-10T12:23:06.724Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T04:23:06.724Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "eb8ab8f471f33cdc52c1e67e01283ab8bc50cdd2",
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
        "joined_at": "2026-11-10T04:18:22.449Z",
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
        "event_log_digest": "sha256:8c13d98ba946a321a0beb9d1ffe9ad1ecd46707b710ebe41031d27844d9d77fe",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-31cb99125142babd8d7777a8787e1d19",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-31cb99125142babd8d7777a8787e1d19",
        "root_review_id": "review-31cb99125142babd8d7777a8787e1d19",
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
      "joined_at": "2026-11-10T04:18:22.449Z",
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
          "fingerprint": "sha256:19aba777a140232c905945ba92b3184a1498366bb62ff2b21341e5c323631b7f",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T04:18:50.207Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:19aba777a140232c905945ba92b3184a1498366bb62ff2b21341e5c323631b7f"
    }
  },
  "record_id": "review-31cb99125142babd8d7777a8787e1d19",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-31cb99125142babd8d7777a8787e1d19",
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
    "project_root_digest": "c3cf87077905a20ab253cbc46a6d2e62ee3ed633fef73c7fcc4904df3e69ae4d",
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
  "startup_commit": "eaa2e3f06a464ec4275946add0c094f96d322c50",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "9d6cd7ed0c822f4f70a9f1a3e0eddb20ac9627cc",
        "digest": "sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0",
        "path": ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md"
      },
      "author_response": {
        "digest": "sha256:a60de9262af58346d117e1ce1f890b771cceb4f9b880e1e18f6c6a7966803085",
        "path": ".aitm/stories/001/104/design/reviews/xpr-2026-11-09-pr-attestation/spec/2026-11-10-github-tested-merge-binding-replan-review-31cb99125142babd8d7777a8787e1d19/review-31cb99125142babd8d7777a8787e1d19-author-response-1.md"
      },
      "commit": "eb8ab8f471f33cdc52c1e67e01283ab8bc50cdd2",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:a1bd03411c67e09f36b0303f540cc030e997e754d4b9189946c29697e316a291",
        "path": ".aitm/stories/001/104/design/reviews/xpr-2026-11-09-pr-attestation/spec/2026-11-10-github-tested-merge-binding-replan-review-31cb99125142babd8d7777a8787e1d19/review-31cb99125142babd8d7777a8787e1d19-reviewer-response-1.md"
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
        "digest": "sha256:3831d04637a763224e6db7b63ada31527e0badb914c863e7a77ba18069e2f222",
        "path": ".aitm/stories/001/104/design/reviews/xpr-2026-11-09-pr-attestation/spec/2026-11-10-github-tested-merge-binding-replan-review-31cb99125142babd8d7777a8787e1d19/review-31cb99125142babd8d7777a8787e1d19-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
