<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "f4bebd11c067e3450226a6a0292d52e5aa04ff5c",
      "commit": "fb03ec8c197db1c5c4d41c81907466b66eba30c4",
      "digest": "sha256:0f2f876d2ba2891006a77a8aee43d1bce000a0d8ecfdc1ac7083bc49e833ce55",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-execution-packet.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "06d1c9703e2684cd56d3263c6551d8d0048120c3",
      "commit": "5d5eb2876493aab63684da798230130ec8930f99",
      "digest": "sha256:4065c91cc4fe50a48aa5a3d8cc4f557831d3f5cf310145961221c4789612e18b",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-execution-packet.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-execution-packet.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-57add6ec-0d65-440a-ab05-1ffaa9654480",
      "claimed_at": "2026-11-17T13:05:49.217Z",
      "expires_at": "2026-11-17T21:05:49.217Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T13:05:49.217Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:bb2fa3e5d45b41281bb7b95072c1b45ffcf5d5bc308a372e581ac9e1d81b4e54"
    },
    {
      "claim_id": "claim-4cabe3eb-32ec-4ca6-b7d5-6e173cc249af",
      "claimed_at": "2026-11-17T13:07:17.244Z",
      "expires_at": "2026-11-17T21:07:17.244Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T13:07:17.244Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "5d5eb2876493aab63684da798230130ec8930f99",
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
        "joined_at": "2026-11-17T13:04:54.831Z",
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
        "event_log_digest": "sha256:2c594a91124a94aa03de44cd3f5c1e512e276aafb2a1f41e8c5f337d42ecef82",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-bc77b92cf0572db34f16881721f8db19",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-bc77b92cf0572db34f16881721f8db19",
        "root_review_id": "review-bc77b92cf0572db34f16881721f8db19",
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
      "joined_at": "2026-11-17T13:04:54.831Z",
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
          "fingerprint": "sha256:bb2fa3e5d45b41281bb7b95072c1b45ffcf5d5bc308a372e581ac9e1d81b4e54",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T13:05:49.179Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:bb2fa3e5d45b41281bb7b95072c1b45ffcf5d5bc308a372e581ac9e1d81b4e54"
    }
  },
  "record_id": "review-bc77b92cf0572db34f16881721f8db19",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-bc77b92cf0572db34f16881721f8db19",
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
  "startup_commit": "fb03ec8c197db1c5c4d41c81907466b66eba30c4",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "06d1c9703e2684cd56d3263c6551d8d0048120c3",
        "digest": "sha256:4065c91cc4fe50a48aa5a3d8cc4f557831d3f5cf310145961221c4789612e18b",
        "path": ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-execution-packet.md"
      },
      "author_response": {
        "digest": "sha256:a4785819e1e83d9a981e7ebf3ca96c6461be32a6f624aaee6aba486c29d2dac4",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-queue-packet/plan/2026-11-17-2026-11-17-368-queue-inclusive-execution-packet-review-bc77b92cf0572db34f16881721f8db19/review-bc77b92cf0572db34f16881721f8db19-author-response-1.md"
      },
      "commit": "5d5eb2876493aab63684da798230130ec8930f99",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:66cc24172ccfcb90a6ce3e38194c02882cd26246b228c9f1c3aafff5ee835876",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-queue-packet/plan/2026-11-17-2026-11-17-368-queue-inclusive-execution-packet-review-bc77b92cf0572db34f16881721f8db19/review-bc77b92cf0572db34f16881721f8db19-reviewer-response-1.md"
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
        "digest": "sha256:d82bd55eb972a1e47905b0ad36a11c028e55d2e021f1c43c5d429a88cc97d57e",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-queue-packet/plan/2026-11-17-2026-11-17-368-queue-inclusive-execution-packet-review-bc77b92cf0572db34f16881721f8db19/review-bc77b92cf0572db34f16881721f8db19-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
