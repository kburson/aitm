<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "8c3c77a102d2ee06f78f59c47c8b34750adbf426",
      "commit": "9806f13c39e573ec13d8e0cce61875f657feac15",
      "digest": "sha256:cf54ff6ed44fd650774705cb9b88911c4abe6d80e164918b5f5edf57c4079fda",
      "path": ".aitm/stories/004/458/design/2026-11-25-pinned-story-effort-cost.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "aa1cdc9940a37dff43f57d1bb7859cb9f7dad240",
      "commit": "1f66b6e322981d2eab4fcceb48cf3c010f1a65c9",
      "digest": "sha256:9d834f6dfbcb27d1cc28c6c818e6cbcba26cb044c6963ad7ba62673c72d16a57",
      "path": ".aitm/stories/004/458/design/2026-11-25-pinned-story-effort-cost.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/004/458/design/2026-11-25-pinned-story-effort-cost.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-1e7413f9-612d-4525-9a28-4eacbb2e4633",
      "claimed_at": "2026-11-26T02:06:17.086Z",
      "expires_at": "2026-11-26T10:06:17.086Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-26T02:06:17.086Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:d05378fe03130750b1936004faa46835ce3f83bc69d77971dde2756200e357bb"
    },
    {
      "claim_id": "claim-0e53d9bf-bc4e-4130-b783-9d307d51f84e",
      "claimed_at": "2026-11-26T02:06:45.486Z",
      "expires_at": "2026-11-26T10:06:45.486Z",
      "host": "codex",
      "last_activity_at": "2026-11-26T02:06:45.486Z",
      "role": "author",
      "session_fingerprint": "sha256:0a2c23fc828401b217a0141c886d3d9e315252adbc36dad83cb120f023ec2fdf"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "1f66b6e322981d2eab4fcceb48cf3c010f1a65c9",
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
        "joined_at": "2026-11-26T02:05:42.762Z",
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
        "event_log_digest": "sha256:f087ce867a0d4da41c46d01c90b6e88f3fd7e6015659330e18eff1ef7374057d",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-619e5e7edf5b675344a5e085d33d265d",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-619e5e7edf5b675344a5e085d33d265d",
        "root_review_id": "review-619e5e7edf5b675344a5e085d33d265d",
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
      "joined_at": "2026-11-26T02:05:42.762Z",
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
          "fingerprint": "sha256:d05378fe03130750b1936004faa46835ce3f83bc69d77971dde2756200e357bb",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-26T02:06:17.062Z",
      "model_display": "claude-sonnet-5-5",
      "model_id": "claude-sonnet-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:d05378fe03130750b1936004faa46835ce3f83bc69d77971dde2756200e357bb"
    }
  },
  "record_id": "review-619e5e7edf5b675344a5e085d33d265d",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-619e5e7edf5b675344a5e085d33d265d",
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
  "startup_commit": "9806f13c39e573ec13d8e0cce61875f657feac15",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "aa1cdc9940a37dff43f57d1bb7859cb9f7dad240",
        "digest": "sha256:9d834f6dfbcb27d1cc28c6c818e6cbcba26cb044c6963ad7ba62673c72d16a57",
        "path": ".aitm/stories/004/458/design/2026-11-25-pinned-story-effort-cost.md"
      },
      "author_response": {
        "digest": "sha256:d3945cc67433e650bef8e930e699e1c1598761b12ef14b4b830c1cf307b08f5a",
        "path": "docs/peer-reviews/spec/2026-11-26-2026-11-25-pinned-story-effort-cost-review-619e5e7edf5b675344a5e085d33d265d/review-619e5e7edf5b675344a5e085d33d265d-author-response-1.md"
      },
      "commit": "1f66b6e322981d2eab4fcceb48cf3c010f1a65c9",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:354765e435960cfa9c48c9416c21c2251068114baf60489805a5cc3c94ce8842",
        "path": "docs/peer-reviews/spec/2026-11-26-2026-11-25-pinned-story-effort-cost-review-619e5e7edf5b675344a5e085d33d265d/review-619e5e7edf5b675344a5e085d33d265d-reviewer-response-1.md"
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
        "digest": "sha256:8640d46e88abce29c45e3dbf9a33264109015ed511038924a051c8458684ef6e",
        "path": "docs/peer-reviews/spec/2026-11-26-2026-11-25-pinned-story-effort-cost-review-619e5e7edf5b675344a5e085d33d265d/review-619e5e7edf5b675344a5e085d33d265d-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
