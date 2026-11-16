<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "f20446fb08341308f40c3ff0a430860522aa6746",
      "commit": "6e9eb06220c70186c0146bc9d29af65196fa9e16",
      "digest": "sha256:c0eb6620d0eb7ae7dc922cafe5975d030718acf244b095db86494fc12bb6056c",
      "path": ".aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "c4b40426a7293295e5332439be2fafadc2a50589",
      "commit": "0fbf65b9244e0dfe7d7a0301707d59b0a5cddabd",
      "digest": "sha256:0267141e5b25ee88112e23b081e8d392aca09d0142ad8f6b4d1b1e1dabab0530",
      "path": ".aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-b18c2331-45c6-478d-abcf-389e4d8543cc",
      "claimed_at": "2026-11-16T21:58:30.205Z",
      "expires_at": "2026-11-17T05:58:30.205Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-16T21:58:30.205Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:5fd002c0d6ba48119db5a190bc420a12968335ffedbe4e46983bb5a6666383d1"
    },
    {
      "claim_id": "claim-2e6eb1a2-1d08-4f48-a51c-9c3c3f3b7194",
      "claimed_at": "2026-11-16T22:03:24.946Z",
      "expires_at": "2026-11-17T06:03:24.946Z",
      "host": "codex",
      "last_activity_at": "2026-11-16T22:03:24.946Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "0fbf65b9244e0dfe7d7a0301707d59b0a5cddabd",
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
        "joined_at": "2026-11-16T21:57:56.248Z",
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
        "event_log_digest": "sha256:677ae0515a4640ca670078019c22b16dc61e150841beb8bc0ba95e17f0f0c11d",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-f07dbc2d2f9b704a70c2cb872586d1dc",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-f07dbc2d2f9b704a70c2cb872586d1dc",
        "root_review_id": "review-f07dbc2d2f9b704a70c2cb872586d1dc",
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
      "joined_at": "2026-11-16T21:57:56.248Z",
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
          "fingerprint": "sha256:5fd002c0d6ba48119db5a190bc420a12968335ffedbe4e46983bb5a6666383d1",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-16T21:58:30.172Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:5fd002c0d6ba48119db5a190bc420a12968335ffedbe4e46983bb5a6666383d1"
    }
  },
  "record_id": "review-f07dbc2d2f9b704a70c2cb872586d1dc",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-f07dbc2d2f9b704a70c2cb872586d1dc",
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
  "startup_commit": "6e9eb06220c70186c0146bc9d29af65196fa9e16",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "c4b40426a7293295e5332439be2fafadc2a50589",
        "digest": "sha256:0267141e5b25ee88112e23b081e8d392aca09d0142ad8f6b4d1b1e1dabab0530",
        "path": ".aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md"
      },
      "author_response": {
        "digest": "sha256:c41b0581a5aed030e81e053515f098141fdf92820f789f350b2cfcc52544e445",
        "path": ".aitm/stories/003/354/plan/reviews/plan/2026-11-16-2026-11-16-354-working-tree-obligations-plan-review-f07dbc2d2f9b704a70c2cb872586d1dc/review-f07dbc2d2f9b704a70c2cb872586d1dc-author-response-1.md"
      },
      "commit": "0fbf65b9244e0dfe7d7a0301707d59b0a5cddabd",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004",
        "R1-F005"
      ],
      "reviewer_response": {
        "digest": "sha256:89ffc107a8188e999539ff4f9ffb5b7a1ae17e603bece7222256242499f94c84",
        "path": ".aitm/stories/003/354/plan/reviews/plan/2026-11-16-2026-11-16-354-working-tree-obligations-plan-review-f07dbc2d2f9b704a70c2cb872586d1dc/review-f07dbc2d2f9b704a70c2cb872586d1dc-reviewer-response-1.md"
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
        "digest": "sha256:83009ea236b9f468c7b4587f4dc5fe295cf707f1dfaf97631981e5c9f09e342d",
        "path": ".aitm/stories/003/354/plan/reviews/plan/2026-11-16-2026-11-16-354-working-tree-obligations-plan-review-f07dbc2d2f9b704a70c2cb872586d1dc/review-f07dbc2d2f9b704a70c2cb872586d1dc-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
