<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "a21256d003ec73b3e278038c42d4051171525b80",
      "commit": "63c7e85d66153db6dc03e5aa41fc8d8191845632",
      "digest": "sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1",
      "path": ".aitm/stories/000/2/design/core-design.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "dffd7a5d59ce58c4d7346baf8878b83d4a53ad0c",
      "commit": "24421786443106ae83dc85e955db6ec133fa3a10",
      "digest": "sha256:a21126bb83c00fcc6eda84d7a603c030c926f7667d700acbab12291488a94102",
      "path": ".aitm/stories/000/2/design/core-design.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "767b7bbf82da157494fc94feb5ebf3092c97ed55",
      "commit": "2389091675d6567b5073740812593a4e71d17447",
      "digest": "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d",
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
      "claim_id": "claim-ce63b667-45f6-432b-bfee-82d2cf64d368",
      "claimed_at": "2026-11-09T05:57:59.832Z",
      "expires_at": "2026-11-09T13:57:59.832Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T05:57:59.832Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01"
    },
    {
      "claim_id": "claim-1001c259-c531-4991-9eb3-ea3ea5d4799f",
      "claimed_at": "2026-11-09T06:02:03.195Z",
      "expires_at": "2026-11-09T14:02:03.195Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T06:02:03.195Z",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "2389091675d6567b5073740812593a4e71d17447",
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
        "joined_at": "2026-11-09T05:57:25.687Z",
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
        "event_log_digest": "sha256:370dfc1622b7c55388404102dc366ce436909f3194d2f820308f5bbccc49ca1c",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-095b15003bea70559dd3ce3bb285292a",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-095b15003bea70559dd3ce3bb285292a",
        "root_review_id": "review-095b15003bea70559dd3ce3bb285292a",
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
      "joined_at": "2026-11-09T05:57:25.687Z",
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
          "fingerprint": "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T05:57:59.810Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01"
    }
  },
  "record_id": "review-095b15003bea70559dd3ce3bb285292a",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-095b15003bea70559dd3ce3bb285292a",
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
    "project_root_digest": "f0c77ea8c58f25bcc08dd835352561f8a29a96d406695e3204389ed2ff37f562",
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
  "startup_commit": "63c7e85d66153db6dc03e5aa41fc8d8191845632",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "dffd7a5d59ce58c4d7346baf8878b83d4a53ad0c",
        "digest": "sha256:a21126bb83c00fcc6eda84d7a603c030c926f7667d700acbab12291488a94102",
        "path": ".aitm/stories/000/2/design/core-design.md"
      },
      "author_response": {
        "digest": "sha256:8fe04423a83ddd3fdbe28a23acabbb4f66f223e849d0594fa83f9bfec960fd0f",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-author-response-1.md"
      },
      "commit": "24421786443106ae83dc85e955db6ec133fa3a10",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004"
      ],
      "reviewer_response": {
        "digest": "sha256:d8ab9bca056aaf98da9bc2e3fe1dcd27abe46b70370f3a674a959f7c68aa1575",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "767b7bbf82da157494fc94feb5ebf3092c97ed55",
        "digest": "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d",
        "path": ".aitm/stories/000/2/design/core-design.md"
      },
      "author_response": {
        "digest": "sha256:bf7423adb219ee80e95ab44a4f02f9a4fda67459a94a649558cbb2e49362f866",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-author-response-2.md"
      },
      "commit": "2389091675d6567b5073740812593a4e71d17447",
      "decision": "revisions-requested",
      "finding_ids": [
        "R2-F001",
        "R2-F002"
      ],
      "reviewer_response": {
        "digest": "sha256:3bc7995e2e452a255d2b4649c5696ddb1c6c6432937825863bca243937daabf7",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-2.md"
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
        "digest": "sha256:fcffded238d61cc766f94b96534c9b84a9d988b2626d7ad143568171281b5298",
        "path": ".aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
