# #472 accepted pickup review

Independent Grok 4.7 Build Fast review. [First review](2026-11-27-integration-pickup-review-r1.md).

PASS

Epic #472 pickup matches the accepted packet on every checked gate. It can proceed in rank order from trunk `44ca79c17f80a657d6278cfd82cb988e8a19820a`.

**Ranks.** Ledger ordinal 3 and project rank 30 are #472. Children run 10 #9/C04, 20 #10/C05, 30 #11/C06, 40 #12/C07, 50 #13/C08. That order is the same as the dependency order.

**Predecessors and siblings.** Native prerequisites match the leaves: #9 on #4/C02, #6/C54, #7/C55, #8/C56; #10 on #9; #11 on #3/C01 and #10/C05; #12 on #5/C03, #11/C06, and #497/C110; #13 on #11 and #12. C56 is the #470 merge `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6`, an ancestor of the tip. C110 is the tip and is the #12 policy-fixture gate. Shared-file edges C01→C06, C06→C07, and C07→C08 stay on the leaf graph. #13 waits for reviewed receipts of #9–#12 on successive integration bases. Other epics keep their own gates. C90 parsing and C98 cutover stay outside this scope.

**Literal targets.** Work starts at the literal trunk tip above. Ref and worktree exclusion stays on the literal `target_ref`. Each child rechecks ancestors at its current base. Sibling commits land on the integration branch first. #13 and trunk admission use those pinned bases, then the final trunk delivery.

**Resource-only route.** The only pre-leaf step is the shared integration resource. Parent-eligibility checks on this route stay inside that preparation. C07 still consumes the C110 fixture and does not take the held policy set.

**Leaf scope and evidence.** Paths, ports, and proof files stay inside the accepted leaves: unit `test_c04.py`; integration `test_c05.py` through `test_c08.py`; affected contract suites; Ruff. C05 keeps an injected ValidationGate. C06 keeps the cooperative limit and fenced forward repair. C07 consumes `RefreshResult` and leaves network refresh and stale/unknown freshness with C08. C08 keeps quarantine, crash/retry, and the rule that a fetched receipt cannot nominate its anchor. The plan does not authorize production adoption.

**CI then SAR.** Each source candidate and the final trunk candidate need passing hosted repository CI and separate hosted Core CI on the exact base, head, and tested tree. Draft comes off only after that CI. A fresh Grok 4.7 source SAR and the trusted verifier are required before each exact merge. Sibling landings and the final trunk delivery are confirmed before integration-owner and epic signoff.
