<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "06aabce1e95b449363555dc3dad4ce3a368ec7bb",
      "commit": "d5c1413a0658f904de7ed921bec872797a376f15",
      "digest": "sha256:f8d229b076947ac00fae768ea4f0df566ecabb5e74fae50ce3c1192388724ddf",
      "path": ".aitm/stories/002/264/design/dependency-maps.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "cffa70dc31c66be92e2a49935cd0c36bf2fa4997",
      "commit": "e63ab450a9e79f361ed7fc15169e28a9015a5b91",
      "digest": "sha256:50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7",
      "path": ".aitm/stories/002/264/design/dependency-maps.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/002/264/design/dependency-maps.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-56ed5467-e1f2-4a84-99b7-498780ae0ac2",
      "claimed_at": "2026-11-12T15:03:40.842Z",
      "expires_at": "2026-11-12T23:03:40.842Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-12T15:03:40.842Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:2d641c6d7af179cf4dd5a85a3bdc8bfac47ffaf80a900a255d16eb349a917115"
    },
    {
      "claim_id": "claim-d8072f58-6d8b-4de0-8bf3-bf7009c2a566",
      "claimed_at": "2026-11-12T15:06:06.243Z",
      "expires_at": "2026-11-12T23:06:06.243Z",
      "host": "codex",
      "last_activity_at": "2026-11-12T15:06:06.243Z",
      "role": "author",
      "session_fingerprint": "sha256:31447649ec74b9afd5a1eadc6de73b6bdd1c59d013494728d39a79ab68e4eed0"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "e63ab450a9e79f361ed7fc15169e28a9015a5b91",
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
        "joined_at": "2026-11-12T15:03:08.076Z",
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
        "event_log_digest": "sha256:053ac81a5e7e65070c3bdf0e1a717bae021d4e0acc60735fd03f0bd6ca236aeb",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-93e744c9779ee4cd9f592c59ba00364a",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-93e744c9779ee4cd9f592c59ba00364a",
        "root_review_id": "review-93e744c9779ee4cd9f592c59ba00364a",
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
      "joined_at": "2026-11-12T15:03:08.076Z",
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
          "fingerprint": "sha256:2d641c6d7af179cf4dd5a85a3bdc8bfac47ffaf80a900a255d16eb349a917115",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-12T15:03:40.810Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:2d641c6d7af179cf4dd5a85a3bdc8bfac47ffaf80a900a255d16eb349a917115"
    }
  },
  "record_id": "review-93e744c9779ee4cd9f592c59ba00364a",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-93e744c9779ee4cd9f592c59ba00364a",
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
  "startup_commit": "d5c1413a0658f904de7ed921bec872797a376f15",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "cffa70dc31c66be92e2a49935cd0c36bf2fa4997",
        "digest": "sha256:50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7",
        "path": ".aitm/stories/002/264/design/dependency-maps.md"
      },
      "author_response": {
        "digest": "sha256:897745373a9933b2361c36101a785c699f38495b23507710c5e060df6a34506c",
        "path": ".aitm/stories/002/264/design/reviews/xpr/spec/2026-11-12-dependency-maps-review-93e744c9779ee4cd9f592c59ba00364a/review-93e744c9779ee4cd9f592c59ba00364a-author-response-1.md"
      },
      "commit": "e63ab450a9e79f361ed7fc15169e28a9015a5b91",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001"
      ],
      "reviewer_response": {
        "digest": "sha256:ef9e122a9694d9b17554a77a6669803073ef7802ae76dfab50a229d20fdd2785",
        "path": ".aitm/stories/002/264/design/reviews/xpr/spec/2026-11-12-dependency-maps-review-93e744c9779ee4cd9f592c59ba00364a/review-93e744c9779ee4cd9f592c59ba00364a-reviewer-response-1.md"
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
        "digest": "sha256:113384f7728ab3ae7565644476b83327a0d847d5dd606decbfdb628097bfcef8",
        "path": ".aitm/stories/002/264/design/reviews/xpr/spec/2026-11-12-dependency-maps-review-93e744c9779ee4cd9f592c59ba00364a/review-93e744c9779ee4cd9f592c59ba00364a-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
