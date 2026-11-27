# #472 first pickup review

Independent Grok 4.7 Build Fast verdict.

CHANGES REQUIRED

The child rank order is sound, and the CI/SAR merge sequence is sound. The pickup still cannot start: the leaf graph drops mandatory predecessors, the sibling gate is unnamed, and the resource-only route drops the scoped parent-check limit.

**Ranks.** Epic #472 at project rank 30 and ledger ordinal 3 matches the ledger row. Children run #9/C04 (10), #10/C05 (20), #11/C06 (30), #12/C07 (40), #13/C08 (50). That order respects C04→C05→C06→C07→C08. Keep it.

**Predecessor gates.** Carry these into the leaf issue graph and pin them on trunk `44ca79c17f80a657d6278cfd82cb988e8a19820a` before the child starts:

- #9/C04: C02, C54/#6, C55/#7, and C56/#8. The plan pins only C56 at `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6`. State that this commit is contained in the trunk tip.
- #11/C06: C01 as a mandatory shared-file predecessor, plus C05.
- #12/C07: C03 as a mandatory shared-file predecessor, plus C06. C110/#497 at the trunk tip clears the #12 policy-decision hold. Keep that pin, and cite the C07 reconciliation publication `0945941c6c024b6dd621202b2456696ae1df0154` as the policy text, separate from the code trunk.
- #13/C08: C07 as the mandatory shared-file predecessor, plus C06.
- Ledger ordinal 3 also depends on predecessor epics 1 and 2. Record those landings before epic pickup.

**Sibling gate.** Name the receipts that block #13 implementation and trunk admission: reviewed #9, #10, #11, and #12 on the re-pinned integration base. Re-pin JIT at each delivered integration base, then verify the exact base, head, and tested tree. C11, C13, C63, C20, and C22 stay outside this gate. C90 still owns parsing and C98 still owns cutover.

**Resource-only route.** Before any leaf delivery, provide only the shared integration resource, and keep parent checks scoped to that resource. #13 implementation and trunk admission stay behind the named sibling receipts.

**Leaf scope and evidence.** Bind every child to its accepted contract paths, produces, and the named pytest plus Ruff evidence. Preserve these boundaries in the pickup text: injected ValidationGate with no allow-all default; ref/worktree exclusion on the literal target, the cooperative-lock limit, and forward repair fenced until C10; C07 consumes RefreshResult and does not own network refresh; C08 owns quarantine, continuity, crash/retry, and stale/unknown freshness. Verify the installed `aitm-core` package. Production adoption stays out of scope.

**CI, then SAR.** On every source candidate and the final trunk candidate, require passing hosted repository CI and a separate hosted Core CI run, matched to the exact base, head, and tested tree. Remove draft only after both are green. Immediately before each exact merge, require a fresh Grok 4.7 source SAR and the trusted verifier. After the sibling landings and the final trunk delivery, sign off #13 and #472.
