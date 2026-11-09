---
schema: "aitm.review-response/v0"
level: "spr"
story: 2
role: "author"
round: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "73210b6da93942f06a0d6616cf5df02eaf64180c"
artifact_digest: "sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1"
patch: "patch-002.diff"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6-astra", "effort": "xhigh"}
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
started_at: "2026-11-09T05:29:25Z"
submitted_at: "2026-11-09T05:35:24Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R2-F001", "R2-F002", "R2-F003", "R2-F004"]
---

## Summary

Accepted all four round-two findings. They complete the shared-order and recovery semantics identified in round one without changing owner policy or granting a fresh implementation budget. The FUR now names durable facts that let a rebuild reproduce the decisions.

## Finding dispositions

- **R2-F001 — accepted.** Every authoritative managed start in a shared planning store, including a local test process, needs an admission verified in the shared CAS order. An offline clone cannot substitute its stale local state, and neither advisory mode nor later publication retroactively authorizes an unadmitted execution. Preparation remains pending without launching; already produced unadmitted output is diagnostic evidence only. In a genuinely local-only store, durable local intent/admission CAS supplies that order and publication is not applicable. Target-mutation wording now uses the same distinction. Acceptance includes a stop published by another clone while the would-be test executor is offline. The normal core-only walk observes an authorized merge in checked-out trunk; a separate fixture exercises an explicitly authorized core-run mutation of a non-checked-out local target without a remote.
- **R2-F002 — accepted.** Added typed reservation/resolution, review activation/invalidation, attempt reopening/clock change and managed execution facts to the compact event inventory. Every clock-mode boundary is recorded atomically with its causal operation in the owning event stream, including a reservation that never obtains a child and a retained verdict activated only later. Prior/new modes and generation/cause are validated; private runtime state cannot supply missing clock authority. Prepared/admitted/started/cancel-requested/finished/uncertain phases distinguish intent from execution. The admission's enclosing commit supplies its version; the event does not attempt to hash its own enclosing commit. Full-rebuild acceptance now exercises lost-acknowledgement reservation resolution without a child and delayed effective review activation.
- **R2-F003 — accepted.** Defined a typed evidence-only recovery for terminal unverified attempts with unchanged source. Reopen records its scope and retains prior closure/sign-off, time and allowance. A fresh bind --evidence generation for the same historical attempt permits managed verification and evidence/observation/sign-off while the old generation stays fenced. It grants no new implementation, expansion or target mutation authority. A missing real test can therefore run lawfully under current admission rules; eligible recovery engagement starts a new recorded segment without charging terminal waiting or resetting usage, and the later review activation is genuine. Lost derived proof with an already applicable pass preserves the stopped clock. Necessary code changes use explicit same-attempt rework and a normal implementation binding. A tripped, pivoted or scope-replaced attempt cannot use this path to evade replanning. The acceptance case requires an actual missing-test rerun, not just reconstruction of a receipt.
- **R2-F004 — accepted.** Forward repair now derives the maximal validated prefix of the exact quarantined history before the first disallowed commit. The receipt binds that prefix commit/tree, first violation, bad tip and deterministic restoration, rather than accepting the repair author's last cache entry. The P→V→B fixture requires preservation of valid unseen V and rejects restoring older P, even when that result is schema-valid and fast-forward. Fresh validation derives the same restoration from retained history and anchored legacy/repair rules. Invalid tail operations stay retained for explicit reconciliation; the repair does not automatically replay them, discard their evidence or bless a rewritten chain.

## Changes made

Updated the core event inventory, fold boundary contract, execution admission, evidence-only reopening and binding, forward repair, CLI inventory, local delivery walk and corresponding acceptance rows. Both optional suggestions are covered by the execution phase vocabulary and separate observed-merge/core-run delivery fixtures.

All ten round-one dispositions remain in author-response-1.md. This round makes the four remaining edge cases explicit; it does not reinterpret upstream additions as review findings or change the published SAR record.

## Declined changes and rationale

None. All four required findings are accepted, with no deferral or new owner decision. Existing expansion-completion interpretation, second-trip cap, review-depth/sequence policy choice and hosted audit mechanism remain open.

## Verification

- Checked the new admission clauses together: shared starts require published authority; local-only starts use local CAS; a prepared target intent alone grants no dispatch; no remote prerequisite leaks into the local-only mutation case.
- Walked durable reconstruction of reservation pause/resolution without a child and delayed review activation. Each boundary has a typed causal event/clock fact in the same transaction, rather than an inferred private timestamp.
- Walked Done/unverified → evidence reopen → new evidence-only binding → actual managed rerun → effective review → new sign-off. Old closure/generation and cumulative time/allowance survive; superseded/tripped attempts cannot regain execution through this route.
- Walked repair from P with unseen valid V and invalid B in one fetch; only V supplies the restored payload and a fresh validator can reproduce that choice.
- Checked FUR relative links, whitespace, response metadata, complete round-two finding coverage and unchanged native-attempt file digests before the author commit. No implementation tests apply; these scenarios are design-level reasoning and specified future acceptance tests.
- This temporary commit contains only the revised FUR and manual SPR response pair. Context files, published SAR, blocked native attempt and trunk remain untouched. Full-file round 3 is required; no XPR starts.
