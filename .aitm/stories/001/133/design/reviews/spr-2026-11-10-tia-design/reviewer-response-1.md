---
schema: "aitm.review-response/v0"
level: "spr"
story: 133
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/001/133/design/test-impact-analysis-design.md"
artifact_base_commit: "dafd48cb6faf58c7a99e35945adca15f084b6ae6"
artifact_digest: "sha256:1e4f53942fa8c15c08fa68983825ebba638f6e9009c2e27aaa0dd5533258fcd8"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6.1-sol", "effort": "high"}
role_session: "codex-collaboration:/root/tia_spr"
session_identity_kind: "distinct-collaboration-participant"
started_at: "2026-11-10T16:07:27Z"
submitted_at: "2026-11-10T16:09:39Z"
start_basis: "recorded UTC bound"
finding_ids: ["SPR-01", "SPR-02", "SPR-03", "SPR-04", "SPR-05"]
answered_finding_ids: []
---

## Summary

I independently read every numbered line of the candidate without truncation in ranges 1–50, 51–100, 101–150, 151–200, 201–250, 251–300, 301–350, 351–400, and 401–414. The SHA-256 matched the declared digest before and after retrieval. I also checked the graduated draft and the workflow, inventory, and coverage contract in the accepted #103 design. This is a design review in a distinct Codex collaboration session.

The design retains explainable dependency witnesses, full fallback for unresolved impact, independent shard reconciliation, the 3/6/10 minute budgets, isolated PR failure, and separate owner approval for any gate cutover. The remaining issues concern the proof needed to authorize an update or release a stop.

## Findings

1. **SPR-01 [P1] The final merge operation can consume stale authority.** Lines 321–329 and 339–357 require a recheck and one serialized actor, but the host mutation has no stated precondition that binds it to the head and base just checked or to the tested tree. A contributor can push H2 after the actor rechecks fully validated H1 and before a merge-by-PR-number request reaches GitHub. Serializing the actor's local requests does not serialize PR head updates at GitHub. A post-merge full run on the resulting SHA cannot undo the unauthorized repair merge. The same race can invalidate an ordinary merge. The acceptance rows at lines 400–401 cover stale evidence presented before admission, with no proof for movement between readback and mutation.

2. **SPR-02 [P1] A disconnected running workspace has no defined fail-closed pause.** Lines 362–379 cover notification, the next governed boundary, and a disconnected workspace holding restart. They do not state what an already running session must do at a governed boundary when it cannot obtain the shared decision. A clone can lose its connection after seeing Healthy, miss the stop notification, and continue ordinary local edits using that cached decision. The disconnected case at line 401 proves only the release barrier. It cannot establish the code pause required by lines 280–287.

3. **SPR-03 [P1] The restart receipt can establish upstream ancestry while the workspace still runs the defect.** Lines 372–389 bind the acknowledgment to workspace generation and the updated base. A workspace can integrate the repaired upstream, then resolve a conflict by retaining the old defective behavior in its effective branch or working tree. Its base still contains the repair and unrelated pickup validation can be fresh. Those facts alone can satisfy the stated receipt conditions. The enrollment snapshot is also described as a roster that can undergo verified changes, with no explicit rule preventing an enrollment withdrawal from dropping a disconnected workspace's outstanding obligation. Either case can make the release check pass without verified delivery to all workspaces enrolled at the stop.

4. **SPR-04 [P1] A second verified trunk defect has no transition while the first incident is active.** Lines 298–319 describe one incident and ordered, idempotent events. Lines 321–337 bind recovery to one defect and one repair candidate. A distinct scheduled failure can arrive while repair A is in flight or while workspaces are integrating A. The design gives no rule for incorporating failure B, invalidating an already-open workspace-update phase, or reconciling B before a release for A. Duplicate and out-of-order event handling at line 402 cannot establish what happens to two different authenticated failures.

5. **SPR-05 [P1] Trusted artifact custody does not establish trusted inventory or outcomes.** Lines 59–68 and 147–185 place the selector, collector, and authority outside the candidate and require artifact identity, digest, and exact accounting. They do not require the collector to establish which part of the record can be influenced by Python executing in a candidate job. A candidate module imported during collection or execution can alter in-process pytest behavior or write a report on a candidate-writable path, while all workflow, verifier, and policy blobs stay unchanged. A canonical job may then upload an artifact with the right run, assignment, and IDs. Comparing a digest and a list of IDs cannot distinguish reported passes from observed execution. This affects the full fallback as well as selected mode and can also hide trustworthy negative evidence from the health authority. Lines 396–397 test bad receipt shape, but a forged receipt can have the expected shape.

## Required changes

- **SPR-01** Require a host-enforced final update precondition or equivalent fenced path for the exact admitted base, head, and approved merge result. Specify what happens if the approved tree cannot be guaranteed for an enabled merge method. Exercise head and base movement between readback and mutation, and verify that an unexpected resulting tree holds recovery and cannot be recorded as the authorized repair.
- **SPR-02** Specify that an unavailable or expired shared decision cannot admit ordinary governed mutations or new operations. Define what bounds any already admitted operation and where it stops at the first safe point. Rehearse a live session that loses access before the stop is recorded, misses the notification, and attempts another ordinary action while disconnected.
- **SPR-03** Require evidence for the effective integrated workspace state under the incident's fix proof, including conflict resolution or local changes that can defeat the fix. Specify that an outstanding obligation in the stop roster cannot be satisfied by disconnect, relabeling, or enrollment withdrawal. Exercise a conflict that restores the bug despite repair ancestry and an attempted roster change while a disconnected receipt is outstanding.
- **SPR-04** Define how the authority retains distinct unresolved test-failure evidence while stopped, folds or queues new failures, and fences repair, recovery, and restart when the relevant incident state changes. Exercise a second verified failure during workspace updates and show that recovery for the first failure alone cannot reopen the line.
- **SPR-05** Define the provenance and observation boundary for collection, assignments, per-test results, and negative evidence. Specify how the trusted side establishes the portions used for gating and rejects candidate-controlled or unverifiable claims, including when full fallback cannot provide trustworthy evidence. Qualify the boundary with an otherwise well-formed receipt that attempts to hide a test or substitute a pass after candidate code runs.

## Optional suggestions

At cutover, define how changed-line coverage handles a zero executable-line denominator after deleting executable logic. Record the intended treatment so a reviewer can distinguish a genuinely inapplicable denominator from a fallback.

## Decision

Revisions requested.
