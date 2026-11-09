---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "981b8d77e2e988e9ec3f79768c7c9728cb66c11a"
artifact_digest: "sha256:195fff0b8903bf1a94d5ae3337d368ba0a7bfeb7110d7dd5276f0f6900d9f4f3"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1be88-ab35-75f0-aa41-1f21e6062d95"
started_at: "2026-11-09T04:43:57Z"
submitted_at: "2026-11-09T04:45:59Z"
start_basis: "recorded"
finding_ids:
  - R2-F001
  - R2-F002
  - R2-F003
  - R2-F004
  - R2-F005
  - R2-F006
  - R2-F007
answered_finding_ids: []
---

## Summary

**Revisions requested.** I read the full current FUR, author-response-1, the latest master decision record including the Review timing section, the accepted architecture, the actual story #1 backfill and its XPR manifest. This round covers the upstream `7e829d5` additions as integrated in the current digest, including the event envelope, document-review turn and completion records, timing, CLI, migration and the review-timing acceptance case. The original review base remains `981b8d7`.

The revised design resolves the fundamental event-ordering problem and separates local recording, publication and projection. It also fixes the open-policy treatment and introduces content-bound acceptance, actual evidence capture and bounded forward repair. Several remaining seams can still produce duplicate issuance, a false delivery result, or evidence the normal entry points cannot faithfully reconstruct.

### Round-one dispositions

| Finding | Round-two result |
| --- | --- |
| R1-F001 | Resolved. CAS operations preserve causal append order, re-evaluate consulted state and retain conflicting local outcomes. |
| R1-F002 | Resolved. Assigned routes, binding generations and one pinned cache/store snapshot prevent the cited overwrites and redirection. |
| R1-F003 | Resolved. Trusted default-ref routing, committed policy and freshness are separated from story files. |
| R1-F004 | Canonical digest, stale-base import and JIT invalidation resolved. R2-F002 and R2-F003 cover remaining review-record lifecycle and assurance. |
| R1-F005 | Deterministic fact mapping, provenance and cutover atomicity resolved. R2-F002 and R2-F005 cover a real legacy timing-source and bootstrap gap. |
| R1-F006 | Intent and finalization added. R2-F001 addresses concurrent dispatch of the same issued intent and authority handoff. |
| R1-F007 | Resolved. Pending actions, published-only projection and serialized/monotonic provider effects cover the reported crash and ordering cases. |
| R1-F008 | Exact test/review inputs, evidence recovery and delivery-before-sign-off added. R2-F004 covers false-positive local delivery and crash after target mutation. |
| R1-F009 | Open policy correctly retained and origin/child stop is atomic. R2-F006 covers command ordering at a detected trip. |
| R1-F010 | Observed/estimated/Unknown and learning measures distinguished. R2-F002 covers the integrated review-time facts and attribution contract. |
| R1-F011 | Resolved. Kind-specific progression, reviewed spike deliverables and dependency dispositions address the reported lifecycle conflicts. |
| R1-F012 | Data-only policy, quarantine and forward repair addressed. R2-F005 covers independent anchor and migration receipt verification. |
| R1-F013 | Resolved. Ownership at the write boundary, version/order and unknown-owner behavior are explicit. |
| R1-F014 | Nominal core-only walk, recovery commands and failure cases added. R2-F007 covers the legal advisory state when evidence or setup is missing. |

## Findings

### R2-F001 — High — Fence identity creation after a reservation becomes visible

**Evidence.** FUR lines 398, 415–416 and 434–438 publish a stable intent, then rely on `create_or_reconcile`. That prevents competing *reservations*, but two clones can still resume the same published intent, both observe no remote match and both create an issue. A correlation marker can find a completed create after a lost response. Its absence at one observation does not prove another sender cannot still create. Likewise, a former shared local allocation authority can expose an ID from a disconnected clone before it learns it has been replaced.

**Required change.** Separate reservation from exclusive dispatch. For providers with no proven idempotent create, require a shared, durably acquired dispatch claim before sending, and observation-only recovery while the previous dispatch is uncertain or can still run. Require any retry/takeover to establish safe absence and fence the old sender. Define the shared local allocation publication/fencing point before a permanent ID is exposed. Preserve local-only allocation behavior. Add acceptance for two clones resuming the *same* intent and a stale allocator after authority handoff. The provider may choose its fencing or idempotency mechanism.

### R2-F002 — High — Define how turn facts are recorded as work lands and replayed without duplicates

**Evidence.** FUR lines 185–186, 236–237, 358–360, 392–396, 487, 506 and 524 retain the upstream event and command surface. They give final import ownership of immutable collateral while `review turn` is supposed to append as each response lands. A turn on an M1–M4 review branch has no final manifest and its source does not yet exist on planning. The event table also lacks the level-record ID that line 396 needs, and a live fact and backfill of identical response bytes have different recording envelopes. The real XPR round-two backfill's timing uses the preceding submission, while its `backfill.source` points to a response whose raw start is a registration time. Hashing that response alone cannot reproduce the selected start. The upstream owner-agreed boundary excludes setup, pre-claim reading and publication. A prior-submit proxy or final author acknowledgement can span some of those activities.

**Required change.** Give a level its stable identity before the first turn. Describe which immutable bytes and predecessor/basis evidence `review turn` persists or references, and which validations require completion or a final import. A provisional turn must be useful for timing and unable to accept the FUR. Define idempotency on the normalized review fact and immutable source identity, separate from recording actor/time and derivation provenance. Preserve the exact timing anchor for `recorded`, `claim` and `prior-submit`, including an independently readable predecessor or native claim reference, and handle a later qualified correction without overwriting the original. Keep proxy coverage and unknown/excluded work separate when reporting state, review level, role and model. Clarify how a span crossing a state boundary is attributed without double counting. Update the real-record migration and timing acceptance to compare live-plus-import and backfill of the same level, including native registration reuse and an interrupted turn or unobserved start.

**Basis.** Story #1 draft lines 174–191, actual story #1 events lines 13–17 and portable XPR manifest lines 40–42 and 64–70. The FUR's causal append order and no planning-time trip remain correct.

### R2-F003 — High — Validate review level and assurance before treating a record as accepted

**Evidence.** FUR lines 236–237 and 354–360 check response digests, finding coverage, terminal decision and the configured level list. Those checks can all pass for a record labeled SPR whose author and reviewer have the same session, or a record labeled XPR with identical providers. The accepted architecture defines these levels by their participant relationships. The actual v0 XPR manifest distinguishes retained native fingerprints and ordinary tool-recorded consensus from unavailable independent authority assurance. A byte-consistent record can remain useful without proving all of those claims.

**Required change.** Specify validation of each level's provider and session relationship, participant continuity within a level, and the evidence or assurance kind the applicable policy permits. Define the result for missing, contradictory or merely declared provenance, retaining useful timing/collateral even when it cannot satisfy a required level. Preserve the native v0 limitation during migration and the ability to use manual portable M1 records under a policy that explicitly allows their assurance. Add an otherwise well-formed wrong-provider or same-session record to acceptance. Leave the required-level matrix open.

**Basis.** Architecture lines 132–140 and the portable XPR manifest lines 34–42.

### R2-F004 — High — Prove reviewed content reached the local delivery target and retain proof across crashes

**Evidence.** FUR lines 370–374 and 485 describe ordinary merge/fast-forward as proving ancestry plus a target result. A merge using Git's `ours` strategy can name the reviewed source as a parent while leaving the target tree unchanged. Other merge resolutions can replace reviewed changes with unreviewed bytes. Core-run squash/rebase also has a gap if the target ref moves and the process dies before the planning evidence commit. A post-hoc check with no pinned intended result cannot reliably reconstruct that mapping. [Git merge strategies](https://git-scm.com/docs/merge-strategies)

**Required change.** Define the positive content check for ordinary merge as well as rewritten delivery, against the intended pre-target and exact reviewed source/delta. Retain the approved transformation or equivalent proof. Reject or leave pending ancestry-only, discarded changes and unverified conflict resolutions. For an authorized core-run mutation, durably record a stable operation and pinned inputs/expected result before target update, then verify and record the result. A retry after the target moved must reconcile rather than perform a second delivery. External deliveries with incomplete proof may remain pending. Test the ancestry-without-content case and a crash after target mutation.

**Basis.** Architecture lines 128–130. The chosen Git plumbing and merge strategy remain implementation choices.

### R2-F005 — High — Give initial validation and legacy migration a noncircular trust anchor

**Evidence.** FUR lines 113–115, 127–128, 145–149, 159, 438 and 498–508 require trusted anchors, warn against accepting a familiar trailer, and promise fresh-clone verification. Init's reuse check nevertheless points to the trailer and its only second-commit content is `.aitm/README.md`. The required `store.json` identity and allocation authority have no creation path. For legacy stores the cutover receipt is the only described evidence of the accepted legacy tip/tree. A fresh clone cannot trust an exception solely because the history making the exception declares it valid. If the in-tree receipt's “resulting valid tree” means the final tree object ID, it would also have to hash its own contents.

**Required change.** Specify the source and validation rules for the identity/root of a new store, how a fresh clone obtains that anchor, and where init creates or resumes the initial authority metadata. Pin the accepted legacy baseline independently of a candidate migration receipt, with a bounded policy for legacy paths and deterministic verification. Specify a non-self-referential result binding, for example a validated payload tree excluding the receipt or another comparable construction. Align the init reuse check, migration and fresh-clone tests. Retain the data-only rule and owner-only intervention for irreparable ancestry.

### R2-F006 — High — Detect and commit a trip before the command it is meant to refuse

**Evidence.** FUR lines 292, 324–326, 368 and 386–402 say touching commands check time, a passing review stops the clock and the detected trigger is refused in enforce mode. The transition algorithm has no placement for that check. A review-pass command arriving with enough observed activity to prove an overrun can first stop the clock and record success. A sync or test command may likewise touch a known-tripped attempt before the rules engine runs. Late telemetry is allowed and correctly does not retroactively move state, but that does not define how in-flight evidence is recorded or how a known overrun blocks the next normal action.

**Required change.** Put trip detection and its CAS recheck explicitly ahead of mutable implementation work or passing-review closure at the observed command boundary. Distinguish retaining already-produced observation/evidence and exporting work from authorizing another normal implementation action. Define which commands can still record analysis or recover evidence while fenced, and where a newly completed subprocess interval is evaluated. Exercise an observed overrun arriving with a pass/transition request and a CAS retry. Preserve the established advisory reporting behavior and the rule that unobserved work stays qualified.

### R2-F007 — Medium — Define the legal result of advisory advancement with missing prerequisites

**Evidence.** FUR lines 288, 325–341, 362, 372, 386 and 517 say advisory can advance with a failed `plan-accepted` or `implementation-bound` guard. An attempt can only start with an accepted plan generation and valid bound source, and later verification requires that attempt/binding. The result can therefore be a Develop record with no legal evidence-producing command. A similar ambiguity exists after `Done/unverified`: the design preserves that disposition but leaves any correction behind an unspecified reopening operation.

**Required change.** Name the minimum integrity data required to represent each transition safely and distinguish it from waivable workflow evidence. Define the resulting provisional attempt/binding state, or the specific integrity refusal and supported recovery when no consistent state exists. Show the normal advisory recovery from missing plan or binding and from `Done/unverified` once evidence becomes available. Keep the waived failure and original disposition in history and do not manufacture delivery or verification.

## Required changes

Address R2-F001 through R2-F007 in the FUR. The gaps are specific to dispatch ownership, turn-level provenance and assurance, local delivery proof, trust bootstrap, trip ordering and advisory recovery. Each can be resolved through a small contract and a matching acceptance scenario. The accepted architecture and master plan remain context.

## Optional suggestions

- Mark the event JSON example at lines 200–203 as abbreviated, or include its required sequence, operation and provenance fields. The prose already specifies those fields.

## Decision

**revisions-requested**

No new owner decision is needed. The expansion-completion boundary, second-trip cap, review-depth matrix and GitHub every-push audit mechanism remain open. Re-review the complete revised FUR and author dispositions at the next digest.
