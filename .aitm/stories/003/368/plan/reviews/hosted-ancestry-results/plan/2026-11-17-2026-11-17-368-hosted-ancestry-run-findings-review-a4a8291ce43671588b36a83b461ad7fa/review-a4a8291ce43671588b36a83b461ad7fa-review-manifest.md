<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "0219a6254b6da55ddf2de71464158d5ad2684a59",
      "commit": "6aebc0300ac50d07d34fa74516a78ab5264314c4",
      "digest": "sha256:e3b27b2243efc1afcbf893eee8f8e36e5ccaf4ea8c9d99bc4238e77638ddf3a3",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "9a2560235b9215e275ccaf857296903922c70fac",
      "commit": "e09af44445322e54bb8ec7a38e6ef928c12ee395",
      "digest": "sha256:08283cca09f45ed85d6c77f56ac49d3311fbbcdd6f40cce523227fe618ffc54e",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-a12dfacf-0296-4f59-9efb-d204aa838a09",
      "claimed_at": "2026-11-17T12:54:48.872Z",
      "expires_at": "2026-11-17T20:54:48.872Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T12:54:48.872Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:906d1c8ad78ca7a3a1895ccc186d94a7954127640f6c4ef55680b7319be12fd8"
    },
    {
      "claim_id": "claim-c83869ac-f68c-486e-9b3e-052f030d3da0",
      "claimed_at": "2026-11-17T12:56:43.907Z",
      "expires_at": "2026-11-17T20:56:43.907Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T12:56:43.907Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "e09af44445322e54bb8ec7a38e6ef928c12ee395",
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
        "joined_at": "2026-11-17T12:53:49.769Z",
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
        "event_log_digest": "sha256:10ec31cd665a88be42d0b530b52b526bfc1a232debc0fbe4fc7f0d61d4fc3ff6",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-a4a8291ce43671588b36a83b461ad7fa",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-a4a8291ce43671588b36a83b461ad7fa",
        "root_review_id": "review-a4a8291ce43671588b36a83b461ad7fa",
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
      "joined_at": "2026-11-17T12:53:49.769Z",
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
          "fingerprint": "sha256:906d1c8ad78ca7a3a1895ccc186d94a7954127640f6c4ef55680b7319be12fd8",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T12:54:48.850Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:906d1c8ad78ca7a3a1895ccc186d94a7954127640f6c4ef55680b7319be12fd8"
    }
  },
  "record_id": "review-a4a8291ce43671588b36a83b461ad7fa",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-a4a8291ce43671588b36a83b461ad7fa",
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
  "startup_commit": "6aebc0300ac50d07d34fa74516a78ab5264314c4",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "9a2560235b9215e275ccaf857296903922c70fac",
        "digest": "sha256:08283cca09f45ed85d6c77f56ac49d3311fbbcdd6f40cce523227fe618ffc54e",
        "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md"
      },
      "author_response": {
        "digest": "sha256:a83c96a0b7443beb71bb5ecc742e4f9643c5aa45daf29c4ac1b86144d30ab08b",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry-results/plan/2026-11-17-2026-11-17-368-hosted-ancestry-run-findings-review-a4a8291ce43671588b36a83b461ad7fa/review-a4a8291ce43671588b36a83b461ad7fa-author-response-1.md"
      },
      "commit": "e09af44445322e54bb8ec7a38e6ef928c12ee395",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:5188bd1a5e38f9815d847a0e4f3707bdc69181f08363294db79e94fb9f6f256d",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry-results/plan/2026-11-17-2026-11-17-368-hosted-ancestry-run-findings-review-a4a8291ce43671588b36a83b461ad7fa/review-a4a8291ce43671588b36a83b461ad7fa-reviewer-response-1.md"
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
        "digest": "sha256:2cf193f56c258dd409d6a8726623d74fb79dfe3263d9fff680e3c3e8dbfc14a1",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry-results/plan/2026-11-17-2026-11-17-368-hosted-ancestry-run-findings-review-a4a8291ce43671588b36a83b461ad7fa/review-a4a8291ce43671588b36a83b461ad7fa-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
