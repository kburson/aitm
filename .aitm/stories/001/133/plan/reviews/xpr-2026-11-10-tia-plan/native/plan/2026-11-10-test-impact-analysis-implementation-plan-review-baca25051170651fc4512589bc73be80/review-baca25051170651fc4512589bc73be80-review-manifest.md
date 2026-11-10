<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "2a249109fba9be97f43369cb2d55961541df3927",
      "commit": "03af51301e6de2665e7c85e759ef133d285791b6",
      "digest": "sha256:3549515f497a736d5cc101cb2f28aacc5c69f666936a3bdcd0d624ca1b133a07",
      "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "2cd3746caae2f1148605fcb9548b304356430be9",
      "commit": "7d3d1a57db05abdc97cace136fdda3e847f8c64b",
      "digest": "sha256:4500099ac8f04148f1f0f6ee8c2fc31c5e53cbdc16707bcc0fb16f931c97bd59",
      "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md",
      "snapshot": null,
      "turn": 1
    },
    {
      "blob": "28af578ca04f3f3e2c9b790ed0526b03979c06f0",
      "commit": "8aece3870c3e3e92009e6248184203e48ac8e37c",
      "digest": "sha256:ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7",
      "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md",
      "snapshot": null,
      "turn": 2
    }
  ],
  "artifact_path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-15ec2890-ebba-4319-8ca4-2d211cde8cb1",
      "claimed_at": "2026-11-10T16:39:35.666Z",
      "expires_at": "2026-11-11T00:39:35.666Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-10T16:39:35.666Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:1acdf73fcbb80586e286552155f58ea364355a0fa6bf788f441a1f726bf2e2ee"
    },
    {
      "claim_id": "claim-46998e64-6fb5-4b57-bd90-01fb50b52c55",
      "claimed_at": "2026-11-10T16:42:36.947Z",
      "expires_at": "2026-11-11T00:42:36.947Z",
      "host": "codex",
      "last_activity_at": "2026-11-10T16:42:36.947Z",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "8aece3870c3e3e92009e6248184203e48ac8e37c",
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
            "fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1",
            "source": "official-runtime"
          }
        },
        "host": "codex",
        "identity_source": "runtime",
        "joined_at": "2026-11-10T16:39:09.661Z",
        "model_display": "gpt-6.1-sol",
        "model_id": "gpt-6.1-sol",
        "provider": "openai",
        "role": "author",
        "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
      },
      "role": "author",
      "sequence": 3
    }
  ],
  "lineage_receipt": {
    "attempts": [
      {
        "consumed_grant_digest": null,
        "event_log_digest": "sha256:89591f5f9e8275c4ac949d4096c63b32de64b0b0ccf9f27a7fa60e5939310da3",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-baca25051170651fc4512589bc73be80",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-baca25051170651fc4512589bc73be80",
        "root_review_id": "review-baca25051170651fc4512589bc73be80",
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
          "fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1",
          "source": "official-runtime"
        }
      },
      "host": "codex",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T16:39:09.661Z",
      "model_display": "gpt-6.1-sol",
      "model_id": "gpt-6.1-sol",
      "provider": "openai",
      "role": "author",
      "session_fingerprint": "sha256:97325cc8fb55f4eb160fc8e7bb916436cbc2816c1b8b7ad52566c0039feaf0c1"
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
          "fingerprint": "sha256:1acdf73fcbb80586e286552155f58ea364355a0fa6bf788f441a1f726bf2e2ee",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-10T16:39:35.636Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:1acdf73fcbb80586e286552155f58ea364355a0fa6bf788f441a1f726bf2e2ee"
    }
  },
  "record_id": "review-baca25051170651fc4512589bc73be80",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-baca25051170651fc4512589bc73be80",
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
    "project_root_digest": "45e35c8c443b53cfec5d21e6860f429b6360871e74879412a467ad07ee9e0b01",
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
  "startup_commit": "03af51301e6de2665e7c85e759ef133d285791b6",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "2cd3746caae2f1148605fcb9548b304356430be9",
        "digest": "sha256:4500099ac8f04148f1f0f6ee8c2fc31c5e53cbdc16707bcc0fb16f931c97bd59",
        "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:5fcca59d780ba6dc2c07c311ccb98203353dd000e5afafb453061ca517a9e19f",
        "path": ".aitm/stories/001/133/plan/reviews/xpr-2026-11-10-tia-plan/native/plan/2026-11-10-test-impact-analysis-implementation-plan-review-baca25051170651fc4512589bc73be80/review-baca25051170651fc4512589bc73be80-author-response-1.md"
      },
      "commit": "7d3d1a57db05abdc97cace136fdda3e847f8c64b",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:28032946a006651e52e87e310c06cfc51edddcfc4f7d6b545edecac8f10dea19",
        "path": ".aitm/stories/001/133/plan/reviews/xpr-2026-11-10-tia-plan/native/plan/2026-11-10-test-impact-analysis-implementation-plan-review-baca25051170651fc4512589bc73be80/review-baca25051170651fc4512589bc73be80-reviewer-response-1.md"
      },
      "snapshot": null,
      "turn": 1
    },
    {
      "artifact": {
        "blob": "28af578ca04f3f3e2c9b790ed0526b03979c06f0",
        "digest": "sha256:ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7",
        "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
      },
      "author_response": {
        "digest": "sha256:365fe226ae5196ad3a9b2bb072aaac82369c6e10056020888a2941f06e7566d2",
        "path": ".aitm/stories/001/133/plan/reviews/xpr-2026-11-10-tia-plan/native/plan/2026-11-10-test-impact-analysis-implementation-plan-review-baca25051170651fc4512589bc73be80/review-baca25051170651fc4512589bc73be80-author-response-2.md"
      },
      "commit": "8aece3870c3e3e92009e6248184203e48ac8e37c",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:78f831fccc488bf6fb4451d5c5f4084f22de90fefba5ad9fc5a346fcc84bf0e7",
        "path": ".aitm/stories/001/133/plan/reviews/xpr-2026-11-10-tia-plan/native/plan/2026-11-10-test-impact-analysis-implementation-plan-review-baca25051170651fc4512589bc73be80/review-baca25051170651fc4512589bc73be80-reviewer-response-2.md"
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
        "digest": "sha256:1716e23a846a45f16b673327fca57e163a1d45b4ba85432ce49536ca7a2626ea",
        "path": ".aitm/stories/001/133/plan/reviews/xpr-2026-11-10-tia-plan/native/plan/2026-11-10-test-impact-analysis-implementation-plan-review-baca25051170651fc4512589bc73be80/review-baca25051170651fc4512589bc73be80-reviewer-response-3.md"
      },
      "snapshot": null,
      "turn": 3
    }
  ]
}
```
