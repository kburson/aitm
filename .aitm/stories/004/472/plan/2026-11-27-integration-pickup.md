# #472 Trusted Git story store pickup

Delivery ledger ordinal 3. Project #24 epic rank 30. Build from verified trunk
`44ca79c17f80a657d6278cfd82cb988e8a19820a`. C56/#8 landed at `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` and C110/#497 landed at
`44ca79c17f80a657d6278cfd82cb988e8a19820a`. Verify each child’s current prerequisites, pinned
source and scope before its pickup. Process the children in rank order.

| Rank | Issue | Accepted delivery |
| ---: | --- | --- |
| 10 | #9 / C04 | Typed operation and storage ports, MemoryBackend and reusable transaction semantics. Preserve retry, refusal, conflict, authorization, attempt and atomic related-write behavior. |
| 20 | #10 / C05 | Pinned Git snapshot reads and same transaction contract through temporary-index and ref CAS. Prove isolation, interrupted publication and retry. Use the mandatory injected validation gate. |
| 30 | #11 / C06 | Validate the planning root, graph and eligible data paths. Scope ref/worktree exclusion to the literal target, record its cooperative limit and keep unavailable forward repair fenced. |
| 40 | #12 / C07 | Resolve committed configuration and workflow from the anchored default commit. Preserve the existing accepted review policy, routing and freshness distinctions. C110 on trunk qualifies affected policy inputs. C90 owns parsing and C98 owns cutover. |
| 50 | #13 / C08 | Quarantine untrusted candidates and prove continuity, crash/retry and integration on trunk. Verify the exact reviewed composition of C04–C08 and required sibling deliveries. |

Use the accepted C04–C08 contracts and the C07 reconciliation in publication
`0945941c6c024b6dd621202b2456696ae1df0154`. Provide only the shared
integration resource before leaf delivery. Keep #13 implementation and
trunk admission gated by the reviewed sibling receipts. Re-pin JIT pickup at
each delivered integration base. Run tests first for the named acceptance
and refusal paths and verify the installed package.

Require passing hosted repository and separate hosted Core CI on each
source candidate and the final trunk candidate. Verify exact base, head and
tested tree. Remove draft only after passing CI. Require a fresh Grok 4.7
source SAR and the trusted verifier before each exact merge. Confirm all
required sibling landings, verify the final trunk delivery, then sign off the
integration owner and epic. The plan does not authorize production adoption.
