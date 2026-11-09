---
schema: "aitm.review-manifest/v0"
level: "spr"
story: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "73210b6da93942f06a0d6616cf5df02eaf64180c"
artifact_base_blob: "965dee7bb7043a43c607cb8502a45ce33b39d649"
base_digest: "sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9"
final_digest: "sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1"
rounds: 3
outcome: "exhausted"
execution: "manual"
authority_assurance: "declared-manual"
reviewer_model_id: "gpt-6.1-sol"
reviewer_effort: "high"
reviewer_session: "01a1bebb-3dd5-7422-8d7e-58de85638746"
author_model_id: "gpt-6-astra"
author_effort: "xhigh"
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
verified_at: "2026-11-09T05:37:34Z"
---

# Core design manual SPR review record

## Outcome

Exhausted after 3 rounds, with 14 findings resolved as recorded below. Final reviewer acceptance binds exactly the raw FUR digest above. This is manual same-provider consensus; it does not constitute XPR, implementation acceptance, master-plan review, native-tool acceptance or story closure.

## Participants and procedure

The owner explicitly selected the same manual SPR process used for story 01, with GPT-6 Astra / xhigh as author and GPT-6.1 Sol / high as reviewer, after the separate native attempt was blocked. A fresh independent Codex reviewer session read the full current FUR and owner/architecture context. Its session differs from the author, the SAR reviewer and the unsuccessful native CLI reviewer. The author alone revised the FUR and made the temporary round commits. The original handoff allows manual SPR and requires complete response pairs, per-author patches and reconstruction. Five rounds is the cap; this review exhausted within it.

The selected model/effort settings are supported by the explicit reviewer launch and observed author/reviewer turn contexts. Session fields here are observed Codex session IDs, recorded as manual provenance; they are not native runtime fingerprints or independent attestations. No broker, native join/submit/finalize, setup or hook repair was used for this manual level. The owner-authorized alternative is recorded explicitly rather than represented as recovery of the failed native attempt.

Started/submitted timestamps are recorded for each actual turn. They bound review/response work, not a claim of continuously engaged agent-hours. Setup, failed native launches, publication and cleanup are outside these spans. No registration timestamp is reused as a later turn start. No story timing events or unrelated context documents are rewritten by this review.

## Base and prior review lineage

The manual SPR starts from published SAR commit 73210b6da93942f06a0d6616cf5df02eaf64180c with raw digest sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9. SAR exhausted in three rounds with 21 findings resolved. Its separate record retains the original base 981b8d77e2e988e9ec3f79768c7c9728cb66c11a (raw sha256:2a31083b0095233d9d2d8ba1bc11d3054bd43fe977b6f90376eda9e8593d4026), and the owner-directed integrated upstream 7e829d53c39bb100ab6761ea2861c6720a891e70 (raw sha256:aceb88b37eb36d2bc08b48e639aef4784de2949e95307ead02e5dc13ac9ccbea). SAR patch 000 remains unchanged. This SPR patch 000 creates the post-SAR base, which already includes those upstream additions. They are not credited to SPR findings.

Every SPR round reviews the full current document, including review events, planning/review timing, backfill provenance, review CLI and acceptance. Each level accepts only its own reviewed bytes; SAR does not retroactively approve SPR revisions. The current raw digest and patches do not claim implementation of the future canonical-content contract.

## Patches and reconstruction

Apply patches in numerical order to an empty directory, retaining repository-relative paths. Patch 000 creates the base; each subsequent patch records its author turn. A zero-byte patch is a no-change acknowledgement (git apply --allow-empty). Source commits are provenance only; the files reconstruct every revision without those Git objects.

| Patch | Resulting raw SHA-256 | Patch bytes | Source commit |
| --- | --- | --- | --- |
| [patch-000.diff](patch-000.diff) | sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9 | 96014 | 73210b6da93942f06a0d6616cf5df02eaf64180c |
| [patch-001.diff](patch-001.diff) | sha256:865cdcef8edfaa472fe31ae05425f99e6af26e00f8e238b59d42e045149cf257 | 66982 | d3be48feb17069de0057de9d90c1993a21eed39b |
| [patch-002.diff](patch-002.diff) | sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1 | 39513 | 2d8899965a30d020e5e72004ad0af4b6442aed95 |
| [patch-003.diff](patch-003.diff) | sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1 | 0 | 1594683563e681b7db7297fc4f3a2b4da4c773c0 |

## Finding dispositions

All ten round 1 findings and all four round 2 findings were accepted and resolved. Round 3 read the full current file, verified the remaining dispositions and accepted with no new required changes or optional suggestions. The six response files preserve the findings and rationale. Round 3's author patch is empty.

## Declined and flagged for owner

None. No required finding was declined or deferred and no new owner decision was needed. Existing expansion-completion interpretation, second-trip cap, review-depth/sequence policy and GitHub every-push audit mechanism remain open. This task stops before XPR.

## Calls changed or clarified

Specified shared-history continuity and deterministic repair, cooperative ref/worktree exclusion with explicit external-race limits, one graduation intent per draft, blocking expansion reservations, authoritative managed-start ordering, immutable verification inputs, effective review/closure prerequisites, exact-content multi-level policy completion, engagement eligibility, stable bootstrap/adoption and evidence-only recovery. Added typed boundary/execution facts so a rebuild can reproduce these decisions. These are builder-level mechanisms under the accepted architecture; owner numerical limits and open choices remain unchanged. The design's acceptance cases require later implementation proof; this document review does not claim those runtime tests have passed.

## Blocked native attempt retained

[blocked-native-attempt.md](blocked-native-attempt.md) records the separate failed review ID, input, selected participants, errors and public-original hashes. Its original worktree/branch, setup and private recovery evidence remain intact. 13 native/setup file digests and its HEAD/branch were compared before and after this manual cycle. No native reviewer joined or submitted; its state is not upgraded, abandoned or superseded by this manual acceptance. Private scratch, hook tokens and provider handles are not published.

## Verification and publication boundary

- Parsed every response header: schema, role, level, story, round, model/effort, distinct stable sessions, true turn timestamp basis, path, base and raw digest.
- Verified every reviewer input, author output and finding/disposition mapping against the corresponding committed FUR version.
- Applied the complete patch chain in a temporary directory; compared every intermediate and final version byte for byte and by SHA-256; removed the replay directory.
- Checked FUR relative links and FUR/Markdown whitespace. Patch context markers are retained as Git-generated syntax and checked by replay. No implementation tests apply to this documentation-only review.
- Checked all round commits change only the FUR and this review folder; prior SAR/context records remain unchanged. Verified native preservation separately.
- Publication copies only this FUR and manual SPR folder into the refreshed planning checkout, followed by an exact-path commit and fast-forward push. The containing planning commit identifies publication without a self-referential hash here.
- XPR is not started. The temporary manual worktree can be archived after publication; the separate blocked native worktree must remain retained.
