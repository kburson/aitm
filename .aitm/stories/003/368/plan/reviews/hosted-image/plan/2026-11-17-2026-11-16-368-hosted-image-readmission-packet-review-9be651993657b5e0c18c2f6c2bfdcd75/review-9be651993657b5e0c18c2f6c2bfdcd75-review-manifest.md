<!-- ai-peer-review-template version="1" digest="sha256:e53bf4d9991ae94a699fede1d62fd90324e45923de951babcb8d9ad237900bd9" -->

# Review manifest

Mode: `normal`

```json
{
  "acceptance_basis": "reviewer-consensus",
  "artifact_history": [
    {
      "blob": "d7fff3c875c4c7b3abea3584a467b80fcbd9df40",
      "commit": "3a5cdce226af4c820df177c1d5023c7b542bdd99",
      "digest": "sha256:8c06223244f85a8f84140101811d3fdec55d9187d9d92677b270230fee24692e",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-image-readmission-packet.md",
      "snapshot": null,
      "turn": 0
    },
    {
      "blob": "b5d244ba18db692df4be428aee138ebb68e79178",
      "commit": "6df7bf7333df62371fb15e80574fc342551927af",
      "digest": "sha256:1986cd3c8af25fef68f435877531ef13f214cb49ac3c1be117ce0b33acefecf8",
      "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-image-readmission-packet.md",
      "snapshot": null,
      "turn": 1
    }
  ],
  "artifact_path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-image-readmission-packet.md",
  "authority": {
    "acceptance_attestation": null,
    "policy": "unavailable",
    "verifier": null
  },
  "authority_assurance": "unavailable",
  "claims": [
    {
      "claim_id": "claim-ece409c1-e79b-482f-87c2-3cef76eda167",
      "claimed_at": "2026-11-17T05:39:42.199Z",
      "expires_at": "2026-11-17T13:39:42.199Z",
      "host": "claude-code",
      "last_activity_at": "2026-11-17T05:39:42.199Z",
      "role": "reviewer",
      "session_fingerprint": "sha256:d6251fd891350239116342c2c2cb3890ce5ea43fdbd601aaf99b554095c96576"
    },
    {
      "claim_id": "claim-bee16beb-6e7a-482f-accb-ecc0eda2df05",
      "claimed_at": "2026-11-17T05:41:36.929Z",
      "expires_at": "2026-11-17T13:41:36.929Z",
      "host": "codex",
      "last_activity_at": "2026-11-17T05:41:36.929Z",
      "role": "author",
      "session_fingerprint": "sha256:76db90c482a2d4b62a9e997e0578af0ecf27a2a2853532bf57af0df506c86756"
    }
  ],
  "commit_mode": "normal",
  "final_commit": "6df7bf7333df62371fb15e80574fc342551927af",
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
        "joined_at": "2026-11-17T05:38:48.643Z",
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
        "event_log_digest": "sha256:341b8549ed24c8ba347b9a3a3dab3ab59ce20dfb08cb0b886336e9728c59c7e5",
        "predecessor_review_id": null,
        "reciprocal_receipt_digest": null,
        "record_id": "review-9be651993657b5e0c18c2f6c2bfdcd75",
        "recovery_claim_digest": null,
        "recovery_id": null,
        "recovery_ordinal": 0,
        "review_id": "review-9be651993657b5e0c18c2f6c2bfdcd75",
        "root_review_id": "review-9be651993657b5e0c18c2f6c2bfdcd75",
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
      "joined_at": "2026-11-17T05:38:48.643Z",
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
          "fingerprint": "sha256:d6251fd891350239116342c2c2cb3890ce5ea43fdbd601aaf99b554095c96576",
          "source": "environment-declaration"
        }
      },
      "host": "claude-code",
      "identity_source": "runtime",
      "joined_at": "2026-11-17T05:39:42.163Z",
      "model_display": "claude-opus-5-5",
      "model_id": "claude-opus-5-5",
      "provider": "anthropic",
      "role": "reviewer",
      "session_fingerprint": "sha256:d6251fd891350239116342c2c2cb3890ce5ea43fdbd601aaf99b554095c96576"
    }
  },
  "record_id": "review-9be651993657b5e0c18c2f6c2bfdcd75",
  "recoveries": [],
  "residual_risk": [
    "human-authority-unavailable"
  ],
  "review_id": "review-9be651993657b5e0c18c2f6c2bfdcd75",
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
  "startup_commit": "3a5cdce226af4c820df177c1d5023c7b542bdd99",
  "status": "accepted",
  "supplements": [],
  "turns": [
    {
      "artifact": {
        "blob": "b5d244ba18db692df4be428aee138ebb68e79178",
        "digest": "sha256:1986cd3c8af25fef68f435877531ef13f214cb49ac3c1be117ce0b33acefecf8",
        "path": ".aitm/stories/003/368/plan/2026-11-16-368-hosted-image-readmission-packet.md"
      },
      "author_response": {
        "digest": "sha256:339bd596e4de438550aa2fbf6ee0cd0237dc283bced05fe624f52b1645762e97",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-image/plan/2026-11-17-2026-11-16-368-hosted-image-readmission-packet-review-9be651993657b5e0c18c2f6c2bfdcd75/review-9be651993657b5e0c18c2f6c2bfdcd75-author-response-1.md"
      },
      "commit": "6df7bf7333df62371fb15e80574fc342551927af",
      "decision": "revisions-requested",
      "finding_ids": [],
      "reviewer_response": {
        "digest": "sha256:381c74c87f03e41ce5dc9597e70ce6f88e31ddd525f3cb2abf4498d60fb8f81a",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-image/plan/2026-11-17-2026-11-16-368-hosted-image-readmission-packet-review-9be651993657b5e0c18c2f6c2bfdcd75/review-9be651993657b5e0c18c2f6c2bfdcd75-reviewer-response-1.md"
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
        "digest": "sha256:3f664523600ca94dcffaebe86af30709578bc206ce21046127513dd9497d6bca",
        "path": ".aitm/stories/003/368/plan/reviews/hosted-image/plan/2026-11-17-2026-11-16-368-hosted-image-readmission-packet-review-9be651993657b5e0c18c2f6c2bfdcd75/review-9be651993657b5e0c18c2f6c2bfdcd75-reviewer-response-2.md"
      },
      "snapshot": null,
      "turn": 2
    }
  ]
}
```
