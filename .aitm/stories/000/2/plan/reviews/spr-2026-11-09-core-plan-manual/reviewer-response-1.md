---
schema: "aitm.review-response/v0"
level: "spr"
story: 2
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "058e48141cc3c11bf4423f71c92619d8f64d7929"
artifact_digest: "sha256:54577b157af8c35296ceeb85d19b7d75af5a684bba79c45daeef493977b234e2"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1bf26-a955-77e0-bf3e-1a549309bfaa"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T07:12:24.461Z"
submitted_at: "2026-11-09T07:15:18.164Z"
start_basis: "recorded"
finding_ids: [R1-F001, R1-F002, R1-F003, R1-F004, R1-F005, R1-F006]
answered_finding_ids: []
---

## Summary

**Revisions requested.** I read all 1,132 lines of the current plan and checked it against the accepted core design, parent architecture and master plan, owner decision record, original Refine record, planning layout and interim review strategy. I also checked the preceding SAR findings and final disposition. The table and leaf sections agree on 62 leaves and 194.5 agent-hours, the maximum leaf estimate is four hours, and the table is topological under its declared prerequisites. The original 180 h Refine estimate is retained.

Codex worker metadata and the current turn record identify this separate session and gpt-6.1-sol/high. This is declared-manual SPR. The timestamps bound the recorded turn.

## Findings

### R1-F001 — High — Connect normal lifecycle commands to authored sync and late review activation

C17 owns explicit sync (plan lines 459–471). C31 orders the trip check before authored sync (lines 711–723), but C28's transition proof and the composition map still omit the call that performs the separately recorded authored sync on a normal state change, reports its result, and pins a new snapshot for the transition. C38 exposes `reconcile_review`, while the mapped `evidence reconcile` command belongs to C42 and specifies reconstruction and rerun requirements only (lines 119–123, 781–793, 837–849). C50 can exercise activation and rebuild through the helper without demonstrating how an early retained pass becomes effective through the installed CLI. The design requires both normal authored sync and explicit evidence reconciliation of still-applicable review at the genuine later activation (design lines 324–326, 362–364 and 449–463).

Name the production owner and route for normal authored sync followed by a newly pinned transition, and connect `evidence reconcile` or another named supported CLI action to C38 late activation. Prove installed `promote` handles an eligible authored change as a separate saved operation and bases its decision on the resulting state, including retained conflict when the import cannot safely complete. Prove a single early review submission stays ineffective through entry to Review, then activates through the named command with the genuine later clock stop and no duplicate verdict. Preserve pre-sync trip precedence and recovery capabilities.

### R1-F002 — High — Give repair validation and managed target mutation explicit gate integration

C06 wires the gate into GitBackend, whose transaction writes planning. C10 introduces a repair helper and planning adapter with no validator integration path, even though normal validation rejects the invalid ancestor from which repair must extend (plan lines 305–317 and 403–415). C41 writes a different target ref and tests an already checked-out target, but it neither names use of the C06 gate around target CAS nor tests detected interference across that CAS (lines 823–835). These are special ref writers with different safety needs. The accepted design explicitly makes fresh validation understand an exact verified repair and applies the common ref/worktree gate and interference detection to managed delivery (design lines 162–174 and 455–459).

Give C10 ownership of the production verifier update or an earlier named validation seam. Drive a repair through the CLI and verify the repaired history through the normal validator in a fresh clone, rejecting a forged or non-maximal restoration. Give C41 an explicit common-gate path for the exact target, with pre/post worktree checks and retained/fenced handling of detected out-of-band checkout interference. Extend the existing real Git fixtures to cover those boundaries.

### R1-F003 — High — Finish extension composition at the installed package entry point

C13 declares registry and provider helpers and unit tests. C11 declares an init provider step, but C13 does not supply the production connection from the committed enabled-extension snapshot to mounted CLI commands and init contributions. The composition map and C49/C50 proofs cover selected guards/actions and disabled ownership, but leave the accepted entry-point discovery, CLI mounting and enabled provider-init path unowned (plan lines 60–62, 93–95, 347–359, 417–443 and 1087). A registry built by test code could pass while an installed provider's command or init step is inaccessible. M1 owns the generic plugin contract for these contributions, including committed enablement and the host-neutral init path (design lines 137–147, 547–574 and goals 24–31).

Identify the leaf that discovers installed `aitm.extensions` entry points, composes the pinned enabled registry into command and init dispatch, and names the shared call-site paths and prerequisites. Exercise a disposable installed fixture extension through the ordinary CLI and init under committed enabled and disabled policy. Use the real registry to prove ordering, enablement and typed routing without requiring a hosted endpoint. Keep provider-specific init operations in their later extension scope.

### R1-F004 — High — Bind final expansion changes to the selected child in both issuance paths

The plan resolves local graduation authority and gives C30 its prerequisite. It still passes a concrete `RelatedWriteSet(read_set, writes, events)` into `graduate_local` before the allocator chooses or changes the candidate. Re-evaluating the existing set on a losing-number race can validate the origin without changing the child ID already embedded in an event or block. In the external path, `finalize_external_identity(reservation, expected_draft)` does not carry the related origin writes at all (plan lines 283–285, 515–541 and 697–709). The accepted atomic finalization and reallocation rules require the final block and facts to name the actual winning child and keep origin/finalization coupled (design lines 499 and 535–545).

Specify where candidate-dependent origin writes are built from the exact child identity selected for each attempted transaction, including the rebuild after number loss. Name the external finalizer seam that carries the still-current origin reservation and its related facts into that same finalization transaction once external identity is known. In C30, prove the resulting origin block, expansion events and reciprocal child facts name the actual winning ID after reallocation and after external lost-response finalization, with no unblocked interval, duplicate finalization or attachment to a fenced origin.

### R1-F005 — Medium — Encode the shared-file serialization that the backlog promises

The plan states that shared composition edits serialize by listed prerequisites and describes explicit serial owners (lines 90–95 and 1064–1070). The actual dependency closure allows C08 and C14 to edit `services.py` independently. It also allows C31 and C43 to change both `services.py` and `store/sync.py` independently, and C45 and C61 to change `cli/bind.py` independently. Table order can provide a deterministic lane, but calling it a fallback while the leaf ledger records the incomplete graph leaves that lane optional. The parent requires independent leaves to have disjoint paths or an integration order (master plan line 55).

Encode the missing serial edges or a mandatory deterministic per-file integration lane that the leaf ledger carries alongside functional dependencies. Cover the touched-file overlaps above and other overlaps found by comparing prerequisite closure with the file allowlist. Preserve useful parallelism for disjoint owners.

### R1-F006 — Medium — Run the required C5 cases against the exact released wheel

C60's post-publication test installs the immutable artifact and reruns lifecycle/migration smoke. The full matrix can be attached from C49–C59 candidate/source jobs under the current wording (plan lines 1047–1062, 1091–1093 and 1130–1132). The parent C5 checkpoint explicitly includes local-only and two-clone cases, migration/review import, repair and performance budgets on the released core (master plan line 70). A wheel can install and pass smoke while the tested checkout has code or package data absent from the wheel.

List the collected C5 suites to run in the clean consumer pinned to the released hash/version. Include the required two-clone, repair and performance evidence alongside lifecycle and migration/review import, with the documented hardware/capability lanes and a check that imports and the CLI resolve to the installed artifact. Reuse the existing fixture scenarios and keep live publication separate and once-per-release. C5 remains pending until this evidence is retained.

## Required changes

Address R1-F001 through R1-F006 and reconcile the leaf details, dependency/serialization rules, CLI proof and qualification map. Keep the original Refine estimate, owner-open choices and separate C5 release/C6 adoption boundaries. If the corrected obligations exceed a leaf's estimate, assign the work to a separately bounded deliverable or show how the delivered contracts and fixtures keep it within four hours.

## Optional suggestions

Carry the preceding SAR reminder about C25 forward. C25 can test the same normalized fact with its own live and completion interfaces. C51 supplies the installed final-import composition after C26.

## Decision

**revisions-requested**

The next round reviews the full revised candidate and its author dispositions.
