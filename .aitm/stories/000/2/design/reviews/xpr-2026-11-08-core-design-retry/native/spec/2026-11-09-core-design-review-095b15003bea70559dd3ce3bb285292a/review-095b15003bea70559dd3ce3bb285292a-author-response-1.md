<!-- ai-peer-review-template version="1" digest="sha256:f81da1894a46ceb20866070833b4e99ef536ef633542b418783d29e6a981dbd8" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-095b15003bea70559dd3ce3bb285292a"
role: "author"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_commit: "63c7e85d66153db6dc03e5aa41fc8d8191845632"
artifact_blob: "a21256d003ec73b3e278038c42d4051171525b80"
artifact_digest: "sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  model_display: "gpt-6-astra"
  session_fingerprint: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
  identity_source: "runtime"
started_at: "2026-11-09T05:57:25.687Z"
submitted_at: "2026-11-09T06:11:17.385Z"
finding_ids: []
answered_finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004"]
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revised the full core design for all four sealed round-1 findings and all four optional suggestions. The required changes specify a usable captured-input verification lane, explicit spike/epic guard substitutions, the split between committed policy and routing-anchor adoption, and root-only store ignore behavior.

I also evaluated the ten observations in the retained, unsubmitted response from independent attempt review-c48ef23713ec789fe0b762af03d3f2b9. They are additional author input, not findings submitted in this review. Their provenance and dispositions appear separately below. This revision preserves owner decisions and the open expansion-completion, second-trip-cap, global review-depth and hosted-audit choices. It does not implement the core or claim any proposed runtime acceptance test passed.

## Finding dispositions

- **R1-F001 — accepted.** Added the M1 verification lane: a private export outside registered worktrees, copied captured source and explicitly declared [test] inputs, no mutable sharing with the checkout, read-only source and prepared dependency roots, separate outputs, platform-enforced process-tree containment and network denial, capability probing, and an unavailable/diagnostic result when enforcement cannot be established. macOS uses sandbox-exec profiles; Linux uses namespace/mount/privilege restrictions. Added the missing input declaration and explicit environment preparation/execution boundary. The default uv command uses its captured prepared environment with no-sync/offline behavior; the lock is validated before sealing, rather than incorrectly claiming no-sync validates it. M1 must prove the real authoritative lane on both supported host fixtures. The no-worktree rule now explicitly concerns registered story worktrees.
- **R1-F002 — accepted.** Added the kind-by-slot matrix. Story/defect retain source commits and test receipts; spikes use a deliverable binding, research/input JIT, registered immutable deliverable, typed deliverable-validation receipt and review/archive evidence; epics use aggregate child evidence and have no implementation clock/JIT/PR/test subprocess. Spikes still pass through Test and use the same Develop-to-effective-review implementation clock. Added bind --deliverable, deliverable validate and its event.
- **R1-F003 — accepted.** Classified default-repository/store anchors and routing separately from tip-effective mode, limits, extensions, tests and complete review-policy definition. Anchor changes require explicit verified reconfiguration; workflow policy is evaluated from the pinned validated default-branch commit without per-clone adoption. Aligned the ambiguous routing/policy wording. The allocation authority mentioned in the suggested classification was separately simplified as described under U7, so it is no longer a per-clone adopter setting.
- **R1-F004 — accepted.** Init writes only /.aitm/. Existing foreign patterns are preserved and an unanchored .aitm/ pattern is diagnosed. Nested fixture trees remain trackable.

Optional suggestions:
- **O1 — accepted:** renamed expansions_per_story to expansions_per_attempt, retaining the numerical limit and fresh-attempt semantics.
- **O2 — accepted:** core.state.changed now names every state-changing operation and carries terminal/disposition/replacement facts. The same event family covers sign-off, reopening and trip/pivot/related-story edges.
- **O3 — accepted as a representation refinement:** future shared metadata records a stable worktree ID/display label, while physical paths remain clone-local. The required last-worktree field is retained; historical native/manual originals and legacy metadata are not rewritten.
- **O4 — accepted:** discard atomically removes the live draft directory, writes an entity-bound tombstone/event, and retains its last tree/attachment provenance in Git. Checked suffixes prevent display-name collisions; stable entity/operation identity governs retry.

## Changes made

The first independent XPR's reviewer wrote a draft but its native submission failed before any finding IDs were sealed. The failure was caused by two unignored bookkeeping files I created during its reviewer turn, not by an artifact edit by that reviewer. I preserved those files outside the checkout and verified the exact original HEAD/index/branch/worktree boundary was restored. The package then refused same-session launch resume because its earlier launch outcome remained unknown. The normal broker recovery did not resolve that manual-launch ledger. The old attempt remains intact and unsubmitted; this is the installed procedure's separate fresh-XPR route, not acceptance or supersession of the old one.

The following U labels refer only to that unsubmitted draft's numbered observations. They are not added to this review's sealed finding IDs:

| Prior observation | Author evaluation / disposition in this revision |
| --- | --- |
| U1: core-only time-trip proof | Accepted clarification. Defined ActivityProducerRegistration and the supported measurement/ingestion contract; core ships CLI/tool observations, while a deterministic conforming fixture proves confirmed-overrun logic. A core-only live install without a qualifying producer reports Unknown/possible overrun, not fabricated engagement. Goal and acceptance wording now agree. |
| U2: unspecified test lane | Addressed together with R1-F001; required actual platform proof remains future implementation work. |
| U3: shared pre-dispatch admission for local tests | Accepted the offered clarification alternative, not the proposed optimistic replacement. Stated the concrete additional property: prevent a managed launch after a stop already precedes it in the shared order. Rejecting a receipt at later publication cannot undo that execution. This preserves the explicit prior SPR resolution; costs are visible and local-only admission remains local. |
| U4: terminal model | Accepted. Defined Done dispositions/replacement fields, supersede/duplicate command routes and atomic signoff Review-to-Done behavior. Unverified remains a clearly separate advisory historical outcome and never means delivered. The signed-off predicate checks the proposed same-transaction sign-off, avoiding a circular prerequisite. |
| U5: publication before anchor | Accepted. Fresh init prepares/retains the proposed store locally; only the post-config-landing rerun publishes and protects it. Rejected/edited proposals therefore leave no protected remote orphan. Missing retained root objects produce explicit bootstrap recovery/reconfiguration rather than trust in an unanchored branch. Existing published histories still require continuity rules. |
| U6: read budget versus refresh | Accepted. Read-only queries use pinned validated local refs and disclose freshness; --refresh opts into network validation. Mutation preflight refresh remains. The warm-read budget includes interpreter start; lazy CLI/model/extension loading is an explicit implementation constraint. |
| U7: separate local allocator service | Accepted simplification. Shared-ref CAS/publication is the local-number allocation authority. Any clone may propose an unissued number; replay rechecks the same semantic intent/entity reservation and reallocates before exposure. No separate designated allocator/takeover protocol or undefined routing service remains. Updated init/store/migration and acceptance language consistently; existing issued/provider IDs never change. |
| U8: publication default | Accepted. Mutating commands attempt bounded publication by default for a configured remote; uncertainty yields the pending result while retaining local work. Mandatory shared-order actions remain ineligible until publication. Read-only/local-only behavior and sync --push are explicit. |
| U9: story commit tags | Accepted. Defined exact [#<positive decimal story ID>] subject-prefix parsing on recorded nonempty source changes. Source commit evidence is retained through delivery mapping; a squash/rebase target message is not the authority. |
| U10: store topology | Accepted. M1 uses the code clone's Git common directory for local planning objects/ref/locks/index/worktree checks. Its configured planning remote may be a separate repository. Removed the implied unconfigurable separate local/bare-store mode. |

The prior draft's optional build-order suggestion belongs in the implementation plan, which the owner has now separately authorized after design acceptance. The configuration's exact serialized schema remains a builder concern constrained by the named required fields/classes; no placeholder becomes a valid trust anchor. Paragraph reformatting is not required for this content revision. Stable operation-ID retry semantics now explicitly avoid duplicate refused-command records.

For round 2, review the **entire current FUR**, including all U-derived edits and acceptance rows, against the parent architecture and owner decision record. In particular, check the verification lane's feasibility and declared limitations, the shared-allocation change, bootstrap ordering, and kind-specific effective-pass rules. Do not restrict the review to the four sealed findings or a patch.

## Declined changes and rationale

No sealed required finding is declined or deferred. The optional optimistic-admission alternative in U3 is not adopted because it changes the launch-stop property; the requested alternative explanation is supplied. No owner-open numerical, expansion-boundary or global review-policy choice is resolved here. The owner has separately authorized planning work after accepted design publication, not implementation.

## Verification

- Read the complete submitted reviewer response and checked the four findings against the FUR, its accepted parent architecture and decision record.
- Checked every named U observation against the retained unsubmitted draft and kept that provenance separate from this native round.
- Applied asserted exact-text edits to the FUR only, plus this author response body; native protected headers and reviewer originals are unchanged.
- Checked Markdown whitespace, FUR frontmatter/fences and link targets. Inspected the resulting FUR diff and remaining allocator/reconfiguration terminology.
- Checked uv's primary documentation for project environment selection, no-sync/offline behavior and separate lock validation: [environment reference](https://docs.astral.sh/uv/reference/environment/), [locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/). Checked installed sandbox-exec usage for the macOS profile entrypoint. Platform confinement remains a required future executable proof, not a passed test in this documentation review.
- No implementation code, global permissions, tool ledgers, hook identities or unrelated story/context files were changed. Native submit owns the revision commit; final portable patch replay occurs before publication.
