<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "894ae5cabd9c561c84f9ed28edcb7339cb23a985",
      "commit": "1eded398ddd7e718f544bfa3e78f651cc13dbb81",
      "digest": "sha256:162d4d2a95eec01adcb8181dadff2dd550b63282ee8ce85eb45fb0d9361b46da",
      "path": ".aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "4d7a8692b8acdd011c784ef8957b37f6d2b6b88e",
      "commit": "e3bc34118e735a1ca80e772a8d9379d7191918c2",
      "digest": "sha256:a6f7ef90668153eeb063d34b33162424409526021475eeed97dbf342b289c109",
      "path": ".aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-a37fd0d7-b464-4bbf-8178-2be95f9ce2e5",
      "claimed_at": "2026-11-16T12:55:58.896Z",
      "expires_at": "2026-11-16T20:55:58.896Z",
      "host": "grok",
      "last_activity_at": "2026-11-16T12:55:58.896Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:0c26620ccf192459c096abf761f4125c0e239c36725cd214d71437bf7a857592"
    },
    {
      "claim_id": "claim-b4d841c3-f573-47a1-96f6-539618e617d6",
      "claimed_at": "2026-11-16T13:07:01.995Z",
      "expires_at": "2026-11-16T21:07:01.995Z",
      "host": "codex",
      "last_activity_at": "2026-11-16T13:07:01.995Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "e3bc34118e735a1ca80e772a8d9379d7191918c2",
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
        "joined_at": "2026-11-16T12:53:55.956Z",
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
        "event_log_digest": "sha256:4f424d8b94db2f8ae95691863261510edd2422145b9e162d8b6d5749770fd6fc",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-c71d9bf99a30b80cea3e96ba9d9c8b9f",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-c71d9bf99a30b80cea3e96ba9d9c8b9f",
        "root_review_id": "review-c71d9bf99a30b80cea3e96ba9d9c8b9f",
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
      "joined_at": "2026-11-16T12:53:55.956Z",
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
          "declared_id": null,
          "observed_id": null,
          "requested_id": "grok-4.7",
          "source": "launch-request"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:0c26620ccf192459c096abf761f4125c0e239c36725cd214d71437bf7a857592",
          "source": "environment-declaration"
        }
      },
      "host": "grok",
      "identity_source": "declared",
      "joined_at": "2026-11-16T12:55:58.895Z",
      "model_display": "grok-4.7",
      "model_id": "grok-4.7",
      "provider": "xai",
      "role": "reviewer",
      "session_fingerprint": "sha256:0c26620ccf192459c096abf761f4125c0e239c36725cd214d71437bf7a857592"
    }
  },
  "record_id": "review-c71d9bf99a30b80cea3e96ba9d9c8b9f",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-c71d9bf99a30b80cea3e96ba9d9c8b9f",
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
      "host": "grok",
      "model_display": "grok-4.7",
      "model_id": "grok-4.7",
      "provider": "xai",
      "selector": "grok"
    },
    "schema": "ai-peer-review.runtime/v1",
    "transport_mode": "manual"
  },
  "schema": "ai-peer-review.manifest/v1",
  "startup_commit": "1eded398ddd7e718f544bfa3e78f651cc13dbb81",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "4d7a8692b8acdd011c784ef8957b37f6d2b6b88e",
        "digest": "sha256:a6f7ef90668153eeb063d34b33162424409526021475eeed97dbf342b289c109",
        "path": ".aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:2f99c45c76704db68e2c0a5d922f5ba4a25d8156c15d7b1dc99760edb8f0d85b",
        "path": ".aitm/stories/003/344/plan/reviews/plan/2026-11-16-test-impact-analysis-implementation-plan-review-c71d9bf99a30b80cea3e96ba9d9c8b9f/review-c71d9bf99a30b80cea3e96ba9d9c8b9f-author-response-1.md"
      },
      "commit": "e3bc34118e735a1ca80e772a8d9379d7191918c2",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002"
      ],
      "reviewer_response": {
        "digest": "sha256:5736ff9ed80bceb97dc5b86b64728b855ffdd5d15401f84c5122018d792b6e9b",
        "path": ".aitm/stories/003/344/plan/reviews/plan/2026-11-16-test-impact-analysis-implementation-plan-review-c71d9bf99a30b80cea3e96ba9d9c8b9f/review-c71d9bf99a30b80cea3e96ba9d9c8b9f-reviewer-response-1.md"
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
        "digest": "sha256:cbaa82903ba5ab2c95edc6198948e86f9c6b9e8a41a1fd1885909ec7e6079bb2",
        "path": ".aitm/stories/003/344/plan/reviews/plan/2026-11-16-test-impact-analysis-implementation-plan-review-c71d9bf99a30b80cea3e96ba9d9c8b9f/review-c71d9bf99a30b80cea3e96ba9d9c8b9f-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
