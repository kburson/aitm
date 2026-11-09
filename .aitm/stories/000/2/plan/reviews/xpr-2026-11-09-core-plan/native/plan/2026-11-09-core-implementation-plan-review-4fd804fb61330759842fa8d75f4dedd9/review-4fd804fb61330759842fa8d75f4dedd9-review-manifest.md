<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "d68b6e037fe7d22dad8b4905d97b2cdf11125d76",
      "commit": "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0",
      "digest": "sha256:1f8fc7179cc17141598e985d9e8136c8ead8c44156cbbff27bad8f03d86192dd",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "30d4f40b5308eb4a1d462e9fbe7fcfd2d9ae22f6",
      "commit": "b9c4998482b5a87788279b5d3c52f87bc99e0461",
      "digest": "sha256:ec134886ca97a5163848b6396c9bcc037eafe0ca4abd48ac5f0d22985e8d3796",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "02cbded299d43dbc568d42c32e302cae7f0fcffc",
      "commit": "ee599d9240df932ff16f2d99ea4c0f28c6ab1c14",
      "digest": "sha256:327af4d64a202e06183491be50b620786681df8dd73f6a0d0265a262f8c7f5be",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 2
    },
    {
      "blob": "7da679cf53afc3ed0e267cd5bc1efb6fb1c286e0",
      "commit": "e4b89a097b49b6abee1ebb1417b21775e3e02e26",
      "digest": "sha256:cd371fe77a716fde2add99815de7d7285bb69cdee643332794fd29547397f017",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 3
    },
    {
      "blob": "83d859f106cba378b0c6e66cd2787121d1f3bc7e",
      "commit": "5b8ebfca7ce499a5abfa235d2c59639d34522483",
      "digest": "sha256:2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
      "path": ".aitm/stories/000/2/plan/core-implementation-plan.md",
      "snapshot": null,
      "turn": 4
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
      "claim_id": "claim-a16edc69-b3b2-4677-924b-83228107625c",
      "claimed_at": "2026-11-09T07:29:06.795Z",
      "expires_at": "2026-11-09T15:29:06.795Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-09T07:29:06.795Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
    },
    {
      "claim_id": "claim-deaf261c-c9d6-4fc4-86d4-54be54878458",
      "claimed_at": "2026-11-09T07:33:35.731Z",
      "expires_at": "2026-11-09T15:33:35.731Z",
      "host": "codex",
      "last_activity_at": "2026-11-09T07:33:35.731Z",
      "role": "author",
      "session_fingerprint": "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "5b8ebfca7ce499a5abfa235d2c59639d34522483",
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
        "joined_at": "2026-11-09T07:28:31.068Z",
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
        "event_log_digest": "sha256:ac6fcbad97d5b5d093fa203fc23c97d42e5dc3c785af5501588029acb97cc0e1",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-4fd804fb61330759842fa8d75f4dedd9",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-4fd804fb61330759842fa8d75f4dedd9",
        "root_review_id": "review-4fd804fb61330759842fa8d75f4dedd9",
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
      "joined_at": "2026-11-09T07:28:31.068Z",
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
          "fingerprint": "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-09T07:29:06.774Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
    }
  },
  "record_id": "review-4fd804fb61330759842fa8d75f4dedd9",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-4fd804fb61330759842fa8d75f4dedd9",
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
    "project_root_digest": "527287cd941cbfb9bf852042c507adef0ff8f30b59abaef2d8494088d6c90dc5",
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
  "startup_commit": "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "30d4f40b5308eb4a1d462e9fbe7fcfd2d9ae22f6",
        "digest": "sha256:ec134886ca97a5163848b6396c9bcc037eafe0ca4abd48ac5f0d22985e8d3796",
        "path": ".aitm/stories/000/2/plan/core-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:f12dcf44f18bd8c2b73295c3b91f2edc714510d5d09c6ded2fdb10d0fe1b46dd",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-author-response-1.md"
      },
      "commit": "b9c4998482b5a87788279b5d3c52f87bc99e0461",
      "decision": "revisions-requested",
      "finding_ids": [
        "R1-F001",
        "R1-F002",
        "R1-F003",
        "R1-F004",
        "R1-F005",
        "R1-F006",
        "R1-F007",
        "R1-F008",
        "R1-F009",
        "R1-F010",
        "R1-F011",
        "R1-F012"
      ],
      "reviewer_response": {
        "digest": "sha256:6ac6850c0b3e489c6433b0b08e4622aab9c477f9dd148400ffaec1a54b9d9430",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "02cbded299d43dbc568d42c32e302cae7f0fcffc",
        "digest": "sha256:327af4d64a202e06183491be50b620786681df8dd73f6a0d0265a262f8c7f5be",
        "path": ".aitm/stories/000/2/plan/core-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:f5107c4769a9021c0a7a0e5c15990ed17b46b945eec38cb51ed17814e57fe0ea",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-author-response-2.md"
      },
      "commit": "ee599d9240df932ff16f2d99ea4c0f28c6ab1c14",
      "decision": "revisions-requested",
      "finding_ids": [
        "R2-F001",
        "R2-F002",
        "R2-F003",
        "R2-F004"
      ],
      "reviewer_response": {
        "digest": "sha256:44f63d80bc3f4c452dc6973a1a2aa78f5a8113177e2e2859e899f87ac2c8707c",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    },
    {
      "artifact": {
        "blob": "7da679cf53afc3ed0e267cd5bc1efb6fb1c286e0",
        "digest": "sha256:cd371fe77a716fde2add99815de7d7285bb69cdee643332794fd29547397f017",
        "path": ".aitm/stories/000/2/plan/core-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:9317df9aa754d7ba1f6ce848a39b29c177006c7bf41ef921dfd8f64e5e2eb6eb",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-author-response-3.md"
      },
      "commit": "e4b89a097b49b6abee1ebb1417b21775e3e02e26",
      "decision": "revisions-requested",
      "finding_ids": [
        "R3-F001",
        "R3-F002"
      ],
      "reviewer_response": {
        "digest": "sha256:bd9d8d20bfda376376c9a6be004785989c58698827689b6265ab774418cf7034",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    },
    {
      "artifact": {
        "blob": "83d859f106cba378b0c6e66cd2787121d1f3bc7e",
        "digest": "sha256:2106b881d255f4547247e2ec0b9adfdfa7e51be9ec4ac12fd0cca5f05b9bf0dd",
        "path": ".aitm/stories/000/2/plan/core-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:25aa7eb37bfb80d70c933eda5858bbe4d44348ea9118e352a99a7519190ce6b4",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-author-response-4.md"
      },
      "commit": "5b8ebfca7ce499a5abfa235d2c59639d34522483",
      "decision": "revisions-requested",
      "finding_ids": [
        "R4-F001"
      ],
      "reviewer_response": {
        "digest": "sha256:80dac47ac2b06bdf988d8d2dda2daf31271b2e08dad329381e914e55be32fbee",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-4.md"
      },
      "snapshot": null,
      "turn": 4
    },
    {
      "artifact": null,
      "author_response": null,
      "commit": null,
      "decision": "accepted",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:d75518405cdb438195985778311a7007fcf0b043e14ba1c8e4b006dfda295587",
        "path": ".aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan/native/plan/2026-11-09-core-implementation-plan-review-4fd804fb61330759842fa8d75f4dedd9/review-4fd804fb61330759842fa8d75f4dedd9-reviewer-response-5.md"
      },
      "snapshot": null,
      "turn": 5
    }
  ]
}
```
