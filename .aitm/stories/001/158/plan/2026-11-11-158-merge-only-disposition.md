# #158 merge-only Stop the Line trial disposition

**The trial is complete with a bounded refusal.** GitHub's atomic ref update is a usable compare-and-update primitive in the measured AITM fixture. The trial supplies no qualified production merge route. Keep #158 open as the unresolved qualification and preserve both of #159's dependency links. The Rank 30 stories have independent predecessor sets.

## Measured on temporary AITM refs

- A request with current target, head and flag expectations advanced target and flag together. Forward-valid requests with a stale target, head or flag left the refs intact. The old head expectation was checked using a no-op ref entry, with a positive control after the actual head changed.
- Ordered cases covered merge before hold and hold before merge. In one competing pair the hold advanced the flag and the stale ordinary request left the target fixed. No concurrent merge winner or full protected-gate route matrix was measured. The provider responses gave no visibility into GitHub's internal final-check timing or behavior after a lost response.
- A ref transaction landed the exact ordered parents and tree under the fixture's PR-only rule. The rule suite recorded a pass for the exact ref update. PR #243 later appeared merged into that commit. Neither provider record identifies the PR that authorized the mutation. [Reviewed measurement](2026-11-11-158-atomic-ref-trial.md) · [Independent evidence review](reviews/2026-11-11-158-atomic-ref-trial-review.md) · [Fixture PR](https://github.com/kburson/aitm/pull/243)

## Qualification decision

Authenticated GraphQL introspection confirms that `updateRefs` accepts a repository and ref updates with before and after OIDs. The input carries no PR identifier, review or check predicate. Native `mergePullRequest` accepts a PR ID and expected head. It exposes no expected base or shared flag predicate. The earlier temporary-ref test also observed the head-conditioned native route landing on a moved base. The measured ref transaction and the native merge route each lack a required part of the accepted admission boundary. [GitHub atomic ref update contract](https://docs.github.com/en/graphql/reference/git#updaterefs) · [Earlier exact-base trial](2026-11-11-158-merge-boundary-trial.md)

The live collaborator list has one write-capable principal, the same account used for the trial. Independent merge-writer, reviewer and trusted check-publisher enforcement is unqualified. The prior run proceeded after the Claude App installation read timed out, which fell short of the reviewed JIT's pre-write gate. The CLI still cannot enumerate App installation scope with its current user token. No additional hosted mutation was dispatched during this disposition. Repeating the one-principal transaction would leave those gates unresolved.

Exact nominated repair, full recovery release, and per-PR validation after release depend on the missing admission boundary. Those cases remain unrun. The same applies to scope isolation through a real protected gate, lost-response ordering and enforcement after GitHub's final update check. A positive qualification requires a reviewed mutation route that binds the reserved PR and the live target, head and flag while retaining the independent gate controls.

## Live teardown and protection readback

The four named fixture refs and ruleset `27046475` are absent. PR #243 remains terminal. Rule suite `5050237373` still records the exact fixture update. The comparable production ruleset fields and effective rules for `trunk` and `planning` match the reviewed teardown snapshot. #157 and #158 remain open blockers of #159. [Authenticated readback](../attachments/2026-11-11-158-merge-only-disposition.json)
