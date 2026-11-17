<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "8810fd841a5da4bd9f7e3459acb87b39719cbf5d",
      "commit": "d4bb3d7f6bdaf0c8d937ae79b7ac3381d15fa296",
      "digest": "sha256:2ca6900a4c72224c44c710e32d8ed1f800f4a8e1c811a8c3c5eeb58d32959182",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "498c3cd756b0fe1dd7c6d817a262970abaa14cfb",
      "commit": "bd28ecf7fcaf212a6dfd3fae128e3a7871691dcb",
      "digest": "sha256:361618e5244f2c64aaffb98a31a3ea291ee62797f27c700304f41bc7b225885f",
      "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-a402d64f-6c6f-4198-9a0c-6e3a077f5fda",
      "claimed_at": "2026-11-17T12:24:55.999Z",
      "expires_at": "2026-11-17T20:24:55.999Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T12:24:55.999Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:a3aefea571c34dba0defe3439ea1d9d5946cf7b46dd4524a6cd5b3df66a84530"
    },
    {
      "claim_id": "claim-7350dc73-6e7d-42ae-b26f-a01536bd254b",
      "claimed_at": "2026-11-17T12:28:53.335Z",
      "expires_at": "2026-11-17T20:28:53.335Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T12:28:53.335Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "bd28ecf7fcaf212a6dfd3fae128e3a7871691dcb",
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
        "joined_at": "2026-11-17T12:24:17.807Z",
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
        "event_log_digest": "sha256:fad09eb2d06f4e36f33626f2a4ac3b8c83f49683716e879e745346ee942eb20d",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-84fdbdfe0dd75c4a33ae32978465093a",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-84fdbdfe0dd75c4a33ae32978465093a",
        "root_review_id": "review-84fdbdfe0dd75c4a33ae32978465093a",
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
      "joined_at": "2026-11-17T12:24:17.807Z",
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
          "fingerprint": "sha256:a3aefea571c34dba0defe3439ea1d9d5946cf7b46dd4524a6cd5b3df66a84530",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T12:24:55.979Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:a3aefea571c34dba0defe3439ea1d9d5946cf7b46dd4524a6cd5b3df66a84530"
    }
  },
  "record_id": "review-84fdbdfe0dd75c4a33ae32978465093a",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-84fdbdfe0dd75c4a33ae32978465093a",
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
  "startup_commit": "d4bb3d7f6bdaf0c8d937ae79b7ac3381d15fa296",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "498c3cd756b0fe1dd7c6d817a262970abaa14cfb",
        "digest": "sha256:361618e5244f2c64aaffb98a31a3ea291ee62797f27c700304f41bc7b225885f",
        "path": ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:888f304f17206e1d76e2893e4e5295133fe1015718cb385d224eaad21d556374",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry/plan/2026-11-17-2026-11-17-368-hosted-ancestry-implementation-plan-review-84fdbdfe0dd75c4a33ae32978465093a/review-84fdbdfe0dd75c4a33ae32978465093a-author-response-1.md"
      },
      "commit": "bd28ecf7fcaf212a6dfd3fae128e3a7871691dcb",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:58fd4ef33366b8efcb5773a94e80179107d1f88d93e0033a5dc180e9d97063a9",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry/plan/2026-11-17-2026-11-17-368-hosted-ancestry-implementation-plan-review-84fdbdfe0dd75c4a33ae32978465093a/review-84fdbdfe0dd75c4a33ae32978465093a-reviewer-response-1.md"
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
        "digest": "sha256:1099a321a6880c278b5586b90156d53a2170418066cfbdc42217fce0df864cf2",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-ancestry/plan/2026-11-17-2026-11-17-368-hosted-ancestry-implementation-plan-review-84fdbdfe0dd75c4a33ae32978465093a/review-84fdbdfe0dd75c4a33ae32978465093a-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
