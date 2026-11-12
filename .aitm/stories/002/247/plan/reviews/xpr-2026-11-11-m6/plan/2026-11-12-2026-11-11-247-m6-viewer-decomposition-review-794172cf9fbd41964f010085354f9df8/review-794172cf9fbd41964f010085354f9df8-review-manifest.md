<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "4d70079e6cd08c9c14495ed981860a274e0f082f",
      "commit": "996dae42effef6a6de6bb3879262a28013e899dd",
      "digest": "sha256:cfe9143eb81d25efe8b6b586a1f4242cc4218cfc30122ec134ea1e060e07000c",
      "path": ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "08f197f3492bbb3f7c799dc3c0cad814b603b578",
      "commit": "aa9f8a486c4510fa7568d60bfd6405ac0d0dae2e",
      "digest": "sha256:4be08e201c73d239ab2147ecd861000e7e0f1812a81f31b66fb1bc0bef514fd6",
      "path": ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-92ef709b-eb22-46c1-af48-39ffd681ca40",
      "claimed_at": "2026-11-12T00:44:08.606Z",
      "expires_at": "2026-11-12T08:44:08.606Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-12T00:44:08.606Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:a9ddb00c18bf95949c28df14c6e2ddb64131150db394d645b943157c0af3d18e"
    },
    {
      "claim_id": "claim-5d332960-5d39-44ec-b159-4f33a17bf224",
      "claimed_at": "2026-11-12T00:47:39.992Z",
      "expires_at": "2026-11-12T08:47:39.992Z",
      "host": "codex",
      "last_activity_at": "2026-11-12T00:47:39.992Z",
      "role": "author",
      "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "aa9f8a486c4510fa7568d60bfd6405ac0d0dae2e",
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
            "fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-12T00:43:26.661Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:b653a121dbb78a8e3ed472ca0d3fe69432083ad78e0d485cf4ce771e70add64d",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-794172cf9fbd41964f010085354f9df8",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-794172cf9fbd41964f010085354f9df8",
        "root_review_id": "review-794172cf9fbd41964f010085354f9df8",
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
          "fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T00:43:26.661Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:c1cbcb4fcd7a783ae196e3c00bcb80a1c4c8df5c4a0a48d8a37423b000b5533c"
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
          "fingerprint": "sha256:a9ddb00c18bf95949c28df14c6e2ddb64131150db394d645b943157c0af3d18e",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T00:44:08.587Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:a9ddb00c18bf95949c28df14c6e2ddb64131150db394d645b943157c0af3d18e"
    }
  },
  "record_id": "review-794172cf9fbd41964f010085354f9df8",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-794172cf9fbd41964f010085354f9df8",
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
    "project_root_digest": "c65beb3747bee1a09eb4be1e14faebdf17a47616d98ce11d87a6db8f2d46cdb4",
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
  "startup_commit": "996dae42effef6a6de6bb3879262a28013e899dd",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "08f197f3492bbb3f7c799dc3c0cad814b603b578",
        "digest": "sha256:4be08e201c73d239ab2147ecd861000e7e0f1812a81f31b66fb1bc0bef514fd6",
        "path": ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
      },
      "author_response": {
        "digest": "sha256:a318742b9a0f15fe48bc5c389568ee0f2ca4f8b0e0ec07f1e0f0f6d6f3d0662d",
        "path": ".aitm/stories/002/247/plan/reviews/xpr-2026-11-11-m6/plan/2026-11-12-2026-11-11-247-m6-viewer-decomposition-review-794172cf9fbd41964f010085354f9df8/review-794172cf9fbd41964f010085354f9df8-author-response-1.md"
      },
      "commit": "aa9f8a486c4510fa7568d60bfd6405ac0d0dae2e",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001"
      ],
      "reviewer_response": {
        "digest": "sha256:0b5d34bd71312da0f8c60b2cc1c13698886b4cddec499239037dd4325e4e06ef",
        "path": ".aitm/stories/002/247/plan/reviews/xpr-2026-11-11-m6/plan/2026-11-12-2026-11-11-247-m6-viewer-decomposition-review-794172cf9fbd41964f010085354f9df8/review-794172cf9fbd41964f010085354f9df8-reviewer-response-1.md"
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
        "digest": "sha256:d5d8c4028787c7b1fd463343a350a7c1a21e6acc80915cc358dea10619041320",
        "path": ".aitm/stories/002/247/plan/reviews/xpr-2026-11-11-m6/plan/2026-11-12-2026-11-11-247-m6-viewer-decomposition-review-794172cf9fbd41964f010085354f9df8/review-794172cf9fbd41964f010085354f9df8-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
