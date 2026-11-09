<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "767b7bbf82da157494fc94feb5ebf3092c97ed55",
      "commit": "bcacb1378ca2cf268bb194cdf80f4fe21f155b2d",
      "digest": "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d",
      "path": ".aitm/stories/000/2/design/core-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "dfed3624be221f3f7358a00b065bbbc2a456cbc4",
      "commit": "86ac9caf47c95d6443e329759ede387c2cfe37e6",
      "digest": "sha256:3355a89fdfd38e16b9f4aeb37fc8fb368ea74ce8b7e608f0504b67a2e9288253",
      "path": ".aitm/stories/000/2/design/core-design.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "3b83c1b5858036702f0993bfb7b48b21800d4a2f",
      "commit": "013cdf2fd4ea753ae94cbb434d146fe5a284f61e",
      "digest": "sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7",
      "path": ".aitm/stories/000/2/design/core-design.md",
      "snapshot": null,
      "turn": 2
    }
  ],
  "artifact_path": ".aitm/stories/000/2/design/core-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-806d7033-31e1-4ab8-bde8-14f1a2e289c7",
      "claimed_at": "2026-11-09T12:48:50.061Z",
      "expires_at": "2026-11-09T20:48:50.061Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T12:48:50.061Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8"
    },
    {
      "claim_id": "claim-05881bb9-3cac-48c1-83e0-e547865df3f1",
      "claimed_at": "2026-11-09T12:53:12.820Z",
      "expires_at": "2026-11-09T20:53:12.820Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T12:53:12.820Z",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "013cdf2fd4ea753ae94cbb434d146fe5a284f61e",
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
        "joined_at": "2026-11-09T12:48:20.791Z",
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
        "event_log_digest": "sha256:a15e9d5583650d1a4723d3b2583caeddacb38ea8406cd28d437062ce181f51b0",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-48ae3de9ffa0067249b56573a8a3b1c8",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-48ae3de9ffa0067249b56573a8a3b1c8",
        "root_review_id": "review-48ae3de9ffa0067249b56573a8a3b1c8",
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
      "joined_at": "2026-11-09T12:48:20.791Z",
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
          "fingerprint": "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T12:48:50.030Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8"
    }
  },
  "record_id": "review-48ae3de9ffa0067249b56573a8a3b1c8",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-48ae3de9ffa0067249b56573a8a3b1c8",
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
    "project_root_digest": "14038d0b357f432aa9a4853e020871f3df41932d19f6a5230b5a1dfcb0aa69bb",
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
  "startup_commit": "bcacb1378ca2cf268bb194cdf80f4fe21f155b2d",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "dfed3624be221f3f7358a00b065bbbc2a456cbc4",
        "digest": "sha256:3355a89fdfd38e16b9f4aeb37fc8fb368ea74ce8b7e608f0504b67a2e9288253",
        "path": ".aitm/stories/000/2/design/core-design.md"
      },
      "author_response": {
        "digest": "sha256:0778bc3c23bb452053fd2eaba8d2e7a3705a175ffed86ecd93744d6378009155",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-09-core-design-fullfile/native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-author-response-1.md"
      },
      "commit": "86ac9caf47c95d6443e329759ede387c2cfe37e6",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003"
      ],
      "reviewer_response": {
        "digest": "sha256:474fa711f89ebf292af1f2de06f9b6eaf3dbda0b18ccb339742cfd9fd89ad191",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-09-core-design-fullfile/native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "3b83c1b5858036702f0993bfb7b48b21800d4a2f",
        "digest": "sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7",
        "path": ".aitm/stories/000/2/design/core-design.md"
      },
      "author_response": {
        "digest": "sha256:ab4f112492d0f7854e1003f973867ef7c7336d4d5d7d866cb183ce6b5d74449e",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-09-core-design-fullfile/native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-author-response-2.md"
      },
      "commit": "013cdf2fd4ea753ae94cbb434d146fe5a284f61e",
      "decision": "revisions-requested",
      "finding_ids": [
        "R2-F001",
        "R2-F002"
      ],
      "reviewer_response": {
        "digest": "sha256:7c6dc37adac0d6540910353c33de06d4d4361683f24e9be87cd2563ff3467b52",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-09-core-design-fullfile/native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-2.md"
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
        "digest": "sha256:a8fc63ffa0939b654a08e4b0d038259d6760ccc00d0d96637c48296b0f7439ae",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-09-core-design-fullfile/native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
