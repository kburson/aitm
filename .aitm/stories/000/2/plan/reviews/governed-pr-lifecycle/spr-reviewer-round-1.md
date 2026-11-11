# #2 Governed PR and working branch lifecycle · independent manual SPR

**Verdict — Changes requested.** Six findings require disposition before this revision is ready for cross-provider review. This was an independent same-provider manual review of the specification and plan. It did not exercise provider writes or qualify a host route.

## Exact inputs and scope

I read the entire 96-line specification followed by the entire 266-line plan in contiguous ranges. I verified the raw SHA-256 digests from the physical review worktree `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk`. The worktree's branch pointer initially resolved to the assigned source commit `123e08304bdfe94ae4eac83f6b93a9a3e2822c79`. It later resolved to collateral-only checkout head `b351fc9e26aae8570f1e44d5d40bcfe5426fbaa6`; the reviewed source bytes remained unchanged. I consulted the accepted Core contracts for identity, binding, dispatch, delivery and aggregation, and the published #133 and #158 amendments and relevant retained trial evidence.

| Artifact under `.aitm/stories/000/2/` | Raw SHA-256 |
| --- | --- |
| `design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` | `2829a591189907906757716138d9dfa9806a552c1194e422823fa507e1cd5db4` |
| `plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` | `7596974f583018af5de1e7a50f208bc360ad1d3c9de4d8ecd4a6335ce2dca258` |

## SPR-PR-01 · P1 · Give ready promotion a viable qualification and recovery handoff

**Locations** Design lines 68–84. Plan lines 26, 160–171, 228–238 and 262–265. #133 amended design lines 52–66 and 74–78. #158 qualification lines 31–54 and 72–74.

The Core draft requires the exact flag/head/target to remain valid through the provider status transition. The proposed #158 transaction compares Git refs for a target update. Its receipt does not, by itself, order a provider PR-status transition. The published #133 design treats draft status as a workflow convention, and #158's repair trace needs a nominated PR to leave draft. If the Core ready capability returns unsupported after #158 qualifies its target mutation, the plan provides no path to exercise the managed repair and recovery it promises. The proof matrix has a race test, but the delivery steps do not assign this separately stronger host capability or name the dependency it blocks.

Make the policy boundary and owner explicit. If the provider-atomic ready transition is required, assign an independently reviewable qualification with its own prerequisite, ordered operations and stop disposition. Gate the integrated repair path and production activation on that positive receipt. If a serialized trusted-service ready admission is sufficient as a workflow convention, reconcile that choice with #133/#158 and specify what happens to an already-dispatched or ambiguous readiness request across a hold or retarget. In either case, preserve #158's hard host merge enforcement, the exact nominated-repair binding, and the prohibition on treating unavailable as positive evidence. Include a trace where merge qualification passes and ready qualification fails, with a specific decision about which flows are held.

## SPR-PR-02 · P1 · Reserve the lifecycle slot and fence old effects before resource reuse

**Locations** Design lines 20–27 and 45–61. Plan lines 82–121, 195–216 and 258–259. Accepted Core design lines 590–596 and Core plan C20.

A dispatch claim is scoped to an already allocated incarnation. The draft does not explicitly make allocation a compare-and-set on the permanent story's single active/pending lifecycle slot. Two callers could propose different incarnation IDs for the same graduated issue, each acquire its own effect claims, and create two branch/PR pairs without violating one dispatcher per claim. Also, the scrap rule gates replacement pickup on old retirement, while early provisioning itself writes the ref. If a literal ref is reused and a previous delete or push can still finish against the same expected OID, a newly created ref can be affected before pickup. A generation ID present only in Core is invisible to the provider ref predicate.

Publish a semantic reservation before any per-effect claim, enforcing at most one active or unresolved provisioning incarnation per permanent story, repository and managed role. Make literal host ref/PR resource ownership exclusive across old and new incarnations. Distinguish a fenced but unsent effect from an already-sent effect that can still land. Block reuse until terminal effect reconciliation, or prove a distinct never-reused host identity or a host fence that prevents the old request affecting the new resource. Add races with two distinct operation IDs and incarnation proposals for one graduated issue, and with an ambiguous old request and same literal ref/OID replacement. Verify a different caller cannot get another eligible claim simply by proposing a new incarnation.

## SPR-PR-03 · P1 · Resolve authority when a working ref is also a governed merge target

**Locations** Design lines 28–35 and 73–79. Plan lines 25, 38–48, 138–152, 173–181 and 261–265. #133 amended design lines 12–18 and accepted Core design lines 508–512.

The integration delivery story owns a working ref that is also the protected-by-policy target of child PRs. The plan authorizes story owners to push their bound working ref and separately requires the parent policy and exact C41 admission for managed child merges. If that working-ref push can write arbitrary fast-forwards to a ref that policy reserves for reviewed child delivery, the integration owner can locally integrate a child and send that result through push. The same repository/ref then has two mutation paths with different checks. Checking unauthorized repository or ref cannot catch the overlap. The concern is limited to parent policy that reserves writes or requires provenance; a policy that explicitly permits direct owner changes needs a clear rule for those changes.

Declare ref roles and operation-level precedence where they overlap. Define whether a governed integration target accepts direct pushes, and under what separately authorized write intent, expected-old-head and provenance requirements a parent owner may refresh or add its own changes. When the parent policy requires exclusive reviewed delivery, constrain the host/broker routes accordingly. Specify effects on child and integration evidence and on concurrent exact delivery. Add a real managed-command negative test attempting to smuggle child integration through an authorized push to the parent's own working ref, plus positive cases for permitted direct work and approved refresh where applicable.

## SPR-PR-04 · P1 · Separate the epic's Backlog relation, integration target and completion condition

**Locations** Design lines 28–35. Plan lines 31–48, 50–70 and 263–265. Accepted Core design lines 450–455 and Core plan C62.

The integration owner is an ordinary “explicitly related” story, but the relation is not specified. If it is a required child of the epic, the preceding child rule would normally select that epic's own integration ref as its delivery target, potentially selecting its own source. If it is a sibling or merely related, C62 can close the epic once its required children land on the integration branch, before its promised default-target delivery. The same ambiguity appears when an integration owner is abandoned or replaced after children have been delivered. The typed composed-source proof solves source eligibility but does not determine which graph and terminal disposition is valid.

Specify separate semantic fields for Backlog parent/required scope, resolved resource owner, and literal delivery target. Pin the integration delivery's upstream target independently of the child-to-integration target. Define whether epic completion requires that designated delivery and make the applicable C62 dependency/scope behavior explicit. Show a top-level graph from provisioning through child delivery, integration review and trunk merge, with no self-target or provisioning dependency cycle. Verify premature epic closure and source/target aliasing refuse, and verify how replacement or abandonment preserves obligations. Preserve pure aggregate behavior.

## SPR-PR-05 · P2 · Separate #158 synthetic qualification from integrated #133 CI proof

**Locations** Plan lines 234–243, 248–254 and 265. #133 plan steps 2–5, especially lines 28–38, 52–73. #158 qualification lines 58–64 and 76–83.

The final hosted proof row requires an accepted #158 capability and an independently reviewed fixture, then asks for held recovery, reopen and first refreshed delivery. #158 qualifies the host mutation with synthetic CI/incident evidence. #133 T34 and T36–T40 own trusted release admission, actual full recovery and actual refreshed CI. The row allows a synthetic #158 trace to appear sufficient for the integrated behavior, or leaves implementers guessing which later producers are necessary.

Give the synthetic host fixture and end-to-end CI fixture separate prerequisites, owners and retained receipts. Require the applicable accepted #133 producer and actual run evidence for the integrated test, including the same-tuple result admitted before release that finishes afterward. The #158 test remains independent from later recovery implementation. Preserve #157/#158 and pickup requirements for #159, and distinguish a proved host mechanism from permission to change the existing #103 gate or production protections.

## SPR-PR-06 · P2 · Preserve the draft convention when retargeting an already-ready PR

**Locations** Design lines 68–79. Plan lines 26, 160–171 and 262. #133 amended design lines 52–66 and #158 qualification lines 72–74.

The plan invalidates previous promotion and merge allowance when the target changes, but an already-ready non-default PR can arrive at the default target already marked ready if the provider preserves that status across retarget. This can evade the draft convention without calling the ready command. The independent merge check still prevents an unauthorized trunk update. The stated ready/retarget race test only exercises an in-flight promotion and may miss an already-ready retarget.

Define the allowed state and action for an already-ready PR retargeted toward a held or open default target. For example, deny the transition or require verified re-drafting before retarget and a fresh target-specific ready admission. If the policy intentionally permits a ready presentation without a valid current promotion receipt, reconcile that behavior with #133 and make the distinction visible. Add a positive and denied retarget test beginning with an already-ready non-default PR, including a lost response. Verify actual provider status and that neither readiness nor CI authorization from the old target carries over.

## Disposition

Return revised source digests and the six finding dispositions for independent closure. The review concerns planning artifacts only. It conveys no hosted-test, implementation, production-protection or #159 pickup authority.
