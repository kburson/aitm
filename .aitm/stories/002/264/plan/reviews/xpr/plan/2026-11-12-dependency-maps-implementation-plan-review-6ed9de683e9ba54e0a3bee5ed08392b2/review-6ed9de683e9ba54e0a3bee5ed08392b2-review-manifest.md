<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "8841c7ca0c0edf28613459ccd6038ab71bff758b",
      "commit": "f785e3d7f5f703fe5ddc9c100df5a081db1c392f",
      "digest": "sha256:fd559940fee27e8095da863a840d10a5d8d0ff2816ea8efd5c635ecc214c22ed",
      "path": ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "276e78a1df75a842ec515082cb511e1c49538b18",
      "commit": "869e0237f13630152fcdec138730398000b7c04d",
      "digest": "sha256:01d990bf16e400a6de2e56a5d88467b76c4aa3b56583920e913101f92e71aa5f",
      "path": ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md",
      "snapshot": null,
      "turn": 1
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
      "claim_id": "claim-7ecd527a-d897-4b3c-ad76-a2cfeb3455ce",
      "claimed_at": "2026-11-12T15:09:38.197Z",
      "expires_at": "2026-11-12T23:09:38.197Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-12T15:09:38.197Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:4f94a9ca3ce36df5862bd1e9007f2569c595c2bad97733e323283998eb0d7963"
    },
    {
      "claim_id": "claim-02e3a12d-46e0-4bbb-b768-025335f43552",
      "claimed_at": "2026-11-12T15:13:27.211Z",
      "expires_at": "2026-11-12T23:13:27.211Z",
      "host": "codex",
      "last_activity_at": "2026-11-12T15:13:27.211Z",
      "role": "author",
      "session_fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "869e0237f13630152fcdec138730398000b7c04d",
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
        "joined_at": "2026-11-12T15:09:07.046Z",
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
        "event_log_digest": "sha256:61512ecfd97eedc735976f974855d2d356b2beecb270ed44a8e1cb91bc1ff9e5",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-6ed9de683e9ba54e0a3bee5ed08392b2",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-6ed9de683e9ba54e0a3bee5ed08392b2",
        "root_review_id": "review-6ed9de683e9ba54e0a3bee5ed08392b2",
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
      "joined_at": "2026-11-12T15:09:07.046Z",
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
          "fingerprint": "sha256:4f94a9ca3ce36df5862bd1e9007f2569c595c2bad97733e323283998eb0d7963",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T15:09:38.164Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:4f94a9ca3ce36df5862bd1e9007f2569c595c2bad97733e323283998eb0d7963"
    }
  },
  "record_id": "review-6ed9de683e9ba54e0a3bee5ed08392b2",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-6ed9de683e9ba54e0a3bee5ed08392b2",
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
  "startup_commit": "f785e3d7f5f703fe5ddc9c100df5a081db1c392f",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "276e78a1df75a842ec515082cb511e1c49538b18",
        "digest": "sha256:01d990bf16e400a6de2e56a5d88467b76c4aa3b56583920e913101f92e71aa5f",
        "path": ".aitm/stories/002/264/plan/dependency-maps-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:e31ceed7b5c3927207ec6f0b98fd123d30cc56afe7221d4afafc94325b5c8313",
        "path": ".aitm/stories/002/264/plan/reviews/xpr/plan/2026-11-12-dependency-maps-implementation-plan-review-6ed9de683e9ba54e0a3bee5ed08392b2/review-6ed9de683e9ba54e0a3bee5ed08392b2-author-response-1.md"
      },
      "commit": "869e0237f13630152fcdec138730398000b7c04d",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004"
      ],
      "reviewer_response": {
        "digest": "sha256:e233e677b738eb01a62382821007f2cdd35c3b2646a73e20977017d7c156bca4",
        "path": ".aitm/stories/002/264/plan/reviews/xpr/plan/2026-11-12-dependency-maps-implementation-plan-review-6ed9de683e9ba54e0a3bee5ed08392b2/review-6ed9de683e9ba54e0a3bee5ed08392b2-reviewer-response-1.md"
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
        "digest": "sha256:f74c00f4822d8328dac4fff2be8b6bd67abcd31e0f7ca5d13c2a4295c2d83228",
        "path": ".aitm/stories/002/264/plan/reviews/xpr/plan/2026-11-12-dependency-maps-implementation-plan-review-6ed9de683e9ba54e0a3bee5ed08392b2/review-6ed9de683e9ba54e0a3bee5ed08392b2-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
