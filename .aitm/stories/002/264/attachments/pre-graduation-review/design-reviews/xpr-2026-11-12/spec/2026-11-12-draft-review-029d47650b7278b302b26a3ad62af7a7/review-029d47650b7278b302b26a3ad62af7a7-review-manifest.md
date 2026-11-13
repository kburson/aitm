<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "f3ed42891b5c4fca7322414c46f4c612f586565b",
      "commit": "ad20083299fc1ea449b39e8d5a3024580e144944",
      "digest": "sha256:f2ce1a217e971ccbeff3ad119725c672a8b8c0af2a104d6d61c6a26ce8726030",
      "path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "d3931f75947f240b124716ad861979c42c1f06e9",
      "commit": "6d2f75a8aa85c81a14938a15b9d463002f40d675",
      "digest": "sha256:0adca6f338bbda55f98b17708bcd6d932b0ca87b6ca6965a0994bc2151e78abd",
      "path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-ccd1cad3-162a-469b-b1bd-ee462ccf1867",
      "claimed_at": "2026-11-12T14:35:17.058Z",
      "expires_at": "2026-11-12T22:35:17.058Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-12T14:35:17.058Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:0f6473fbeb7b0ce4f3edbec042401b9bb4b6d72e6043769973af5539525d3685"
    },
    {
      "claim_id": "claim-6522f228-e41d-44c8-ae84-60e553021706",
      "claimed_at": "2026-11-12T14:37:49.738Z",
      "expires_at": "2026-11-12T22:37:49.738Z",
      "host": "codex",
      "last_activity_at": "2026-11-12T14:37:49.738Z",
      "role": "author",
      "session_fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "6d2f75a8aa85c81a14938a15b9d463002f40d675",
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
            "fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-12T14:34:45.378Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:21f9e887854b2d5d34ac68d5773cd4df6f8f9009badfdfa5f9b338d705336d8a",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-029d47650b7278b302b26a3ad62af7a7",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-029d47650b7278b302b26a3ad62af7a7",
        "root_review_id": "review-029d47650b7278b302b26a3ad62af7a7",
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
          "fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T14:34:45.378Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
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
          "fingerprint": "sha256:0f6473fbeb7b0ce4f3edbec042401b9bb4b6d72e6043769973af5539525d3685",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T14:35:17.022Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:0f6473fbeb7b0ce4f3edbec042401b9bb4b6d72e6043769973af5539525d3685"
    }
  },
  "record_id": "review-029d47650b7278b302b26a3ad62af7a7",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-029d47650b7278b302b26a3ad62af7a7",
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
    "project_root_digest": "62e02a251fcd52362468d110331f401b5aae10588c7335306b322db20353fc9d",
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
  "startup_commit": "ad20083299fc1ea449b39e8d5a3024580e144944",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "d3931f75947f240b124716ad861979c42c1f06e9",
        "digest": "sha256:0adca6f338bbda55f98b17708bcd6d932b0ca87b6ca6965a0994bc2151e78abd",
        "path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/draft.md"
      },
      "author_response": {
        "digest": "sha256:6932eb1dbdaf3015e5bdc52280bfd6a53c619909e85641b45bce9945f6a2d03d",
        "path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/design-reviews/xpr-2026-11-12/spec/2026-11-12-draft-review-029d47650b7278b302b26a3ad62af7a7/review-029d47650b7278b302b26a3ad62af7a7-author-response-1.md"
      },
      "commit": "6d2f75a8aa85c81a14938a15b9d463002f40d675",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004",
        "R1-F005"
      ],
      "reviewer_response": {
        "digest": "sha256:238535ebc2e122e2a7de396647c22c867c94b9c5b3401bbff9c322e8b42d9984",
        "path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/design-reviews/xpr-2026-11-12/spec/2026-11-12-draft-review-029d47650b7278b302b26a3ad62af7a7/review-029d47650b7278b302b26a3ad62af7a7-reviewer-response-1.md"
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
        "digest": "sha256:4fcb93b8676f09db678a4f2775d497d97ccb17e50aa7c35f48a66de9b32dccc8",
        "path": ".aitm/drafts/2026-11/20261112-0820-epic-dependency-maps/design-reviews/xpr-2026-11-12/spec/2026-11-12-draft-review-029d47650b7278b302b26a3ad62af7a7/review-029d47650b7278b302b26a3ad62af7a7-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
