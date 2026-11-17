<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "d0ec23bc2c34fd560fcfe304bd672af9a8843ee8",
      "commit": "5eb4be712529b3e0fde2657f0c0b06e0cbfcf65e",
      "digest": "sha256:effb021737e2324a2ccb78f6d00241de06fcdbd858be3f890be049d1dcddcf2d",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-preflight-packet.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "3fd20ff0d1a5b475ed849a7a27da901490e17a36",
      "commit": "67ef733fb684869cc999bb1c7630d46d07ef3216",
      "digest": "sha256:84cb2afd4378937b42d789f46e775419d44a186bce96a732cd14eb2b6313493b",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-preflight-packet.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-preflight-packet.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-6528855a-4091-42d5-a458-4885670a9bc0",
      "claimed_at": "2026-11-17T05:06:03.539Z",
      "expires_at": "2026-11-17T13:06:03.539Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T05:06:03.539Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:102ec2fea75b4ebd4fe2a760a8281449fd5629f4d85c1c51dc4bdf17be118590"
    },
    {
      "claim_id": "claim-aff0e170-9e7a-47d9-9f49-d8430520c0b5",
      "claimed_at": "2026-11-17T05:12:14.722Z",
      "expires_at": "2026-11-17T13:12:14.722Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T05:12:14.722Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "67ef733fb684869cc999bb1c7630d46d07ef3216",
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
        "joined_at": "2026-11-17T05:05:25.943Z",
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
        "event_log_digest": "sha256:03c4431dc538648c4ee9fb2a2094197e74a59cfa157daf46cde7f57147a47f08",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-c06f8b4bf4d27f7e06d1d22d7f382577",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-c06f8b4bf4d27f7e06d1d22d7f382577",
        "root_review_id": "review-c06f8b4bf4d27f7e06d1d22d7f382577",
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
      "joined_at": "2026-11-17T05:05:25.943Z",
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
          "fingerprint": "sha256:102ec2fea75b4ebd4fe2a760a8281449fd5629f4d85c1c51dc4bdf17be118590",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T05:06:03.516Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:102ec2fea75b4ebd4fe2a760a8281449fd5629f4d85c1c51dc4bdf17be118590"
    }
  },
  "record_id": "review-c06f8b4bf4d27f7e06d1d22d7f382577",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-c06f8b4bf4d27f7e06d1d22d7f382577",
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
  "startup_commit": "5eb4be712529b3e0fde2657f0c0b06e0cbfcf65e",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "3fd20ff0d1a5b475ed849a7a27da901490e17a36",
        "digest": "sha256:84cb2afd4378937b42d789f46e775419d44a186bce96a732cd14eb2b6313493b",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-preflight-packet.md"
      },
      "author_response": {
        "digest": "sha256:d6063e02c7c64001c59b1218c9bf7d4cf6507e576447d51ccc0e74b890be1ac5",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-preflight/plan/2026-11-17-2026-11-16-368-hosted-preflight-packet-review-c06f8b4bf4d27f7e06d1d22d7f382577/review-c06f8b4bf4d27f7e06d1d22d7f382577-author-response-1.md"
      },
      "commit": "67ef733fb684869cc999bb1c7630d46d07ef3216",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:838c6e46860999c0fe26aa252cd06ec1cab1d555efbd84fea3cfd52ca91967bd",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-preflight/plan/2026-11-17-2026-11-16-368-hosted-preflight-packet-review-c06f8b4bf4d27f7e06d1d22d7f382577/review-c06f8b4bf4d27f7e06d1d22d7f382577-reviewer-response-1.md"
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
        "digest": "sha256:e5a396ca2f93e9e699080ab8849877ae4d0f9667965234f21f593cea2ab86407",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-preflight/plan/2026-11-17-2026-11-16-368-hosted-preflight-packet-review-c06f8b4bf4d27f7e06d1d22d7f382577/review-c06f8b4bf4d27f7e06d1d22d7f382577-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
