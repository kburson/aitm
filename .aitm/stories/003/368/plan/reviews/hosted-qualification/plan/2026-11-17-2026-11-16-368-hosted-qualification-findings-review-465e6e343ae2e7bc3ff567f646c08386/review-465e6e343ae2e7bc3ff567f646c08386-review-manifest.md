<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "446cd92432e686752db37e48b4fea612b613313e",
      "commit": "e7962ba930426006eeb272d3c80fca452123e11a",
      "digest": "sha256:0b980ca1b80eeb8588bc803d0fdcf1a76f6d721595cd18e011b22eb0c00b35d2",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-qualification-findings.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "c1f436e594ad8e89948f67e47c2b662926803e56",
      "commit": "c3cc41fc1e14697fd707c17fac6371280185617f",
      "digest": "sha256:7af4c6094fec8726fe686cbcc7ef6c3e8560521051aa86cdb385f483476d24b6",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-qualification-findings.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-qualification-findings.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-fd9fe792-441b-4654-b4f2-91802dc2a5cd",
      "claimed_at": "2026-11-17T06:10:27.399Z",
      "expires_at": "2026-11-17T14:10:27.399Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T06:10:27.399Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:ca2e6e5dd8544fac11d41eec2903c201b5ea9783bb31dcfd24948053f30276aa"
    },
    {
      "claim_id": "claim-268a9568-816c-4df0-a48d-db79c6856d5f",
      "claimed_at": "2026-11-17T06:14:40.658Z",
      "expires_at": "2026-11-17T14:14:40.658Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T06:14:40.658Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "c3cc41fc1e14697fd707c17fac6371280185617f",
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
        "joined_at": "2026-11-17T06:09:25.720Z",
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
        "event_log_digest": "sha256:594423328e6436bb02853f979517e4aa061caee9f0e09cdc8a5cb34bac108cb4",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-465e6e343ae2e7bc3ff567f646c08386",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-465e6e343ae2e7bc3ff567f646c08386",
        "root_review_id": "review-465e6e343ae2e7bc3ff567f646c08386",
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
      "joined_at": "2026-11-17T06:09:25.720Z",
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
          "fingerprint": "sha256:ca2e6e5dd8544fac11d41eec2903c201b5ea9783bb31dcfd24948053f30276aa",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T06:10:27.377Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:ca2e6e5dd8544fac11d41eec2903c201b5ea9783bb31dcfd24948053f30276aa"
    }
  },
  "record_id": "review-465e6e343ae2e7bc3ff567f646c08386",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-465e6e343ae2e7bc3ff567f646c08386",
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
  "startup_commit": "e7962ba930426006eeb272d3c80fca452123e11a",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "c1f436e594ad8e89948f67e47c2b662926803e56",
        "digest": "sha256:7af4c6094fec8726fe686cbcc7ef6c3e8560521051aa86cdb385f483476d24b6",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-qualification-findings.md"
      },
      "author_response": {
        "digest": "sha256:d5240151d822d70e1685c25d23d43f0db107b8cc4da484f202ff384b46d27a93",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-qualification/plan/2026-11-17-2026-11-16-368-hosted-qualification-findings-review-465e6e343ae2e7bc3ff567f646c08386/review-465e6e343ae2e7bc3ff567f646c08386-author-response-1.md"
      },
      "commit": "c3cc41fc1e14697fd707c17fac6371280185617f",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:e1f0829e5430e79709b3bfbd4695170b359b74b0ea6dafa56358d94822dd327e",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-qualification/plan/2026-11-17-2026-11-16-368-hosted-qualification-findings-review-465e6e343ae2e7bc3ff567f646c08386/review-465e6e343ae2e7bc3ff567f646c08386-reviewer-response-1.md"
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
        "digest": "sha256:04f00916fc26044affba23dda486618af42c29fd827d1b1786ea7ae96b754041",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-qualification/plan/2026-11-17-2026-11-16-368-hosted-qualification-findings-review-465e6e343ae2e7bc3ff567f646c08386/review-465e6e343ae2e7bc3ff567f646c08386-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
