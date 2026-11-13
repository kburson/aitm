<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "24b9e278c548914d73c996a25143dc09f2a98161",
      "commit": "e9347ea43609adde86483b16d103c66df4fdf15e",
      "digest": "sha256:b82e504caa40e83ee3d7384bfd214678eb97aced688f06ec99b521c596dfd012",
      "path": ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    }
  ],
  "artifact_path": ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-b1163556-6bb6-485a-b2d5-968d58a3cb28",
      "claimed_at": "2026-11-12T15:18:42.764Z",
      "expires_at": "2026-11-12T23:18:42.764Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-12T15:18:42.764Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:512bef0fbe910931845325d44760f8e5b697c07b3e91a2ccd5136fb6394d87d2"
    },
    {
      "claim_id": "claim-2593afb5-33dc-41fa-bfa1-c7ffece1e8ba",
      "claimed_at": "2026-11-12T15:23:10.881Z",
      "expires_at": "2026-11-12T23:23:10.881Z",
      "host": "codex",
      "last_activity_at": "2026-11-12T15:23:10.881Z",
      "role": "author",
      "session_fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "e9347ea43609adde86483b16d103c66df4fdf15e",
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
        "joined_at": "2026-11-12T15:18:05.105Z",
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
        "event_log_digest": "sha256:abe33cfd2f5f90af2d7ef2fcd6e2af2c17056962d49ab7c418e61a881152c6f7",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-51ac63c23fa8c6be29d5f7e1f972cf91",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-51ac63c23fa8c6be29d5f7e1f972cf91",
        "root_review_id": "review-51ac63c23fa8c6be29d5f7e1f972cf91",
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
      "joined_at": "2026-11-12T15:18:05.105Z",
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
          "fingerprint": "sha256:512bef0fbe910931845325d44760f8e5b697c07b3e91a2ccd5136fb6394d87d2",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T15:18:42.731Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:512bef0fbe910931845325d44760f8e5b697c07b3e91a2ccd5136fb6394d87d2"
    }
  },
  "record_id": "review-51ac63c23fa8c6be29d5f7e1f972cf91",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-51ac63c23fa8c6be29d5f7e1f972cf91",
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
    "project_root_digest": "97f530bf25eb5471676eee8a96ca0c060dc76f0c6db806355696f0c70d9d2b31",
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
  "startup_commit": "e9347ea43609adde86483b16d103c66df4fdf15e",
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
        "digest": "sha256:74552b9b9c91e9bbed0fe6e5ed21b3a16cf29860e315d2782c3311f02b0e7681",
        "path": ".aitm/stories/002/264/plan/reviews/xpr-final/plan/2026-11-12-dependency-maps-implementation-plan-review-51ac63c23fa8c6be29d5f7e1f972cf91/review-51ac63c23fa8c6be29d5f7e1f972cf91-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    }
  ]
}
```
