# #2 Governed PR lifecycle child reconciliation

**Accepted amendment** [Specification](../design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md), [implementation plan](2026-11-11-2-governed-pr-and-branch-lifecycle.md), and [review record](reviews/governed-pr-lifecycle/review-cycle.md), published together at `8939d9fff17599fe644604b5b267625b4bc5621f`. The original Core design and plan remain the baseline for the existing decomposition.

Planning requires linear history. The reviewed bytes were replayed without changes. The accepted specification revision is [f4cea43](https://github.com/kburson/aitm/commit/f4cea431c64c6cae38fd398c9f3b4ad4eab5df28) on planning, and the accepted plan revision is [2a6891f](https://github.com/kburson/aitm/commit/2a6891f956b71bf709215e619e4d1495bbe49b99). The two artifacts and final native acceptance are together at [b4c3245](https://github.com/kburson/aitm/commit/b4c3245f4697b30d9a47d118209807bce10c922d). The review record retains the original review-branch revisions.

The 79 original implementation leaves retain their issue IDs. Five scopes and estimates were revised within the four-hour cap. Six related contracts keep their implementation boundaries. Ten new leaves carry the remaining Core scope with individual estimates of **3–4 h**. The arithmetic is **257.5 h baseline + 3 h on existing leaves + 36.75 h on new leaves = 297.25 h across 89 leaves**. #228 and #229 retain separate preliminary estimates totaling 7.5 h. All estimates include verification and source-review engagement. Recheck the bound at each leaf's JIT.

The amendment uses the existing planned Python Core provider, store, state-machine and CLI interfaces. New Core leaves qualify their contracts with deterministic fixtures. The hosted adapter and runtime own external effects and host proof. The Core baseline release and local-only behavior keep their existing criteria.

## Existing children

### C13

[C13 / #14](../../14/story.md)

The provider extension registration, typed errors and capability discovery are the foundation. The managed action, result and capability extension is delivered by C80. Estimate **3 → 3 h**.

### C16

[C16 / #21](../../21/story.md)

Keep authoring and session binding generation behavior. C81 separately owns a stable managed incarnation that survives an ordinary C16 rebind. C83 owns the hosted pickup prerequisite. Estimate **4 → 4 h**.

### C20

[C20 / #25](../../25/story.md)

Reserve the canonical explicit delivery-target declaration with permanent story identity. Identical input replays its reservation. A differing repository, literal ref or resolved resource incarnation conflicts before a new dispatch. C81 owns the later lifecycle slot and host-effect claims. Estimate **3.5 → 4 h**.

### C22

[C22 / #26](../../26/story.md)

Publish the explicit target and pending hosted provisioning intent with the graduated Backlog identity and reciprocal graph relationships. Resolve branch-backed parent targets separately from Backlog parentage. Preserve local-only graduation. Test explicit default/no-parent/aggregate targets and refusal or pending for missing/unbound targets. C82 handles existing-story backfill. Estimate **3.5 → 4 h**.

### C39

[C39 / #46](../../46/story.md)

Positive observation and exact delivery mapping remain the source of proof. C86 consumes that evidence and accounts for attested bootstrap history without changing the observation contract or granting admission. Estimate **3.5 → 3.5 h**.

### C40

[C40 / #47](../../47/story.md)

Keep the exact reviewed transform contract. C86 consumes the mapping for any verified bootstrap rewrite or omission. The managed wrapper remains a separate consumer. Estimate **3 → 3 h**.

### C41

[C41 / #48](../../48/story.md)

Keep exact admission and recovery for the literal target. C88 consumes the typed boundary for managed targets. The GitHub default target needs a positive #158 host receipt in addition to Core admission. Estimate **3.5 → 3.5 h**.

### C43

[C43 / #50](../../50/story.md)

Expose a replay-safe terminal action envelope keyed by the exact completed or retired incarnation and usable only after shared publication. Exercise restart and duplicate replay. C85 supplies retirement-specific action policy and effect orchestration. Estimate **3 → 3.5 h**.

### C62

[C62 / #63](../../63/story.md)

In the aggregate required-scope evaluator, require the explicitly designated integration delivery to satisfy its upstream obligation before closing the epic. Hold when the owner is abandoned pending accepted scope replacement or revision. Reject self-targets and keep pure aggregate behavior. Managed branch, delivery and source proof are separate leaves. Estimate **3 → 4 h**.

### C76

[C76 / #79](../../79/story.md)

Keep the tagged, nonempty ordinary source guard and its evidence contract. C86 adds the separately registered, tightly scoped alternative only for a designated integration delivery. Estimate **3 → 3 h**.

### C79

[C79 / #80](../../80/story.md)

Expose the exact verified-delivery and required-completion record from the successful sign-off path for later retirement admission. Prove failed or stale sign-off does not qualify and pending cleanup does not revoke verified delivery. C85 owns the terminal dispatch and cleanup. Estimate **3 → 3.5 h**.


Additional native predecessor links from [C64 / #58](../../58/story.md), [C67 / #66](../../66/story.md), [C75 / #82](../../82/story.md) expose their existing restart fixture, graduation and CLI audit results to the new leaves. Each added edge has reciprocal records. Existing edges and unrelated children retain their prior scope.

## New Core leaves

### C80

[C80 / #233](../../../002/233/story.md) · Managed provider contracts and capability results

- **Estimate** 3.5 h, P1/S.
- **Predecessors** [C13 / #14](../../14/story.md).
- **Owned areas** src/aitm_core/providers/managed.py and GitHostProvider extension registration; packages/aitm-core/tests/unit/test_c80.py.
- **Produces** Typed effect and capability boundary shared by Core, the GitHub adapter and runtime.
- **Proof** Exercise registration of scoped provisioning, observation, readiness, delivery and retirement capabilities, typed pending/unsupported/refused results and receipts. Missing or unqualified capability stays unavailable. No provider endpoints are called.

### C81

[C81 / #234](../../../002/234/story.md) · Managed incarnation reservation and effect claims

- **Estimate** 4 h, P1/S.
- **Predecessors** [C16 / #21](../../21/story.md), [C20 / #25](../../25/story.md), [C22 / #26](../../26/story.md), [C43 / #50](../../50/story.md), [C64 / #58](../../58/story.md), [C80 / #233](../../../002/233/story.md).
- **Owned areas** src/aitm_core/managed/incarnations.py and claims.py; packages/aitm-core/tests/integration/test_c81.py.
- **Produces** Stable resource identity and durable per-effect claims for pre-pickup, current session and terminal service roles.
- **Proof** Reuse the C64 two-clone fixture. Race different operation and incarnation proposals for one permanent story/repository/role. One CAS slot wins. Ordinary rebind keeps the incarnation and fences the old session. Duplicate effects share one claim, unsent claims emit zero writes, and sent ambiguous effects hold until positive adoption or proven safe replay. Reject foreign lookalikes and same-ref/OID reuse while the old request can land.

### C82

[C82 / #235](../../../002/235/story.md) · Explicit target backfill for graduated stories

- **Estimate** 3 h, P1/S.
- **Predecessors** [C75 / #82](../../82/story.md), [C81 / #234](../../../002/234/story.md).
- **Owned areas** src/aitm_core/managed/targets.py; packages/aitm-core/tests/integration/test_c82.py.
- **Produces** Published target backfill entry point independent of branch creation, with deterministic read-set and validation.
- **Proof** Exercise authorized publication for an existing numbered story. Resolve the literal repository/ref and optional target incarnation. Deny unauthorized, absent, self, sibling, stale and implicit-default substitutions. Identical backfill is replay-safe and an ambiguous old target leaves provisioning pending.

### C84

[C84 / #236](../../../002/236/story.md) · Dependent admission and retirement fence

- **Estimate** 3.5 h, P1/S.
- **Predecessors** [C81 / #234](../../../002/234/story.md).
- **Owned areas** src/aitm_core/managed/retirement_fence.py; packages/aitm-core/tests/integration/test_c84.py.
- **Produces** A shared order for parent-incarnation admissions and retirement, consumed by provisioning, retarget and terminal cleanup.
- **Proof** Race child provisioning, reparent and retarget against retirement at an unchanged parent OID. A winning dependent holds the ref and a winning fence rejects later dependency admission. In-flight or uncontrolled host routes remain pending. Restart reproduces the same admission order.

### C83

[C83 / #237](../../../002/237/story.md) · Published branch and draft provisioning

- **Estimate** 3.75 h, P1/S.
- **Predecessors** [C82 / #235](../../../002/235/story.md), [C84 / #236](../../../002/236/story.md).
- **Owned areas** src/aitm_core/managed/provision.py; packages/aitm-core/tests/integration/test_c83.py.
- **Produces** Resumable pre-pickup provisioning, branch/draft receipts and typed content-free bootstrap provenance.
- **Proof** With deterministic doubles, publish before effects. Resume separate ref and draft claims after each lost response. Verify exactly one draft and explicit default/non-default target, record exact bootstrap OID, parent and unchanged tree when required, and block pickup before the draft is verified. Bootstrap CI supplies provisioning evidence only.

### C85

[C85 / #238](../../../002/238/story.md) · Terminal managed PR and worktree retirement

- **Estimate** 4 h, P1/S.
- **Predecessors** [C79 / #80](../../80/story.md), [C83 / #237](../../../002/237/story.md).
- **Owned areas** src/aitm_core/managed/retire.py; packages/aitm-core/tests/integration/test_c85.py.
- **Produces** Replay-safe terminal retirement orchestration using the dependent fence, exact receipts and owning worktree manager.
- **Proof** After completion or abandonment, reconcile effects, retain a merged PR and delivery mapping, close an open abandoned PR and retire only the bound exact ref and owned worktree. Verify outstanding dependents, conditional delete or hold, host retarget invalidation, and a recoverable scrap source before deletion. Lost responses resume the same terminal intent.

### C86

[C86 / #239](../../../002/239/story.md) · Composed-source eligibility for integration delivery

- **Estimate** 4 h, P1/S.
- **Predecessors** [C79 / #80](../../80/story.md), [C83 / #237](../../../002/237/story.md).
- **Owned areas** src/aitm_core/managed/composed_source.py and the C76 source guard extension; packages/aitm-core/tests/integration/test_c86.py.
- **Produces** A typed composed-source receipt and an explicitly scoped C76 guard path.
- **Proof** Drive Develop exit for the designated integration story with an exact nonempty delta mapped from verified child deliveries. Bind its literal upstream, pinned baseline, incarnation and exact head/tree. Test distinct nested non-default upstream and wrong-default/sibling, stale/empty/unexplained source, recorded versus foreign empty bootstrap, and separate current Test, independent Review and C41 admission.

### C87

[C87 / #240](../../../002/240/story.md) · Installed managed lifecycle commands and operation catalog

- **Estimate** 4 h, P1/S.
- **Predecessors** [C67 / #66](../../66/story.md), [C82 / #235](../../../002/235/story.md), [C85 / #238](../../../002/238/story.md).
- **Owned areas** src/aitm_core/cli/catalog.py and managed_lifecycle.py; packages/aitm-core/tests/integration/test_c87.py.
- **Produces** One coordinated extension to the Core route registry and the installed managed lifecycle entry points.
- **Proof** Run installed help and versioned catalog with explicit command, argument, capability and result schema parity. Invoke create/reconcile, pickup, backfill and terminal lifecycle against Core fixtures. Missing handlers or capability remain unavailable. The catalog cannot provide direct provider access.

### C88

[C88 / #241](../../../002/241/story.md) · Core policy for managed PR operations

- **Estimate** 4 h, P1/S.
- **Predecessors** [C41 / #48](../../48/story.md), [C84 / #236](../../../002/236/story.md), [C86 / #239](../../../002/239/story.md).
- **Owned areas** src/aitm_core/managed/operations.py; packages/aitm-core/tests/integration/test_c88.py.
- **Produces** Provider-neutral admission for scoped observation, push/refresh, ready/retarget and merge, without a generic proxy.
- **Proof** Use deterministic broker doubles to deny unqualified routes, stale runtime scope and cross-story operations. Scope observation to the bound PR and allowed evidence. Enforce dual-role target write policy, invalidation on retarget, C41 and default-only host prerequisites. Check that managed non-default delivery ignores the trunk hold, and a positive #158 boundary without qualified readiness holds integrated repair.

### C89

[C89 / #242](../../../002/242/story.md) · Installed managed PR and evidence commands

- **Estimate** 3 h, P1/S.
- **Predecessors** [C87 / #240](../../../002/240/story.md), [C88 / #241](../../../002/241/story.md).
- **Owned areas** src/aitm_core/cli/managed_pr.py; packages/aitm-core/tests/integration/test_c89.py.
- **Produces** Thin installed command handlers and a catalog/dispatch contract for aitm-github and aitm-harness.
- **Proof** Through the installed entrypoint, invoke authorized push/refresh, ready/retarget, merge and scoped PR, review and CI evidence reads through the same Core dispatcher. Compare help, catalog, typed results and denied routes. Keep unavailable host operations visible as unavailable. Skill/MCP parity and real hosted controls are the receiving packages' fixtures.


## Package handoffs and proof order

- [M2 aitm-github draft](../../../../drafts/2026-11/20261108-1310-github-extension/draft.md) owns actual draft/CI, hosted branch lifecycle, scoped provider effects, ready/retarget reconciliation, exact non-default delivery and the default-target #158 handoff. Use temporary AITM refs. Qualify automatic deletion and host-driven retarget or closure before allowing managed retirement. A refusal supplies denial evidence.
- [M3 aitm-harness draft](../../../../drafts/2026-11/20261108-1310-harness/draft.md) owns runtime-attested caller identity, direct Git/API isolation including anonymous routes, and installed CLI/skill/MCP parity. Joint managed readiness needs a real provider/runtime capability receipt.
- [#158 qualification](../../../001/158/plan/2026-11-11-158-merge-only-qualification.md) owns default-target writer exclusivity and exact base/head/tree and in-flight ordering with synthetic input. Its positive host receipt and managed readiness are separate prerequisites for hosted repair. The [#133 integration plan](../../../001/133/plan/2026-11-11-133-merge-only-stop-the-line.md) owns T34 and T36–T40 and the actual scheduled failure, repaired trunk pass and fresh post-release TIA evidence.
- #159 retains its existing native blockers #157 and #158. Production protections and #103 changes require their existing authorization. No trial or branch protection change is part of this reconciliation.

## Readback and boundary

[Verified native issue, body, Project and dependency receipt](governed-pr-lifecycle-reconciliation-receipt.json). The initial baseline ledger, new leaf records, reciprocal relationships and append-only event updates are retained on planning. The unchanged historical accepted documents preserve their prior hashes. All newly created children are Backlog. The applicable child Design, Plan, JIT and pickup checks still govern implementation.
