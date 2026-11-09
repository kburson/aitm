<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "887c2e7e4a7c89ed156ee397be9a504dfdd7dff1",
      "commit": "ab631c02f2eef28517f8a864e54679fdd548f467",
      "digest": "sha256:ef3f278a4ce014e7f8a4e5866c25b1b9d3070f2ab0ce93168bfd1a2199e18719",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "97cae59d57a60358b642c91c9d14d6e2eca78879",
      "commit": "b80d0fb9bd63cecbc9665a295c98119a24ec2440",
      "digest": "sha256:d586d85b2988f24c60a8a5a43497b00ac54316fc17963fe29955e16aa4f03219",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "a87ae8d9888667d252dc612b866a132fc21b0501",
      "commit": "967393ff2724084e19595dcc225a730a9f5cf998",
      "digest": "sha256:19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 2
    }
  ],
  "artifact_path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-3b778829-d7e5-492e-ab31-f62114d9738e",
      "claimed_at": "2026-11-09T13:20:53.298Z",
      "expires_at": "2026-11-09T21:20:53.298Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T13:20:53.298Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:00278e43df2c8f02eef7ab5892e8a19c3d1097a8b1ee6e0e18436dcf006ca043"
    },
    {
      "claim_id": "claim-3b8bc0b0-c5e9-4a11-933b-f5dbdc07f1c6",
      "claimed_at": "2026-11-09T13:25:40.742Z",
      "expires_at": "2026-11-09T21:25:40.742Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T13:25:40.742Z",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "967393ff2724084e19595dcc225a730a9f5cf998",
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
            "requested_id": "gpt-6-astra",
            "source": "launch-request"
          },
          "session": {
            "assurance": "declared",
            "fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-09T13:20:22.129Z",
        "model_display": "gpt-6-astra",
        "model_id": "gpt-6-astra",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:b51ddeed0d1662d8c81597739da531a5aed690519deba50cbb259a6d1ffa780f",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-09e4246bfa4caa5feff1592de9f2249c",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-09e4246bfa4caa5feff1592de9f2249c",
        "root_review_id": "review-09e4246bfa4caa5feff1592de9f2249c",
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
          "requested_id": "gpt-6-astra",
          "source": "launch-request"
        },
        "session": {
          "assurance": "declared",
          "fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T13:20:22.129Z",
      "model_display": "gpt-6-astra",
      "model_id": "gpt-6-astra",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
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
          "fingerprint": "sha256:00278e43df2c8f02eef7ab5892e8a19c3d1097a8b1ee6e0e18436dcf006ca043",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T13:20:53.276Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:00278e43df2c8f02eef7ab5892e8a19c3d1097a8b1ee6e0e18436dcf006ca043"
    }
  },
  "record_id": "review-09e4246bfa4caa5feff1592de9f2249c",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-09e4246bfa4caa5feff1592de9f2249c",
  "runtime": {
    "adapter_version": "1.0.0",
    "author": {
      "effort": "xhigh",
      "host": "codex",
      "model_display": "gpt-6-astra",
      "model_id": "gpt-6-astra",
      "provider": "openai"
    },
    "classification": "XPR",
    "ownership": "broker",
    "project_root_digest": "0632eda9d4027a84e1bf1d401479e0274e876c1468709c6125d7e5d696bbe1c4",
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
  "startup_commit": "ab631c02f2eef28517f8a864e54679fdd548f467",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "97cae59d57a60358b642c91c9d14d6e2eca78879",
        "digest": "sha256:d586d85b2988f24c60a8a5a43497b00ac54316fc17963fe29955e16aa4f03219",
        "path": ".aitm/stories/000/2/plan/core-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:bc7bd731a135f418b494c185cea8b26d4e23d53bca86c3cc78287257aedbfdcc",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-author-response-1.md"
      },
      "commit": "b80d0fb9bd63cecbc9665a295c98119a24ec2440",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:5b36a24353f6ca5110afbb21a5a43f906275b9caf204c37cabb725a1f06132ce",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "a87ae8d9888667d252dc612b866a132fc21b0501",
        "digest": "sha256:19b607f81a82ce7680339abab2adbd96ca91351c229c9bcf4dc2c0fc89d887b8",
        "path": ".aitm/stories/000/2/plan/core-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:6e7a2eb3101b1583f299582db406e460ab9160aa9e97ff3323a318a5fb767523",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-author-response-2.md"
      },
      "commit": "967393ff2724084e19595dcc225a730a9f5cf998",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:9c7494e02bbbbdb972d7f09b036113e749060be02b1cbbbc47ad30dcce0f67aa",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    },
    {
      "artifact": null,
      "author_response": null,
      "commit": null,
      "decision": "accepted",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:836d3556bcb9efac220efb61075ca6df7516b8d1ea761be21eea7f9ff6f312eb",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
