<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "7352a3b8ab8f6e924078dd162459a1550e01da4c",
      "commit": "41c129a1c5a10da34ead7afd74086d161cdcb411",
      "digest": "sha256:ba5f792ba3f84190926061c808a2e2c26b5d01d4f4cf79c555732d80fc22f00d",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "6e61eaa157b9c2fd4699c86c0bceff21e495c179",
      "commit": "3b1b2813579082046e6527847dc5f8d4c8fcfc30",
      "digest": "sha256:086cade1941fe06df033a9f6cf91938f4ae00be6e7bd1cbf667f50697273b693",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-8df82c8c-df8b-43d2-a508-99b3360162d8",
      "claimed_at": "2026-11-17T05:23:19.905Z",
      "expires_at": "2026-11-17T13:23:19.905Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T05:23:19.905Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:b06e9ca10c5c7a630bac2effe5a5a3757ebe6a0d49fb9165f20fe31a9b315605"
    },
    {
      "claim_id": "claim-03efa2e8-d466-479c-b819-098a7ac86529",
      "claimed_at": "2026-11-17T05:25:29.748Z",
      "expires_at": "2026-11-17T13:25:29.748Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T05:25:29.748Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "3b1b2813579082046e6527847dc5f8d4c8fcfc30",
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
        "joined_at": "2026-11-17T05:22:30.515Z",
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
        "event_log_digest": "sha256:347fa4b0bb7fbb8b295fc7138d2abbb6602cb2843322311b5bd50a4a889474d4",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-9e6f1dfbab13cc5d8c17d1c53bd75978",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-9e6f1dfbab13cc5d8c17d1c53bd75978",
        "root_review_id": "review-9e6f1dfbab13cc5d8c17d1c53bd75978",
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
      "joined_at": "2026-11-17T05:22:30.515Z",
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
          "fingerprint": "sha256:b06e9ca10c5c7a630bac2effe5a5a3757ebe6a0d49fb9165f20fe31a9b315605",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T05:23:19.883Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:b06e9ca10c5c7a630bac2effe5a5a3757ebe6a0d49fb9165f20fe31a9b315605"
    }
  },
  "record_id": "review-9e6f1dfbab13cc5d8c17d1c53bd75978",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-9e6f1dfbab13cc5d8c17d1c53bd75978",
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
  "startup_commit": "41c129a1c5a10da34ead7afd74086d161cdcb411",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "6e61eaa157b9c2fd4699c86c0bceff21e495c179",
        "digest": "sha256:086cade1941fe06df033a9f6cf91938f4ae00be6e7bd1cbf667f50697273b693",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-restore-retry-packet.md"
      },
      "author_response": {
        "digest": "sha256:3f7d14cc14a8da5523b84c08f83bf26522ab86f7a7be95cc891a7c25a386631b",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-retry/plan/2026-11-17-2026-11-16-368-hosted-restore-retry-packet-review-9e6f1dfbab13cc5d8c17d1c53bd75978/review-9e6f1dfbab13cc5d8c17d1c53bd75978-author-response-1.md"
      },
      "commit": "3b1b2813579082046e6527847dc5f8d4c8fcfc30",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:baad7e9514226b038a6917bf125c44a94141c6f986676ea814612c0229a7237e",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-retry/plan/2026-11-17-2026-11-16-368-hosted-restore-retry-packet-review-9e6f1dfbab13cc5d8c17d1c53bd75978/review-9e6f1dfbab13cc5d8c17d1c53bd75978-reviewer-response-1.md"
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
        "digest": "sha256:85760333b65b5b1f2a23ab575ab209460e3880641bd5f9ba3f436bc96c7d6958",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-retry/plan/2026-11-17-2026-11-16-368-hosted-restore-retry-packet-review-9e6f1dfbab13cc5d8c17d1c53bd75978/review-9e6f1dfbab13cc5d8c17d1c53bd75978-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
