<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "dd63e65951195b3f57c001186e2aca44bf1595f2",
      "commit": "4e7d5708bb5628d7a6767d295fbf4eeacc72670b",
      "digest": "sha256:2506b3bb129e98ca936677c825513fee65f838a65e1c7625087ec091fba5a02e",
      "path": ".aitm/stories/001/103/design/github-ci-quality-gates-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "0fe509aa14e59d00553fe94170bdb30188b624a4",
      "commit": "dc507c8017ed6fb01cb39c561cec77a6959fb206",
      "digest": "sha256:96ef0fb0019e82c3ed43387c6e9efedc83bfeeae6a9094ac4de42980009d120b",
      "path": ".aitm/stories/001/103/design/github-ci-quality-gates-design.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "47890eb1d11573112ec1bd7e5b3400ba9363c27d",
      "commit": "144133b12dfb0fe62644c8359550c92abd4333c2",
      "digest": "sha256:d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0",
      "path": ".aitm/stories/001/103/design/github-ci-quality-gates-design.md",
      "snapshot": null,
      "turn": 2
    }
  ],
  "artifact_path": ".aitm/stories/001/103/design/github-ci-quality-gates-design.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-39085862-3dc2-4749-bfac-489944220cd0",
      "claimed_at": "2026-11-10T02:45:49.410Z",
      "expires_at": "2026-11-10T10:45:49.410Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T02:45:49.410Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:3bae1567c47b4a0eb7bcaa003c3fee94a2ce29d930504d00aa989d4aa5887226"
    },
    {
      "claim_id": "claim-fe416e45-0b85-451b-9406-ad6a420c5b9e",
      "claimed_at": "2026-11-10T02:48:35.337Z",
      "expires_at": "2026-11-10T10:48:35.337Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T02:48:35.337Z",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "144133b12dfb0fe62644c8359550c92abd4333c2",
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
            "fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-10T02:45:20.325Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:746d8ff19630623e1e48353854da36ddde143113339e6dfd508a902d8bc7d4b2",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-2001d40a8de8ac60b2d33b424e958263",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-2001d40a8de8ac60b2d33b424e958263",
        "root_review_id": "review-2001d40a8de8ac60b2d33b424e958263",
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
          "fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T02:45:20.325Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:664318926dfdb04419486df4dc11e2de5f5ae3b5fa76b098a3d841a6e3c93bef"
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
          "fingerprint": "sha256:3bae1567c47b4a0eb7bcaa003c3fee94a2ce29d930504d00aa989d4aa5887226",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T02:45:49.379Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:3bae1567c47b4a0eb7bcaa003c3fee94a2ce29d930504d00aa989d4aa5887226"
    }
  },
  "record_id": "review-2001d40a8de8ac60b2d33b424e958263",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-2001d40a8de8ac60b2d33b424e958263",
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
    "project_root_digest": "9a5957a1447ef2b0da01758772aef1e93eeb30901fdfb0613ea39563b8fad050",
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
  "startup_commit": "4e7d5708bb5628d7a6767d295fbf4eeacc72670b",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "0fe509aa14e59d00553fe94170bdb30188b624a4",
        "digest": "sha256:96ef0fb0019e82c3ed43387c6e9efedc83bfeeae6a9094ac4de42980009d120b",
        "path": ".aitm/stories/001/103/design/github-ci-quality-gates-design.md"
      },
      "author_response": {
        "digest": "sha256:a01978c2602afb601290400ffc4fa1a7460220ac7a9c561755e58c13284c6d2b",
        "path": ".aitm/stories/001/103/design/reviews/xpr-2026-11-09-ci-design/spec/2026-11-10-github-ci-quality-gates-design-review-2001d40a8de8ac60b2d33b424e958263/review-2001d40a8de8ac60b2d33b424e958263-author-response-1.md"
      },
      "commit": "dc507c8017ed6fb01cb39c561cec77a6959fb206",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:d6fc8b2e0037bc8060f74cfbc735f6af53acd902cb5059e7d2882426226d38da",
        "path": ".aitm/stories/001/103/design/reviews/xpr-2026-11-09-ci-design/spec/2026-11-10-github-ci-quality-gates-design-review-2001d40a8de8ac60b2d33b424e958263/review-2001d40a8de8ac60b2d33b424e958263-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "47890eb1d11573112ec1bd7e5b3400ba9363c27d",
        "digest": "sha256:d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0",
        "path": ".aitm/stories/001/103/design/github-ci-quality-gates-design.md"
      },
      "author_response": {
        "digest": "sha256:5c6a374207ce81706856be233be5566c363fc4967c06578b585e7815916ceb3c",
        "path": ".aitm/stories/001/103/design/reviews/xpr-2026-11-09-ci-design/spec/2026-11-10-github-ci-quality-gates-design-review-2001d40a8de8ac60b2d33b424e958263/review-2001d40a8de8ac60b2d33b424e958263-author-response-2.md"
      },
      "commit": "144133b12dfb0fe62644c8359550c92abd4333c2",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:2cefbf8519a1c0ac37a6a25f6583fa4c649621b5523835799fd51b1b6af9b7fe",
        "path": ".aitm/stories/001/103/design/reviews/xpr-2026-11-09-ci-design/spec/2026-11-10-github-ci-quality-gates-design-review-2001d40a8de8ac60b2d33b424e958263/review-2001d40a8de8ac60b2d33b424e958263-reviewer-response-2.md"
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
        "digest": "sha256:7d13d07ef61a11ae4f50b17d67d713eaf30c507195f57bd0800cbe2678ff2749",
        "path": ".aitm/stories/001/103/design/reviews/xpr-2026-11-09-ci-design/spec/2026-11-10-github-ci-quality-gates-design-review-2001d40a8de8ac60b2d33b424e958263/review-2001d40a8de8ac60b2d33b424e958263-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
