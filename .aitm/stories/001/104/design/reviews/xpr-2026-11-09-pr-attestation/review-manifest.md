---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 104
artifact_path: ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md"
artifact_base_commit: "eaa2e3f06a464ec4275946add0c094f96d322c50"
base_digest: "sha256:1b9afd6e13275d1a35ef3be66c8ca98ac4186d0ce94f49257909b2731bb5c20f"
final_digest: "sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0"
rounds: 2
outcome: "exhausted"
native_review_id: "review-31cb99125142babd8d7777a8787e1d19"
native_status: "accepted"
authority_assurance: "unavailable"
author_model_id: "gpt-6.1-sol"
author_effort: "high"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
native_finalization_commit: "99342854e07345d98e42335e96b378587ad5edfd"
verified_at: "2026-11-10T04:26:26+00:00"
---

# XPR review record

Native Claude cross-provider review through the project-local broker with manual invitation transport and normal commits. The finalization is scoped to this artifact.

Claude Opus 5.5 high accepted the final 42-line artifact in round 2 without required changes. Native finalization records reviewer consensus. The independent authority verifier was unavailable. The portable outcome `exhausted` records that assurance limit and `native_status` records the broker's accepted terminal state.

The first review required explicit public attestation scope, an executable signing-job evidence handoff, and fresh-event and current-attempt job checks. The revised design preserves ordinary PR delivery, the 90% floor and behavioral tests. The broker finalized the exact accepted text. Optional wording and pin-time observations remain in the response. [Full-file retrieval audit](retrieval-audit.md).

[Native terminal manifest](native/review-31cb99125142babd8d7777a8787e1d19-review-manifest.md) · [Task instructions](review-instructions.md). The copied native response headers retain their original timing basis. No engagement duration was inferred.

| Patch | Resulting SHA-256 | Source commit |
| --- | --- | --- |
| [patch-000.diff](patch-000.diff) | `sha256:1b9afd6e13275d1a35ef3be66c8ca98ac4186d0ce94f49257909b2731bb5c20f` | `eaa2e3f06a464ec4275946add0c094f96d322c50` |
| [patch-001.diff](patch-001.diff) | `sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0` | `eb8ab8f471f33cdc52c1e67e01283ab8bc50cdd2` |
| [patch-002.diff](patch-002.diff) | `sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0` | `99342854e07345d98e42335e96b378587ad5edfd` |

Replayed each zero-context patch with `git apply --unidiff-zero --allow-empty` and verified each resulting digest and the final FUR bytes.

## Native originals

- [review-31cb99125142babd8d7777a8787e1d19-author-response-1.md](native/review-31cb99125142babd8d7777a8787e1d19-author-response-1.md) · `sha256:a60de9262af58346d117e1ce1f890b771cceb4f9b880e1e18f6c6a7966803085`
- [review-31cb99125142babd8d7777a8787e1d19-review-manifest.md](native/review-31cb99125142babd8d7777a8787e1d19-review-manifest.md) · `sha256:3814ecaa208041b529f81b0dd171b1ca71ab9831a2f61893d3e7b356d90a8008`
- [review-31cb99125142babd8d7777a8787e1d19-reviewer-response-1.md](native/review-31cb99125142babd8d7777a8787e1d19-reviewer-response-1.md) · `sha256:a1bd03411c67e09f36b0303f540cc030e997e754d4b9189946c29697e316a291`
- [review-31cb99125142babd8d7777a8787e1d19-reviewer-response-2.md](native/review-31cb99125142babd8d7777a8787e1d19-reviewer-response-2.md) · `sha256:3831d04637a763224e6db7b63ada31527e0badb914c863e7a77ba18069e2f222`
