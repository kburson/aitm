# #158 JIT · Same-repository atomic merge qualification

This JIT replaces the disposable-repository execution procedure in the
historical 2026-11-10 JIT for this trial. It implements the published
merge-only qualification plan at `51e3c6ae68c1863ec98a8df12d588ac291cb2cb9`,
SHA-256 `530abc24af6ff7ede14c0200416260ba3bd60c5333b1d720a5427fb297614cf1`.
The parent design at that revision has SHA-256
`08568f6bedf3bcb582737691558701fe618dcdfbd5a628e106008dccf5027a50`.
The earlier exact-base and writer trial stays in the evidence set.

The owner authorized this trial on temporary AITM refs. Retain the
four-hour cap and the two-hour decision point. The author and trial
custodian are the invoking Codex coordinator. Use a separate reviewer
for JIT and measurement review. #158 has no open predecessor. Preserve
its Planning record and #159's existing blockers #157 and #158.

## Literal fixture and authority

Pin repository `kburson/aitm`, ID `1450406435`, GraphQL node
`R_kgDOVnNyIw`. Use only these four literal branch refs for this run:

- `refs/heads/codex/158-atomic-b0f8ac7-target`
- `refs/heads/codex/158-atomic-b0f8ac7-head`
- `refs/heads/codex/158-atomic-b0f8ac7-flag`
- `refs/heads/codex/158-atomic-b0f8ac7-objects`

Read back their absence and exact repository identity before writing.
Anchor synthetic Git objects to trunk `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`.
Read current production trunk and planning protection definitions and
effective rules before fixture setup, with any fixture rule active,
and after teardown. Capture repository settings relevant to PR
behavior. The only possible protection write is a temporary ruleset
whose sole included ref is the literal fixture target. Use one active
`pull_request` rule with zero required approvals and no bypass actor.
Copy its rule parameters from the recorded trunk PR rule. Read back
its identity, active status, exact include, empty excludes and bypass
list, and confirm the rule is effective on the fixture target.
Keep the prior repository settings, real CI controls and both
production branches outside the trial write set.

The existing CLI account is `kburson`, the sole collaborator found
on readback. An independent write-capable principal and dedicated
service identity are not supplied by this trial authorization. Use
the current identity for the primitive and PR-only gate experiments.
Record exclusive writers, independent review and trusted check
publisher enforcement as unqualified unless the trial actually has
the required independent actors. Do not install or grant a new actor.

## Bounded fixture procedure

Before fixture writes, inventory active Actions, repository webhooks
and applicable automation for the exact fixture events and refs.
Record current workflow bytes and event filters, and whether any
external automation can act on the fixture. Hold a write if a possible
out-of-scope mutation cannot be excluded. Use synthetic immutable
commits and one auxiliary carrier ref for object availability.
The fixture tree contains only a marker and no workflow files. Any
fixture PR targets the literal fixture target and has no auto-merge,
agent attachment or queued merge. Read back any PR checks and
automated actions. Recheck the current tuple before each independent
operation and once for the common tuple of a competing pair. Use GitHub
GraphQL `updateRefs` with full ref names, expected old OIDs, and
`force: false` to compare and advance the target, PR head and shared
flag. For an admissible fixture merge commit verify ordered parents
and the exact tree. The head compare uses `H → H`; the two actual
updates move target and flag. Read back all three refs after every
response, including failures. Verify that any stale request would
otherwise be a valid fast-forward for both writes.

| Stage | Required measured result |
| --- | --- |
| Stale base | Candidate has ordered parents `B0,H0`, with the advanced target `B1` reachable through `H0`. With target at `B1`, submit expected `B0`. All requested entries are forward-valid against their actual refs. An attributable mismatch leaves head, flag and advanced target intact. |
| Stale head | Keep the head at `H0` and submit expected `H1` in an `H1 → H1` entry, with `H1` a published object descended from `H0`. All actual-to-requested OID transitions are forward-valid. Then advance the head to `H1` and use the identical target, head and flag inputs for the exact positive control. Attribute refusal to the head predicate only with a meaningful comparison and terminal readback. |
| Exact positive | With all predicates current, target and flag advance together and head stays fixed. Read back the landed parents and tree. |
| Hold wins | Advance the flag first. A request carrying the prior flag must leave the target unchanged. Pin a proposed flag successor descended from the actual held flag, so the negative would otherwise be fast-forward. |
| Merge wins and competing dispatch | Demonstrate a merge before the hold, a forward-valid stale-hold refusal, and a subsequent hold on the new flag. Then send one competing pair from the recorded common `(B,H,F)`, with separate request identifiers and intended flag OIDs. Hold-wins is terminal merge refusal and `(B,H,Fheld)`. Merge-wins is terminal hold refusal and `(M,H,Fmerged)`. Two refusals and unchanged state are inconclusive. Mixed state fails. Resolve both before a follow-up hold, other mutations or teardown. Client dispatch and response order establish no provider checkpoint. |
| PR-only boundary | If the primitive passes, verify the exact active rule and a ready, mergeable fixture PR with repository, number, head/base refs and OIDs. Recheck the exact candidate parents/tree and flag under the rule before submitting. Attribute denial to the PR rule using the provider reason or rule suite. A generic denial is inconclusive. If allowed, retain transaction and PR readbacks. PR state alone cannot prove authorization at mutation. |

The production contract additionally requires sole-writer enforcement
with a different write-capable principal, exact PR association even
for identical Git objects, independent checks and review, exact repair
and release, and target refresh after release. If a required earlier
boundary fails, preserve the counterexample and record dependent
cases as unrun. Synthetic state and one-person evidence cannot
satisfy those gates.

## Ambiguity, cleanup and publication

No automatic retries. For a timeout, missing readback or ambiguous
write, stop further mutations and teardown until the coordinator has
terminal provider evidence. Unchanged refs alone do not prove the
request is dead. Missing terminal evidence or an unexplained state
retains the fixture and names the coordinator as custodian. Preserve
provider request IDs and rule evidence where available. Once all
requests are resolved, close the owned fixture PR if open, remove the
exact owned fixture ruleset and delete only the named fixture refs.
Read back teardown and compare production protection snapshots.

Keep the prior trials and retain the reviewed JIT, request and response
receipts, ordered Git objects and refs, fixture rules and cleanup
evidence on `planning`. Report positive capability or a bounded
refusal. Advance #159 only under a separate authorized pickup after
both #157 and a positive reviewed #158 receipt. This run keeps it
blocked.
