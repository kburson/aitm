# #158 Atomic ref transaction trial

**Disposition** The existing AITM repository supported the bounded
atomic ref controls and a PR-rule fixture update. Full merge fence
qualification remains open. Keep #158 in Planning and #159 blocked.
[Reviewed JIT](2026-11-11-158-merge-only-jit.md) ·
[Measured receipt](../attachments/2026-11-11-158-atomic-ref-trial.json).

On three temporary refs, a current expected base, head and flag allowed
one update to advance the target and flag together. The corresponding
stale base, stale head and stale flag requests left every ref intact.
The stale-head request was otherwise forward-valid and succeeded after
only the actual head was advanced to its expected value. GitHub's error
responses contained request IDs and a generic execution error. The
controlled OIDs and readbacks distinguish the observed behavior. The
provider did not identify the failing predicate in those responses.
[GitHub atomic ref update contract](https://docs.github.com/en/graphql/reference/git#updaterefs).

The ordered cases captured both a merge followed by hold and a hold
that left a stale ordinary update unapplied. In the competing pair,
the hold response succeeded, the ordinary response reported an error,
and the target and head stayed at their pre-dispatch OIDs while the
flag advanced to the held OID. This is one measured final state.
Client dispatch and response timing did not expose GitHub's final
update-check interval.

The temporary target ruleset `27046475` had an effective
`pull_request` rule, zero required approvals and no bypass actor.
[Fixture PR #243](https://github.com/kburson/aitm/pull/243) was ready and
mergeable. The atomic update returned success with request ID
`C844:230F38:120135B:38B942D:6AF49907`. Rule suite `5050237373` recorded
a pass, and target and flag advanced together. The landed commit
`595fab23785db4c7e063fb452a2727f943362a2d` has the measured ordered
parents and tree `e53d00bc7507e47add7be1fda0ee1aed694bd1e6`. The immediate
PR readback was open. A later readback attributed its merge to the same
commit. The transaction and rule suite do not identify which PR
authorized mutation. GitHub can mark a PR merged after an indirect
update, so the later state alone does not prove that binding.
[GitHub indirect merges](https://docs.github.com/en/pull-requests/reference/pull-request-merges#indirect-merges).

Only the existing user was available for hosted writes. Exact
association with a nominated PR among identical Git objects, separate
writer, reviewer and check-publisher enforcement, repair and release,
and refreshed post-release CI remain unqualified or unrun. The fixture
had zero Actions runs, checks, reviews and comments in terminal
readback. No agent or auto-merge was attached to the fixture PR.

**Preflight deviation.** The run continued after the Claude
installation detail timed out. Active Actions filters and repository
webhooks were checked. Current external-app event scope remained
unverified at dispatch, so the run fell short of the reviewed JIT
preflight. The terminal observations record what happened in this
fixture. They do not establish that an external app could never have
acted. Keep the measurements as bounded evidence.

The four temporary refs and exact fixture ruleset were removed after
terminal readback. The production rules and repository settings
matched before, with the fixture rule active, immediately before the
protected candidate, and after cleanup. #159 still has its two open
predecessors #157 and #158. Earlier trials remain in the planning
record.
