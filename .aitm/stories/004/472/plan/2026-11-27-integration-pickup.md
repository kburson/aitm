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

## Verified prerequisites and source ownership

The exact trunk tip `44ca79c17f80a657d6278cfd82cb988e8a19820a` contains the reviewed
[#470 trunk delivery](https://github.com/kburson/aitm/pull/529) and
[#471 trunk delivery](https://github.com/kburson/aitm/pull/536). The earlier
#470 merge `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6` is an ancestor.
Its delivered child implementations from PRs #526 and #530 through #534 are
available on trunk. The #471 landing includes the C110 decision fixture
required by C07. The accepted C07 policy amendment is planning publication
`0945941c6c024b6dd621202b2456696ae1df0154`.

| Child | Confirmed native issue prerequisites | Contract paths and primary proof |
| --- | --- | --- |
| #9 | #4/C02, #6/C54, #7/C55, #8/C56 | `models/operations.py`, `store/backend.py`, `store/memory_backend.py`. Produce the typed storage and operation ports with a MemoryBackend contract. Installed `tests/unit/test_c04.py` plus Ruff. |
| #10 | #9/C04 | `store/git_backend.py`, `store/objects.py`. Produce pinned Git snapshot and atomic operations under an injected mandatory ValidationGate. Installed `tests/integration/test_c05.py` plus C04 contract and Ruff. |
| #11 | #3/C01 and #10/C05 | `store/validation.py`, `store/gate.py`, `services.py`, `cli/planning.py`. Produce the planning history validator and literal-target ref/worktree gate. Keep the cooperative exclusion limit explicit and forward repair fenced until C10 verifies it. Installed `tests/integration/test_c06.py` plus Ruff. |
| #12 | #5/C03, #11/C06 and #497/C110 | `config.py`, `models/config.py`, `store/installation.py`, `services.py`. Produce committed policy resolution and change classification. C06 is also the mandatory shared-file dependency. Consume RefreshResult without owning network refresh. Installed `tests/integration/test_c07.py` plus Ruff. |
| #13 | #11/C06 and #12/C07 | `store/continuity.py`, `store/fetch.py`, `services.py`. C07 is also the mandatory shared-file dependency. Produce shared frontier and refresh with quarantine, crash/retry and stale/unknown freshness. Installed `tests/integration/test_c08.py` and composed proof plus Ruff. |

Paths refer to the `packages/aitm-core` package and its `src/aitm_core`
source tree. The current native graph already has the registered prerequisites
shown above. Verify candidate ancestors and delivered contracts at the current
literal target before each child starts. Later sibling commits are first
delivered to the integration branch.

Prepare only the shared integration resource before leaf delivery. Scope any
parent eligibility check for this route to resource preparation. Before #13
implementation and trunk admission require the exact reviewed merge receipts
for #9, #10, #11 and #12, pinned to the successive integration bases. Any
epic consumer outside this set retains its own pickup and dependency gates.
Keep C90 workflow parsing and C98 cutover in their established scope.

Require passing hosted repository and separate hosted Core CI on each
source candidate and the final trunk candidate. Verify exact base, head and
tested tree. Remove draft only after passing CI. Require a fresh Grok 4.7
source SAR and the trusted verifier before each exact merge. Confirm all
required sibling landings, verify the final trunk delivery, then sign off the
integration owner and epic. The plan does not authorize production adoption.
