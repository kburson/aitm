---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 83
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_base_commit: "e641199"
base_digest: "sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de"
final_digest: "sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee"
rounds: 2
outcome: "exhausted"
native_review_id: "review-9a11494429336f06db1d427236d5aa0e"
native_status: "accepted"
authority_assurance: "unavailable"
author_model_id: "gpt-6.1-sol"
author_effort: "high"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
native_finalization_commit: "0f0891eb690bdc2813ba9b3135356049bd43da7a"
verified_at: "2026-11-09T14:26:26+00:00"
---

# XPR review record

Native Claude cross-provider review through the project-local broker with manual invitation transport and normal commits. The finalization is scoped to this artifact.

Two rounds, four required body findings and four optional improvements. The body findings cover owner-session enrollment and same-story reviewer scope, pseudonymous locators and output privacy, visible format drift, and nested/retry/model-change qualification. The author resolved all four, and the native reviewer verified each disposition. The native finding arrays were empty, so the substantive count comes from the response bodies. [Fresh full-file retrieval audit](coverage-audit.md).

[Native terminal manifest](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-review-manifest.md) · [Task instructions](review-instructions.md). The copied native response headers retain their original timing basis. No engagement duration was inferred.

| Patch | Resulting SHA-256 | Source commit |
| --- | --- | --- |
| [patch-000.diff](patch-000.diff) | `sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de` | `e6411995f65df61da29fa737bcfcfa722a8a9265` |
| [patch-001.diff](patch-001.diff) | `sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee` | `670ce2fbe3e4b3752c38cead1b9c49283d54d591` |
| [patch-002.diff](patch-002.diff) | `sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee` | `0f0891eb690bdc2813ba9b3135356049bd43da7a` |

Replayed every patch and verified each resulting digest and the final FUR bytes.

## Native originals

- [review-9a11494429336f06db1d427236d5aa0e-author-response-1.md](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-author-response-1.md) · `sha256:a3cc3790b75b789dd5f5c3ddb15c2c7b1692bd05d71e4b1a4dbb410c28a23800`
- [review-9a11494429336f06db1d427236d5aa0e-author-startup.md](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-author-startup.md) · `sha256:886a198b6c76896d92f2c538221a415c4943604c9ade49405ca25f17a52a358b`
- [review-9a11494429336f06db1d427236d5aa0e-review-manifest.md](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-review-manifest.md) · `sha256:009b9bcd3a10db2627dbe25ac41ddabca0c867886b3ab85308450496204d5291`
- [review-9a11494429336f06db1d427236d5aa0e-reviewer-invitation.md](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-invitation.md) · `sha256:77ba6fc805189e8632c89f24a2db6f45daee7d0947fe44eafb9390205eb579c6`
- [review-9a11494429336f06db1d427236d5aa0e-reviewer-response-1.md](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-response-1.md) · `sha256:5456f93b7fe3fbfbb848614e7a9037444677d8504a6f22014d0290f3f96d8ac8`
- [review-9a11494429336f06db1d427236d5aa0e-reviewer-response-2.md](native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-response-2.md) · `sha256:4241dec77a481849e03a46cbc75e9d5c85cb5f0a0b841ddf164278ff16894689`
