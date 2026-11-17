<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "7ac282bcd78705458093f3193a7070d4bd2ffc6b",
      "commit": "b70e8211591ba243f858a56e1e57f1f38c67555b",
      "digest": "sha256:4ed0f816af1dc9635f4b347a917d44561c949e0425f71f154b6245699b88d6db",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-protected-local-observation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "e4bca8ad88a079211e63b168b9bad4fe2b5f769b",
      "commit": "ca1f08c723f47c39edc5016d99e0121c84f3dd80",
      "digest": "sha256:f4ed0b50d49da73ed5b4f541a26ee4e2d4b00cb2e01a1d20db2182691c7d346a",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-protected-local-observation-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-protected-local-observation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-867bd64c-66b6-492d-9c4d-daf6d5707709",
      "claimed_at": "2026-11-17T01:06:47.524Z",
      "expires_at": "2026-11-17T09:06:47.524Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T01:06:47.524Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:cd7588a405e04feb723306cd5b5d92d8af1cd6b4f9b6efd6e5e3710a751b8810"
    },
    {
      "claim_id": "claim-1f9794b1-d9dd-45a0-89a7-19aa13ce2eab",
      "claimed_at": "2026-11-17T01:08:38.075Z",
      "expires_at": "2026-11-17T09:08:38.075Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T01:08:38.075Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "ca1f08c723f47c39edc5016d99e0121c84f3dd80",
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
        "joined_at": "2026-11-17T01:06:10.359Z",
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
        "event_log_digest": "sha256:7b476af9a0e6f9d010571912e42981848d3335493004655342d7f5fb9d07f353",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-313cdd3310f5b10187ba4f4c97d28a27",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-313cdd3310f5b10187ba4f4c97d28a27",
        "root_review_id": "review-313cdd3310f5b10187ba4f4c97d28a27",
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
      "joined_at": "2026-11-17T01:06:10.359Z",
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
          "fingerprint": "sha256:cd7588a405e04feb723306cd5b5d92d8af1cd6b4f9b6efd6e5e3710a751b8810",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T01:06:47.486Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:cd7588a405e04feb723306cd5b5d92d8af1cd6b4f9b6efd6e5e3710a751b8810"
    }
  },
  "record_id": "review-313cdd3310f5b10187ba4f4c97d28a27",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-313cdd3310f5b10187ba4f4c97d28a27",
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
  "startup_commit": "b70e8211591ba243f858a56e1e57f1f38c67555b",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "e4bca8ad88a079211e63b168b9bad4fe2b5f769b",
        "digest": "sha256:f4ed0b50d49da73ed5b4f541a26ee4e2d4b00cb2e01a1d20db2182691c7d346a",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-protected-local-observation-plan.md"
      },
      "author_response": {
        "digest": "sha256:1c3f23123d38820a6cdd4e716a112269ab353b5e37ba747678e1f73b72fb7086",
        "path": ".aitm/stories/003/368/plan/reviews/plan/2026-11-17-2026-11-16-368-protected-local-observation-plan-review-313cdd3310f5b10187ba4f4c97d28a27/review-313cdd3310f5b10187ba4f4c97d28a27-author-response-1.md"
      },
      "commit": "ca1f08c723f47c39edc5016d99e0121c84f3dd80",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001"
      ],
      "reviewer_response": {
        "digest": "sha256:9e906fe836498d09a625a316e076d53f25cf4ab2d819e6a26bedd8c3b1d0e034",
        "path": ".aitm/stories/003/368/plan/reviews/plan/2026-11-17-2026-11-16-368-protected-local-observation-plan-review-313cdd3310f5b10187ba4f4c97d28a27/review-313cdd3310f5b10187ba4f4c97d28a27-reviewer-response-1.md"
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
        "digest": "sha256:97d3213c1b27dc5262882b1de8aad1aa7c068bf3f9533b5fd78593a19a5f1df7",
        "path": ".aitm/stories/003/368/plan/reviews/plan/2026-11-17-2026-11-16-368-protected-local-observation-plan-review-313cdd3310f5b10187ba4f4c97d28a27/review-313cdd3310f5b10187ba4f4c97d28a27-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
