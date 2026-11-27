# #9 initial pickup review

Grok 4.7 Build Fast verdict.

CHANGES REQUIRED

Dependencies match the accepted C04 set exactly: C02/#4, C54/#6, C55/#7, and C56/#8, on pinned `44ca79c17f80a657d6278cfd82cb988e8a19820a`, targeting `codex/core-472-integration`.

The CI and source-SAR order is sound. Tests first, then the installed C04 suite, affected package tests, Ruff, and diff checks. Exact-repository CI and separate Core hosted CI both pass before the PR leaves draft. Grok 4.7 source SAR and the trusted verifier run on that candidate before merge to integration, delivery recording, and Done.

Named proof is short of the C04 producer list. The pickup must name `Backend.read(snapshot, paths) -> Blobs`, `transact(op, expected) -> OperationResult`, `RelatedWriteSet(read_set, writes, events)`, `FinalizationIntent(kind, version, related_preconditions, payload)`, `WriteAuthorizer(owner, change)`, `PendingActionRunner(snapshot)`, `AttemptPreflight(context: OperationContext) -> PreflightResult`, and `OperationCategory(normal, authored_sync, stop_reconciliation, recovery)`. “Outcome” and “service ports” do not carry those names. Replay proof must state the `test_operation_cas` vectors in full: identical retry returns the prior result; a changed payload errors; a stale read-set re-evaluates or conflicts; a related-story update is atomic; the same behavioral cases stay valid for a later Git backend. Refusal proof must keep guards with no transition and no related write, and must keep prior snapshots and event append order.

Narrow preflight semantics need the same precision. No attempt in the pinned read-set yields explicit not-applicable. An attempt-bearing implementation mutation with no installed `AttemptPreflight` reports unavailable. `authored_sync`, `stop_reconciliation`, and `recovery` stay limited to their own declared operations. Attempt reconcile and expand stay category `normal` and require preflight. Category and request identity stay immutable across retries. Missing `WriteAuthorizer` refuses at the mutation boundary and stays distinct from an installed refusal, a fixture, and real registration. C04–C08 tests install explicit fixture authority. Negative tests unregister the named slot in a test composition. Pre-C31 attempt-bearing producers C27, C28, and C30 use an injected typed fixture preflight in test-only composition, while production stays unavailable when that implementation is absent.
