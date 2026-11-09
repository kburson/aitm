---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "bcacb1378ca2cf268bb194cdf80f4fe21f155b2d"
artifact_base_blob: "767b7bbf82da157494fc94feb5ebf3092c97ed55"
base_digest: "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d"
final_digest: "sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7"
rounds: 3
outcome: "exhausted"
native_review_id: "review-48ae3de9ffa0067249b56573a8a3b1c8"
native_status: "accepted"
commit_mode: "normal"
authority_assurance: "unavailable"
author_model_id: "gpt-6-astra"
author_effort: "xhigh"
author_session: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
reviewer_session: "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8"
session_identity_kind: "native-fingerprint"
native_revision_commit: "013cdf2fd4ea753ae94cbb434d146fe5a284f61e"
native_finalization_commit: "64d04e178616ee5fa3b077ae0ac1d50c08f7a910"
verified_at: "2026-11-09T13:10:14Z"
---
# XPR review record

## Outcome and authority
Exhausted in 3 rounds with 5 sealed findings. Native reviewer consensus and author finalization bind exactly the final raw digest above. This record accepts only the named document; it does not authorize implementation, epic closure or a trunk merge.
Used installed ai-peer-review 0.4.1, native Claude, project-local broker, manual invitation transport and normal commit mode. The requested author/reviewer selections are recorded above. Native authority assurance is unavailable, with declared participant/model evidence; this is not independent execution attestation. Participant fingerprints are not raw private provider handles.

## Reconstruction
Apply patches in numerical order to an empty directory; empty patches use git apply --allow-empty. Every intermediate and final version was checked byte for byte against its recorded artifact and by raw SHA-256. Source commits are provenance; reconstruction does not depend on retaining their Git objects.
| Patch | Resulting raw digest | Bytes | Source commit |
| --- | --- | --- | --- |
| [patch-000.diff](patch-000.diff) | sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d | 141558 | bcacb1378ca2cf268bb194cdf80f4fe21f155b2d |
| [patch-001.diff](patch-001.diff) | sha256:3355a89fdfd38e16b9f4aeb37fc8fb368ea74ce8b7e608f0504b67a2e9288253 | 50686 | 86ac9caf47c95d6443e329759ede387c2cfe37e6 |
| [patch-002.diff](patch-002.diff) | sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7 | 31665 | 013cdf2fd4ea753ae94cbb434d146fe5a284f61e |
| [patch-003.diff](patch-003.diff) | sha256:5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7 | 0 | 64d04e178616ee5fa3b077ae0ac1d50c08f7a910 |

## Native mapping and timing
Portable reviewer digests retain native inputs. Portable author digests name outgoing artifacts from native artifact history; native protected author headers name incoming artifacts. The final author acknowledgement is explicitly post-finalization and produces no FUR edit. Native final_commit can name the last artifact revision, so the actual finalization commit is recorded separately.
Native started_at fields may reuse participant registration across rounds. The exports use the first exact role claim where available, otherwise the prior submitted response as a qualified outer bound. These spans are not measured continuous engagement or necessarily response-writing duration; setup, waiting, pre-claim reading and publication remain exclusions/Unknown unless separately observed. No story timing events are silently rewritten by this export.
| Response | Start basis | Public anchor |
| --- | --- | --- |
| [reviewer-response-1.md](reviewer-response-1.md) | claim | native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-review-manifest.md#claim-claim-806d7033-31e1-4ab8-bde8-14f1a2e289c7 |
| [author-response-1.md](author-response-1.md) | claim | native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-review-manifest.md#claim-claim-05881bb9-3cac-48c1-83e0-e547865df3f1 |
| [reviewer-response-2.md](reviewer-response-2.md) | prior-submit | author-response-1.md |
| [author-response-2.md](author-response-2.md) | prior-submit | reviewer-response-2.md |
| [reviewer-response-3.md](reviewer-response-3.md) | prior-submit | author-response-2.md |
| [author-response-3.md](author-response-3.md) | prior-submit | reviewer-response-3.md |

## Native original hashes
| File | Raw SHA-256 |
| --- | --- |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-author-response-1.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-author-response-1.md) | sha256:0778bc3c23bb452053fd2eaba8d2e7a3705a175ffed86ecd93744d6378009155 |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-author-response-2.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-author-response-2.md) | sha256:ab4f112492d0f7854e1003f973867ef7c7336d4d5d7d866cb183ce6b5d74449e |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-author-startup.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-author-startup.md) | sha256:aa393a3db06f2131f14b20a56d8b490cc4a749b5f9b605bf2ca253d89aa21a0c |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-review-manifest.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-review-manifest.md) | sha256:a972387dbfd65970fa35e10baa4f5d76b4ba880ec2df3307d51bc28aa98c6f59 |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-invitation.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-invitation.md) | sha256:ef162ca9cfcba3b6f518484617cc31282ab26a0218dabddfd93e8f6d95e473a0 |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-1.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-1.md) | sha256:474fa711f89ebf292af1f2de06f9b6eaf3dbda0b18ccb339742cfd9fd89ad191 |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-2.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-2.md) | sha256:7c6dc37adac0d6540910353c33de06d4d4361683f24e9be87cd2563ff3467b52 |
| [review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-3.md](native/spec/2026-11-09-core-design-review-48ae3de9ffa0067249b56573a8a3b1c8/review-48ae3de9ffa0067249b56573a8a3b1c8-reviewer-response-3.md) | sha256:a8fc63ffa0939b654a08e4b0d038259d6760ccc00d0d96637c48296b0f7439ae |

## Verification and publication boundary
Validated submitted response hashes against the terminal manifest, model/effort and participant continuity, complete sealed finding dispositions, per-turn input/output digests, exact final acceptance and unchanged native originals. Replayed all patches and compared every intermediate byte sequence. Check Markdown whitespace/links and scoped changes before import; preserve Git's single-space blank-context patch syntax and verify patches by replay. No product implementation tests are claimed.
Publication imports only the final FUR and this review folder into refreshed planning after its base/content preconditions are checked. The containing planning commit identifies publication without a self-referential manifest hash. Earlier levels accept their own bytes and do not retroactively approve these revisions.

## Separate validation, dispositions and retained choices

Owner authorization: 2026-11-09 separate full-file design and plan validation, Astra-6/ExtraHigh author and Opus 5.5/high reviewer, publish and stop before implementation. This independent record starts from planning bcacb1378ca2cf268bb194cdf80f4fe21f155b2d and retains the prior accepted design XPR unchanged. It is not a fourth round in that old review or a retroactive waiver.

Required findings: R1-F001 kind/split/common planning guards; R1-F002 source-review evidence/independence; R1-F003 pivot/reconfiguration acceptance; R2-F001 decomposed-child source/coverage/estimate; R2-F002 actual-corpus migration. All five were resolved and confirmed in round 3. For decomposition coverage the reviewer explicitly accepted the author's bounded own-document alternative; inherited parent-plan-section acceptance is unsupported in M1, not silently selected. Seven earlier unsealed optional suggestions were adopted; the final unsealed wording suggestion was declined as nonblocking, with rationale in the final acknowledgement. Sealed finding count remains five.

Changed builder calls and exact author reasoning are retained in the response pairs. Open owner choices remain expansion completion, second-trip cap, global document-review depth/sequence, hosted every-push audit and later provider/harness/packaging decisions. No global policy, code, production adoption or epic state changed. The downstream plan requires reconciliation and its own full-file validation.

See the [verified full-file coverage](coverage-audit.md), [immutable pre-start instructions](review-instructions.md) and [design retrospective](retrospective.md). Retrieval was checked before finalization, not inferred from acceptance. The blocked native SPR and uncertain first design XPR remain retained separately; the new review does not repair or supersede them. All 13 blocked-SPR baseline file hashes were rechecked unchanged during this task.
