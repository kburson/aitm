---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "63c7e85d66153db6dc03e5aa41fc8d8191845632"
artifact_base_blob: "a21256d003ec73b3e278038c42d4051171525b80"
base_digest: "sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1"
final_digest: "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d"
rounds: 3
outcome: "exhausted"
native_review_id: "review-095b15003bea70559dd3ce3bb285292a"
native_status: "accepted"
commit_mode: "normal"
authority_assurance: "unavailable"
author_model_id: "gpt-6-astra"
author_effort: "xhigh"
author_session: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
reviewer_session: "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01"
session_identity_kind: "native-fingerprint"
native_revision_commit: "2389091675d6567b5073740812593a4e71d17447"
native_finalization_commit: "70af9eb047d7f4bc86e46755e6ed08dbe3970224"
verified_at: "2026-11-09T06:24:47Z"
---
# XPR review record

## Outcome and authority
Exhausted in 3 rounds with 6 sealed findings. Native reviewer consensus and author finalization bind exactly the final raw digest above. This record accepts only the named document; it does not authorize implementation, epic closure or a trunk merge.
Used installed ai-peer-review 0.4.1, native Claude, project-local broker, manual invitation transport and normal commit mode. The requested author/reviewer selections are recorded above. Native authority assurance is unavailable, with declared participant/model evidence; this is not independent execution attestation. Participant fingerprints are not raw private provider handles.

## Reconstruction
Apply patches in numerical order to an empty directory; empty patches use git apply --allow-empty. Every intermediate and final version was checked byte for byte against its recorded artifact and by raw SHA-256. Source commits are provenance; reconstruction does not depend on retaining their Git objects.
| Patch | Resulting raw digest | Bytes | Source commit |
| --- | --- | --- | --- |
| [patch-000.diff](patch-000.diff) | sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1 | 122844 | 63c7e85d66153db6dc03e5aa41fc8d8191845632 |
| [patch-001.diff](patch-001.diff) | sha256:a21126bb83c00fcc6eda84d7a603c030c926f7667d700acbab12291488a94102 | 87061 | 24421786443106ae83dc85e955db6ec133fa3a10 |
| [patch-002.diff](patch-002.diff) | sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d | 32170 | 2389091675d6567b5073740812593a4e71d17447 |
| [patch-003.diff](patch-003.diff) | sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d | 0 | 70af9eb047d7f4bc86e46755e6ed08dbe3970224 |

## Native mapping and timing
Portable reviewer digests retain native inputs. Portable author digests name outgoing artifacts from native artifact history; native protected author headers name incoming artifacts. The final author acknowledgement is explicitly post-finalization and produces no FUR edit. Native final_commit can name the last artifact revision, so the actual finalization commit is recorded separately.
Native started_at fields may reuse participant registration across rounds. The exports use the first exact role claim where available, otherwise the prior submitted response as a qualified outer bound. These spans are not measured continuous engagement or necessarily response-writing duration; setup, waiting, pre-claim reading and publication remain exclusions/Unknown unless separately observed. No story timing events are silently rewritten by this export.
| Response | Start basis | Public anchor |
| --- | --- | --- |
| [reviewer-response-1.md](reviewer-response-1.md) | claim | native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-review-manifest.md#claim-claim-ce63b667-45f6-432b-bfee-82d2cf64d368 |
| [author-response-1.md](author-response-1.md) | claim | native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-review-manifest.md#claim-claim-1001c259-c531-4991-9eb3-ea3ea5d4799f |
| [reviewer-response-2.md](reviewer-response-2.md) | prior-submit | author-response-1.md |
| [author-response-2.md](author-response-2.md) | prior-submit | reviewer-response-2.md |
| [reviewer-response-3.md](reviewer-response-3.md) | prior-submit | author-response-2.md |
| [author-response-3.md](author-response-3.md) | prior-submit | reviewer-response-3.md |

## Native original hashes
| File | Raw SHA-256 |
| --- | --- |
| [review-095b15003bea70559dd3ce3bb285292a-author-response-1.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-author-response-1.md) | sha256:8fe04423a83ddd3fdbe28a23acabbb4f66f223e849d0594fa83f9bfec960fd0f |
| [review-095b15003bea70559dd3ce3bb285292a-author-response-2.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-author-response-2.md) | sha256:bf7423adb219ee80e95ab44a4f02f9a4fda67459a94a649558cbb2e49362f866 |
| [review-095b15003bea70559dd3ce3bb285292a-author-startup.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-author-startup.md) | sha256:3aa0206f785f1d02f584454ed68fb75723d6cce2b8a4410c96e4181fdcd0d999 |
| [review-095b15003bea70559dd3ce3bb285292a-review-manifest.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-review-manifest.md) | sha256:6557a601d84ec3bf3671b3dd246b450caf482ae5c3c29df4167dad1033d67cce |
| [review-095b15003bea70559dd3ce3bb285292a-reviewer-invitation.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-invitation.md) | sha256:ba88e4b0d937d8f06172da4641cb9da40461e2fca5a5544a5616a66f709ed9e5 |
| [review-095b15003bea70559dd3ce3bb285292a-reviewer-response-1.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-1.md) | sha256:d8ab9bca056aaf98da9bc2e3fe1dcd27abe46b70370f3a674a959f7c68aa1575 |
| [review-095b15003bea70559dd3ce3bb285292a-reviewer-response-2.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-2.md) | sha256:3bc7995e2e452a255d2b4649c5696ddb1c6c6432937825863bca243937daabf7 |
| [review-095b15003bea70559dd3ce3bb285292a-reviewer-response-3.md](native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-3.md) | sha256:fcffded238d61cc766f94b96534c9b84a9d988b2626d7ad143568171281b5298 |

## Verification and publication boundary
Validated submitted response hashes against the terminal manifest, model/effort and participant continuity, complete sealed finding dispositions, per-turn input/output digests, exact final acceptance and unchanged native originals. Replayed all patches and compared every intermediate byte sequence. Check Markdown whitespace/links and scoped changes before import; preserve Git's single-space blank-context patch syntax and verify patches by replay. No product implementation tests are claimed.
Publication imports only the final FUR and this review folder into refreshed planning after its base/content preconditions are checked. The containing planning commit identifies publication without a self-referential manifest hash. Earlier levels accept their own bytes and do not retroactively approve these revisions.

## Dispositions, calls and prior levels
All six sealed required findings were accepted and resolved: round 1 F001–F004 (verification lane, kind/slot matrix, configuration classes, root-anchored ignore); round 2 R2-F001–R2-F002 (honest captured-export/contained assurance, explicit preparation, anchored numbering identity). Round 3 requested no required changes. Full response bodies carry the item-by-item dispositions. The retained unsubmitted attempt's U1–U10 are separately attributed in author response 1 and [retained-attempt.md](retained-attempt.md).

Round-3 optional suggestions are deferred to implementation planning without changing the accepted bytes: locate prepared-environment metadata explicitly as clone-local scratch/cache metadata, and distinguish environment provisioning from execution admission's prepared phase in naming and tests. They are optional, not unresolved required findings. The implementation plan must state these routine choices.

Changed provisional calls include shared-ref CAS number allocation instead of a designated allocator; explicit typed Done outcomes and delivery/signoff transaction; local ref freshness and bounded publication defaults; root-anchored cache exclusion; captured-export assurance as an explicit bounded policy distinct from OS containment; offline/hash-verified environment preparation. Author response 1 preserves strict admission before local test dispatch and explains its cost. All are traceable in patches and responses.

Owner-open choices remain open: expansion completion interpretation, second-trip cap, global review-depth matrix, GitHub every-push audit, provider/harness questions and full-install distribution name. This assignment's authorized review sequence does not settle global policy. No runtime acceptance tests or implementation are claimed.

Prior core SAR publication: 73210b6da93942f06a0d6616cf5df02eaf64180c, raw digest d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9. Prior manual SPR publication: 63c7e85d66153db6dc03e5aa41fc8d8191845632, raw digest f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1. Those levels accept their own versions. Native XPR accepts this final version under the owner's scoped assignment, without retroactively reattesting earlier levels.
