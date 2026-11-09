---
schema: aitm.review-response/v0
level: spr
story: 2
role: reviewer
round: 2
artifact_path: .aitm/stories/000/2/design/core-design.md
artifact_base_commit: 73210b6da93942f06a0d6616cf5df02eaf64180c
artifact_digest: sha256:865cdcef8edfaa472fe31ae05425f99e6af26e00f8e238b59d42e045149cf257
agent:
  host: codex
  provider: openai
  model_id: gpt-6.1-sol
  effort: high
reviewer_session: 01a1bebb-3dd5-7422-8d7e-58de85638746
started_at: "2026-11-09T05:27:44Z"
submitted_at: "2026-11-09T05:29:06Z"
start_basis: recorded
finding_ids: [R2-F001, R2-F002, R2-F003, R2-F004]
answered_finding_ids: []
---

## Summary

I verified the revised FUR and the author response for all ten round-one findings. R1-F002, F003, F006, F008, F009 and F010 are resolved. The shared-history checks, pending expansion condition, managed-start ordering and effective-review prerequisites address the original cases in R1-F001, F004, F005 and F007. The remaining findings specify how those contracts must behave when reconstructed from persisted facts, when shared publication is unavailable, or when the normal recovery command follows terminal closure.

## Findings

### R2-F001 — The authority for managed starts is ambiguous across clones and in local-only delivery

**Managed start and dispatch admission, lines 344–346, policy refresh, line 121, and local delivery, lines 406–408.** In a shared store, clone A can publish a stop while clone B is offline with an older validated snapshot. Clone B can read “for shared actions” as excluding its local `test`, admit a managed start on its local ref, and launch after the published stop already won. A later conflict protects the shared record but does not prevent the work from starting. Conversely, the delivery admission paragraph unconditionally requires verified publication of the intent, while the local-only walk and target mutation rules allow an authorized local mutation with publication not applicable.

Name the authoritative admission order for each class. Specify whether a managed test in a shared store must publish its admission for an authoritative start or can run under a separately labeled, non-authoritative local/diagnostic lane when the shared order is unavailable. Align the refusal and result applicability with that choice. For an eligible local-only mutation, the durable local intent and admission establish that order without requiring remote publication. Add a two-clone stale-stop case and exercise authorized core-run local delivery to an eligible un-checked-out target. The already-admitted cancellation boundary can remain as written.

### R2-F002 — The fold contract cannot recover the new clock boundaries from its named inputs

**Events and Folding, lines 224–258, effective pass, lines 398–402, and expansion reservation, line 446.** The event list has a review verdict at import and a child-bearing expansion event at finalization, while `events.fold(events)` owns effective review, attempts and qualified timing. A pass can be imported in Develop, retained in Review, and only become effective later after evidence reconciliation. The verdict and ordinary state transitions do not say when activation occurred. Likewise, an expansion can pause the clock before child creation and clear the pause after authoritative non-issuance, without ever producing a child-bearing event. A rebuild needs the original pause, resume and activation boundaries to reproduce the clock and whether it can trip.

Name the append-only typed facts for reservation/pause, resolution/resume, effective review activation and invalidation, or explicitly make equivalent versioned operation facts fold inputs. Tie the facts to their attempt and operation in the owning CAS. Update the event/operation inventory to agree with the model. Exercise a full rebuild with a lost-acknowledgement expansion that never produces a child and a retained review verdict that becomes effective only later. In both cases the reconstructed clock and applicability must match the live decision.

### R2-F003 — Evidence-only reopening can strand an unchanged attempt without a lawful verification start

**Binding and recovery, lines 296–302, attempt closure event, line 237, admission, line 344, evidence-only reopening, line 367, and sign-off/effective closure, lines 402–410.** Sign-off atomically ends the implementation sessions and closes the attempt even when advisory produces `done/unverified`. The specified reopen puts the same attempt back in Review, but a real missing test must run under a valid current implementation binding and a live, unfenced generation. Merely moving the state to Review neither restores that authority nor says how a new session may acquire it. For example, a clean unchanged source can have a failed or absent test at Done/unverified, and reconciliation cannot reconstruct a pass that never existed. A fresh attempt would reset the exact lineage the reopening promises to preserve.

Define the typed reopen/recovery binding path that permits a managed rerun on the same unchanged source and historical attempt after terminal session closure. Keep the old generation fenced, name the permitted new evidence-only authority, and retain clock/allowance, past sign-off and the genuine activation time if review later becomes effective. Distinguish this from reopening a tripped or scope-replaced attempt for fresh implementation. The acceptance walk should recover an absent authoritative test requiring an actual run, not just restore a lost derived receipt.

### R2-F004 — Forward repair needs one deterministic restore point within the quarantined chain

**Validation and baseline and Forward repair, lines 153–163.** The repair pins the “last validated tree.” That could be the last locally accepted tip rather than the latest valid prefix of the exact quarantined chain. A clone last saw P, another writer published valid V, then a bad commit B was appended. Restoring P as a child of B is a fast-forward and can yield a schema-valid tree, but it drops V's valid events, authored content or issued identity from the active store. A fresh validator must derive the same safe restoration even when it never observed P or V as separate fetch results.

Define the restoration base as the maximal validated prefix before the first disallowed commit in the quarantined chain, or an equally constrained rule that preserves all valid published prefix work and is reproducible without the repair author's cache. Preserve the invalid tail as evidence and keep the existing ancestry/continuity fencing. Add a fixture with valid unseen V followed by bad B in one fetch, and reject a repair that restores older P instead.

## Required changes

Resolve R2-F001 through R2-F004 and align the acceptance cases with the chosen durable semantics. The existing expansion-completion interpretation, second-trip cap, required review-depth matrix and hosted audit mechanism remain open.

## Optional suggestions

- Align the compact event inventory with the managed-start and delivery dispatch vocabulary so an implementation plan can distinguish pending intents, admitted starts, observed execution and terminal results.
- Show the normal core-only delivery observation path and the eligible core-run path as separate test cases. The normal checked-out trunk remains an observation path.

## Decision

revisions-requested
