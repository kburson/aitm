<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "8bae4d50b334eccf4f2ae93f798f0f64f12b25e0",
      "commit": "6b7edfc7782c600fc805f97387269e4f17968333",
      "digest": "sha256:e460f722a7398baff7aecff2a29f63c7e69c8b996338c28464780cdde9e84994",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "b39329afa80d4b5800b0e53ee84c3d76a68127b1",
      "commit": "7035ab5d25e0ce724d595a3abb7a55b1da51b0f2",
      "digest": "sha256:14f2576466bf4362c969f2099762957f485aa82495ae90b92d52cafd266fca41",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "10b46bdecd81653bce3d0e2576deae1ef3cdd0db",
      "commit": "9a061ba4c83206c3efc2861076bff487dea4449e",
      "digest": "sha256:555615f844fe5f535016e3da41bbbe81ffca4079c5d054d62cb62050d22392ce",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md",
      "snapshot": null,
      "turn": 2
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-0e1eebbd-9d29-49ca-a383-b07048b38615",
      "claimed_at": "2026-11-17T05:52:31.396Z",
      "expires_at": "2026-11-17T13:52:31.396Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T05:52:31.396Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:798081e6024e566a3c838afa796a5d1589eec2b43d480ae37902c4d6555493c0"
    },
    {
      "claim_id": "claim-a92b9ecb-b946-4bb8-a5dd-cebe381ca49b",
      "claimed_at": "2026-11-17T05:56:30.037Z",
      "expires_at": "2026-11-17T13:56:30.037Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T05:56:30.037Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "9a061ba4c83206c3efc2861076bff487dea4449e",
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
        "joined_at": "2026-11-17T05:51:35.331Z",
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
        "event_log_digest": "sha256:0fd816238dfddf48ad35949b504a70168e3813cdee42a2ac1f37cdb14ed10d60",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-dabe24b06b8f23586f5a2582c5d60b9b",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-dabe24b06b8f23586f5a2582c5d60b9b",
        "root_review_id": "review-dabe24b06b8f23586f5a2582c5d60b9b",
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
      "joined_at": "2026-11-17T05:51:35.331Z",
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
          "fingerprint": "sha256:798081e6024e566a3c838afa796a5d1589eec2b43d480ae37902c4d6555493c0",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T05:52:31.375Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:798081e6024e566a3c838afa796a5d1589eec2b43d480ae37902c4d6555493c0"
    }
  },
  "record_id": "review-dabe24b06b8f23586f5a2582c5d60b9b",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-dabe24b06b8f23586f5a2582c5d60b9b",
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
  "startup_commit": "6b7edfc7782c600fc805f97387269e4f17968333",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "b39329afa80d4b5800b0e53ee84c3d76a68127b1",
        "digest": "sha256:14f2576466bf4362c969f2099762957f485aa82495ae90b92d52cafd266fca41",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md"
      },
      "author_response": {
        "digest": "sha256:b5749cf6b86c469de4de2452a3d469792320a65f6267c00cdc82a3854abed6e5",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-discovery/plan/2026-11-17-2026-11-16-368-hosted-discovery-retry-packet-review-dabe24b06b8f23586f5a2582c5d60b9b/review-dabe24b06b8f23586f5a2582c5d60b9b-author-response-1.md"
      },
      "commit": "7035ab5d25e0ce724d595a3abb7a55b1da51b0f2",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:0cfeffd543bc53ac62cbb82659ef033649680c85dcbf01e3cdb24dbabfd89ee8",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-discovery/plan/2026-11-17-2026-11-16-368-hosted-discovery-retry-packet-review-dabe24b06b8f23586f5a2582c5d60b9b/review-dabe24b06b8f23586f5a2582c5d60b9b-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "10b46bdecd81653bce3d0e2576deae1ef3cdd0db",
        "digest": "sha256:555615f844fe5f535016e3da41bbbe81ffca4079c5d054d62cb62050d22392ce",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md"
      },
      "author_response": {
        "digest": "sha256:62fdaf8ef66d961d1a562b73cc2239cf69ca88821c54353df486ce1741f8d5e0",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-discovery/plan/2026-11-17-2026-11-16-368-hosted-discovery-retry-packet-review-dabe24b06b8f23586f5a2582c5d60b9b/review-dabe24b06b8f23586f5a2582c5d60b9b-author-response-2.md"
      },
      "commit": "9a061ba4c83206c3efc2861076bff487dea4449e",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:c54508762b84f434a92624cf82d9d539bca8c778bbeb11a8941f1eb7ea57f75c",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-discovery/plan/2026-11-17-2026-11-16-368-hosted-discovery-retry-packet-review-dabe24b06b8f23586f5a2582c5d60b9b/review-dabe24b06b8f23586f5a2582c5d60b9b-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    },
    {
      "artifact": null,
      "author_response": null,
      "commit": null,
      "decision": "accepted",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:82bc8ffdbde7e397185461eb0f11a4f5f9661ac11e6407e1ea6dffe796cc845b",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-discovery/plan/2026-11-17-2026-11-16-368-hosted-discovery-retry-packet-review-dabe24b06b8f23586f5a2582c5d60b9b/review-dabe24b06b8f23586f5a2582c5d60b9b-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
