<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "913cf7e4702c87f79f37ef4e8e9b2bb002bf9396",
      "commit": "e6411995f65df61da29fa737bcfcfa722a8a9265",
      "digest": "sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de",
      "path": ".aitm/stories/000/83/design/usage-capture-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "a8deae9f23ca1c78a62d3c5c8544b7d3f24266cd",
      "commit": "670ce2fbe3e4b3752c38cead1b9c49283d54d591",
      "digest": "sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee",
      "path": ".aitm/stories/000/83/design/usage-capture-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/000/83/design/usage-capture-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-a3111f15-b6b3-4c6f-b8f9-e61bc328a7f7",
      "claimed_at": "2026-11-09T14:21:04.858Z",
      "expires_at": "2026-11-09T22:21:04.858Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T14:21:04.858Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:d152a032112c1f0a4b7f47ca982a1df6a355843f086c6e3f1eb3b8d62d7a81a9"
    },
    {
      "claim_id": "claim-b30c09b6-c93b-4a93-a062-2713e6bd59e4",
      "claimed_at": "2026-11-09T14:22:59.391Z",
      "expires_at": "2026-11-09T22:22:59.391Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T14:22:59.391Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "670ce2fbe3e4b3752c38cead1b9c49283d54d591",
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
        "joined_at": "2026-11-09T14:20:35.970Z",
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
        "event_log_digest": "sha256:59cbad78f05f825dfbba6151ac85114e4bfc90f54f5d1b7c62bab6c23f26b5ba",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-9a11494429336f06db1d427236d5aa0e",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-9a11494429336f06db1d427236d5aa0e",
        "root_review_id": "review-9a11494429336f06db1d427236d5aa0e",
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
      "joined_at": "2026-11-09T14:20:35.970Z",
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
          "fingerprint": "sha256:d152a032112c1f0a4b7f47ca982a1df6a355843f086c6e3f1eb3b8d62d7a81a9",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T14:21:04.838Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:d152a032112c1f0a4b7f47ca982a1df6a355843f086c6e3f1eb3b8d62d7a81a9"
    }
  },
  "record_id": "review-9a11494429336f06db1d427236d5aa0e",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-9a11494429336f06db1d427236d5aa0e",
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
    "project_root_digest": "e9c69f8fda423c009d3ad44f7280976207b26e16bafc44246abea9fb95d93125",
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
  "startup_commit": "e6411995f65df61da29fa737bcfcfa722a8a9265",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "a8deae9f23ca1c78a62d3c5c8544b7d3f24266cd",
        "digest": "sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee",
        "path": ".aitm/stories/000/83/design/usage-capture-design.md"
      },
      "author_response": {
        "digest": "sha256:a3cc3790b75b789dd5f5c3ddb15c2c7b1692bd05d71e4b1a4dbb410c28a23800",
        "path": ".aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-author-response-1.md"
      },
      "commit": "670ce2fbe3e4b3752c38cead1b9c49283d54d591",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:5456f93b7fe3fbfbb848614e7a9037444677d8504a6f22014d0290f3f96d8ac8",
        "path": ".aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-response-1.md"
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
        "digest": "sha256:4241dec77a481849e03a46cbc75e9d5c85cb5f0a0b841ddf164278ff16894689",
        "path": ".aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
