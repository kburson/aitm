<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "6b881112d3a589ada6b74415a242aa56fa81d6a6",
      "commit": "f7928d15ace3a4949ce67c42da37ea7371e05892",
      "digest": "sha256:afc748d5a3f07ecd92be59c5866af3fc919548d79f338380b750790be8dfeeb2",
      "path": ".aitm/stories/001/138/design/pin-serial-baseline-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "15fc0bba8f532edad3fcb143213785a4d0f39e9a",
      "commit": "60e287c30b9c32339e4ba905b463dfb63278773a",
      "digest": "sha256:d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b",
      "path": ".aitm/stories/001/138/design/pin-serial-baseline-design.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/001/138/design/pin-serial-baseline-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-7ee3a258-5b1a-4329-8949-0865bee2a378",
      "claimed_at": "2026-11-10T18:48:09.624Z",
      "expires_at": "2026-11-11T02:48:09.624Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T18:48:09.624Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:2fb694d9ad80b4467c1bb5056516a998d517503f3ff8035c80ede39b6324374b"
    },
    {
      "claim_id": "claim-bb90c805-eba8-4700-9f49-89dca4728373",
      "claimed_at": "2026-11-10T18:50:59.611Z",
      "expires_at": "2026-11-11T02:50:59.611Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T18:50:59.611Z",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "60e287c30b9c32339e4ba905b463dfb63278773a",
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
            "fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-10T18:47:51.319Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:9958bcc1320b348ee832eac589098845bf3b63c5d582febdc0a9a45552cb4efa",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-207875068d6dee69f700fcbc2b3b4131",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-207875068d6dee69f700fcbc2b3b4131",
        "root_review_id": "review-207875068d6dee69f700fcbc2b3b4131",
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
          "fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T18:47:51.319Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
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
          "fingerprint": "sha256:2fb694d9ad80b4467c1bb5056516a998d517503f3ff8035c80ede39b6324374b",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T18:48:09.604Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:2fb694d9ad80b4467c1bb5056516a998d517503f3ff8035c80ede39b6324374b"
    }
  },
  "record_id": "review-207875068d6dee69f700fcbc2b3b4131",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-207875068d6dee69f700fcbc2b3b4131",
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
    "project_root_digest": "02dfee5b6dc15eb3a822b938e47a60ca29f341ec44317c75f8b94b0a1e5c02b5",
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
  "startup_commit": "f7928d15ace3a4949ce67c42da37ea7371e05892",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "15fc0bba8f532edad3fcb143213785a4d0f39e9a",
        "digest": "sha256:d080652606e1e177c4c79c5a9c17a98cdaf5ef8d38ce641f4b55ff89ac0efa0b",
        "path": ".aitm/stories/001/138/design/pin-serial-baseline-design.md"
      },
      "author_response": {
        "digest": "sha256:e96516ec2dd80a5ebde8d047e8f649859dfb5678ec354f3b468e91281167ca01",
        "path": ".aitm/stories/001/138/design/reviews/xpr-2026-11-10-leaf-design/native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-author-response-1.md"
      },
      "commit": "60e287c30b9c32339e4ba905b463dfb63278773a",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:6f92ed2ac6aca77db8d9d4f34a453181bbfb2a2391f4fce539257a6b5bf80929",
        "path": ".aitm/stories/001/138/design/reviews/xpr-2026-11-10-leaf-design/native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-reviewer-response-1.md"
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
        "digest": "sha256:b9753ad52c64f2d9c418d64c63868bc501b51a1fa41ce1f31ab22b1377d415c8",
        "path": ".aitm/stories/001/138/design/reviews/xpr-2026-11-10-leaf-design/native/spec/2026-11-10-pin-serial-baseline-design-review-207875068d6dee69f700fcbc2b3b4131/review-207875068d6dee69f700fcbc2b3b4131-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
