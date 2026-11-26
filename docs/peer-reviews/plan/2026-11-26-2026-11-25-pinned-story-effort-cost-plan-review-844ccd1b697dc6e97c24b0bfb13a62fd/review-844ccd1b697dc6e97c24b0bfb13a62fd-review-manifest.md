<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "04d582a033e5a75cfc433aaf08e9334faeec7b4d",
      "commit": "e907b571dd34d68ac1017d60cbccead05ba736c9",
      "digest": "sha256:426a7c83a6e5ad14109bbf0688798e815819af379e5c4b041b10fd01002980f1",
      "path": ".aitm/stories/004/458/plan/2026-11-25-pinned-story-effort-cost-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "c4ebd79ea8cef9be0ad542db4fb66a6f7e406934",
      "commit": "b1f20b4deea9277b286aa83dd0e7f3eb055065f0",
      "digest": "sha256:5dae7d5346edbd8691658e772508a5672e9f202c332aaafec440686f33afd856",
      "path": ".aitm/stories/004/458/plan/2026-11-25-pinned-story-effort-cost-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/004/458/plan/2026-11-25-pinned-story-effort-cost-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-d7e9dcba-933e-427e-8858-37473f57b8db",
      "claimed_at": "2026-11-26T02:14:04.512Z",
      "expires_at": "2026-11-26T10:14:04.512Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-26T02:14:04.512Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:89dc554194234ba6f6f2cbf6b7c156235bf15d2013dacdae795df1c601977685"
    },
    {
      "claim_id": "claim-2a467498-67ee-4ce4-a1cd-ff6dd9a02789",
      "claimed_at": "2026-11-26T02:14:32.957Z",
      "expires_at": "2026-11-26T10:14:32.957Z",
      "host": "codex",
      "last_activity_at": "2026-11-26T02:14:32.957Z",
      "role": "author",
      "session_fingerprint": "sha256:0a2c23fc828401b217a0141c886d3d9e315252adbc36dad83cb120f023ec2fdf"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "b1f20b4deea9277b286aa83dd0e7f3eb055065f0",
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
            "fingerprint": "sha256:0a2c23fc828401b217a0141c886d3d9e315252adbc36dad83cb120f023ec2fdf",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-26T02:13:26.179Z",
        "model_display": "gpt-6.2-sol",
        "model_id": "gpt-6.2-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:0a2c23fc828401b217a0141c886d3d9e315252adbc36dad83cb120f023ec2fdf"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:4b42863bccdb3e3e0399a6e140f17e41fe1d82703abf81abd722b9ea03612bef",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-844ccd1b697dc6e97c24b0bfb13a62fd",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-844ccd1b697dc6e97c24b0bfb13a62fd",
        "root_review_id": "review-844ccd1b697dc6e97c24b0bfb13a62fd",
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
          "fingerprint": "sha256:0a2c23fc828401b217a0141c886d3d9e315252adbc36dad83cb120f023ec2fdf",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-26T02:13:26.179Z",
      "model_display": "gpt-6.2-sol",
      "model_id": "gpt-6.2-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:0a2c23fc828401b217a0141c886d3d9e315252adbc36dad83cb120f023ec2fdf"
    },
    "reviewer": {
      "evidence": {
        "model": {
          "assurance": "declared",
          "conflict": false,
          "declared_id": "claude-sonnet-5-5",
          "observed_id": null,
          "requested_id": null,
          "source": "environment-declaration"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:89dc554194234ba6f6f2cbf6b7c156235bf15d2013dacdae795df1c601977685",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-26T02:14:04.486Z",
      "model_display": "claude-sonnet-5-5",
      "model_id": "claude-sonnet-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:89dc554194234ba6f6f2cbf6b7c156235bf15d2013dacdae795df1c601977685"
    }
  },
  "record_id": "review-844ccd1b697dc6e97c24b0bfb13a62fd",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-844ccd1b697dc6e97c24b0bfb13a62fd",
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
    "project_root_digest": "e9830cc5264cee35051548283974fe72b138184f8ac8a3a2c7c7af8ebcdeb586",
    "reviewer": {
      "effort": "medium",
      "host": "claude-code",
      "model_display": "claude-sonnet-5-5",
      "model_id": "claude-sonnet-5-5",
      "provider": "anthropic",
      "selector": "claude"
    },
    "schema": "ai-peer-review.runtime/v1",
    "transport_mode": "manual"
  },
  "schema": "ai-peer-review.manifest/v1",
  "startup_commit": "e907b571dd34d68ac1017d60cbccead05ba736c9",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "c4ebd79ea8cef9be0ad542db4fb66a6f7e406934",
        "digest": "sha256:5dae7d5346edbd8691658e772508a5672e9f202c332aaafec440686f33afd856",
        "path": ".aitm/stories/004/458/plan/2026-11-25-pinned-story-effort-cost-plan.md"
      },
      "author_response": {
        "digest": "sha256:38ccfee57c65e05558d34fd3042627e069651481f7900216a1c1040bf9145b52",
        "path": "docs/peer-reviews/plan/2026-11-26-2026-11-25-pinned-story-effort-cost-plan-review-844ccd1b697dc6e97c24b0bfb13a62fd/review-844ccd1b697dc6e97c24b0bfb13a62fd-author-response-1.md"
      },
      "commit": "b1f20b4deea9277b286aa83dd0e7f3eb055065f0",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:05955c361d6bb551059edb66b7cfaf4a4d1838c58a8ccce97dfea614e145d9b1",
        "path": "docs/peer-reviews/plan/2026-11-26-2026-11-25-pinned-story-effort-cost-plan-review-844ccd1b697dc6e97c24b0bfb13a62fd/review-844ccd1b697dc6e97c24b0bfb13a62fd-reviewer-response-1.md"
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
        "digest": "sha256:a18ad392648e65f57354d7475f536ca2353a8ee5aa91b6bd626284324602d78d",
        "path": "docs/peer-reviews/plan/2026-11-26-2026-11-25-pinned-story-effort-cost-plan-review-844ccd1b697dc6e97c24b0bfb13a62fd/review-844ccd1b697dc6e97c24b0bfb13a62fd-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
