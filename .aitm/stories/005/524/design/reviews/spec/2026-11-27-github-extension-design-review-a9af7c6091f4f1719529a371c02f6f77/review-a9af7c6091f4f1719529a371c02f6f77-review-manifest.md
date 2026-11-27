<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "e4e12d87bab444496df675abf41d410b63eb6fa5",
      "commit": "8862808e2dd2062df1c0d2e156e6711c2dbaabbb",
      "digest": "sha256:bce3087c1067ca38c1f25c7c98486c5934b4eb4fff3048fcf5eee75e99cf547b",
      "path": ".aitm/stories/005/524/design/github-extension-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "af55b56f14fc648e3a087c403cc3f662beeb8c7d",
      "commit": "ec9d4443c6644d3c12b1ff9a3af81b6924257ade",
      "digest": "sha256:4f609ef4c63fec821bae5417f6299068a170fea508db4e787af5750ed465288b",
      "path": ".aitm/stories/005/524/design/github-extension-design.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "f88d8caa1c9e1cbc353a127e60e9bd6691f15f88",
      "commit": "3764586c42c940ef3950e3ee95064fa22a9e5f8e",
      "digest": "sha256:dd7b26b28322ebd03211717d0e5f7b4bd46c5f79eebe219a7a881383768d113d",
      "path": ".aitm/stories/005/524/design/github-extension-design.md",
      "snapshot": null,
      "turn": 2
    }
  ],
  "artifact_path": ".aitm/stories/005/524/design/github-extension-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-97bfe34a-6ed9-404e-85a8-1b70fec3dbaa",
      "claimed_at": "2026-11-27T06:13:28.627Z",
      "expires_at": "2026-11-27T14:13:28.627Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-27T06:13:28.627Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:0c13cad915596f8573c341829b1f37504efbaedb00fd577eb7fafa121ffe23b5"
    },
    {
      "claim_id": "claim-4485ab1e-068a-4cc3-8b8e-b7473d6e4dc6",
      "claimed_at": "2026-11-27T06:15:17.716Z",
      "expires_at": "2026-11-27T14:15:17.716Z",
      "host": "codex",
      "last_activity_at": "2026-11-27T06:15:17.716Z",
      "role": "author",
      "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "3764586c42c940ef3950e3ee95064fa22a9e5f8e",
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
            "requested_id": "gpt-6.2-sol",
            "source": "launch-request"
          },
          "session": {
            "assurance": "declared",
            "fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-27T06:12:53.106Z",
        "model_display": "gpt-6.2-sol",
        "model_id": "gpt-6.2-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:51d984f6f410bd35cc5c1c970e14e3b9b28c651a7bf037fe30c42c854750188b",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-a9af7c6091f4f1719529a371c02f6f77",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-a9af7c6091f4f1719529a371c02f6f77",
        "root_review_id": "review-a9af7c6091f4f1719529a371c02f6f77",
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
          "requested_id": "gpt-6.2-sol",
          "source": "launch-request"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-27T06:12:53.106Z",
      "model_display": "gpt-6.2-sol",
      "model_id": "gpt-6.2-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:1918137c8506c6a045c17ba1bd9406968a6f9eee76d71a87ad9966b7592223a8"
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
          "fingerprint": "sha256:0c13cad915596f8573c341829b1f37504efbaedb00fd577eb7fafa121ffe23b5",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-27T06:13:28.603Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:0c13cad915596f8573c341829b1f37504efbaedb00fd577eb7fafa121ffe23b5"
    }
  },
  "record_id": "review-a9af7c6091f4f1719529a371c02f6f77",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-a9af7c6091f4f1719529a371c02f6f77",
  "runtime": {
    "adapter_version": "1.0.0",
    "author": {
      "effort": "medium",
      "host": "codex",
      "model_display": "gpt-6.2-sol",
      "model_id": "gpt-6.2-sol",
      "provider": "openai"
    },
    "classification": "XPR",
    "ownership": "broker",
    "project_root_digest": "a53628967e9bcd74e62648bf7f1a25cf4cc5df6f1fe6c7944a36612ccecdcb54",
    "reviewer": {
      "effort": "medium",
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
  "startup_commit": "8862808e2dd2062df1c0d2e156e6711c2dbaabbb",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "af55b56f14fc648e3a087c403cc3f662beeb8c7d",
        "digest": "sha256:4f609ef4c63fec821bae5417f6299068a170fea508db4e787af5750ed465288b",
        "path": ".aitm/stories/005/524/design/github-extension-design.md"
      },
      "author_response": {
        "digest": "sha256:00fb132feaac4b67f29bc32860e9b0b57b82e66eea29d3d4c377061c285b6c86",
        "path": ".aitm/stories/005/524/design/reviews/spec/2026-11-27-github-extension-design-review-a9af7c6091f4f1719529a371c02f6f77/review-a9af7c6091f4f1719529a371c02f6f77-author-response-1.md"
      },
      "commit": "ec9d4443c6644d3c12b1ff9a3af81b6924257ade",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004",
        "R1-F005",
        "R1-F006"
      ],
      "reviewer_response": {
        "digest": "sha256:32fd2ff664c51f83e8b94303eb592c9ffc6a79ec799be825044e2cc7774bf877",
        "path": ".aitm/stories/005/524/design/reviews/spec/2026-11-27-github-extension-design-review-a9af7c6091f4f1719529a371c02f6f77/review-a9af7c6091f4f1719529a371c02f6f77-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "f88d8caa1c9e1cbc353a127e60e9bd6691f15f88",
        "digest": "sha256:dd7b26b28322ebd03211717d0e5f7b4bd46c5f79eebe219a7a881383768d113d",
        "path": ".aitm/stories/005/524/design/github-extension-design.md"
      },
      "author_response": {
        "digest": "sha256:ded80b6a0b773fb57ef716037963735b26cdd89f858697130c02f25512f2ff73",
        "path": ".aitm/stories/005/524/design/reviews/spec/2026-11-27-github-extension-design-review-a9af7c6091f4f1719529a371c02f6f77/review-a9af7c6091f4f1719529a371c02f6f77-author-response-2.md"
      },
      "commit": "3764586c42c940ef3950e3ee95064fa22a9e5f8e",
      "decision": "revisions-requested",
      "finding_ids": [
        "R2-F001"
      ],
      "reviewer_response": {
        "digest": "sha256:eb2c82f9fa874cca631479d56d535b44ac3b83933deefb11962bceef3a933e89",
        "path": ".aitm/stories/005/524/design/reviews/spec/2026-11-27-github-extension-design-review-a9af7c6091f4f1719529a371c02f6f77/review-a9af7c6091f4f1719529a371c02f6f77-reviewer-response-2.md"
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
        "digest": "sha256:81cd76b8a3fd77b2ba24321469e94fbfc806b0a886de624b5e7877760b6726f2",
        "path": ".aitm/stories/005/524/design/reviews/spec/2026-11-27-github-extension-design-review-a9af7c6091f4f1719529a371c02f6f77/review-a9af7c6091f4f1719529a371c02f6f77-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
