# #199 Claude causal revision proof implementation plan

> **For agentic workers:** Use the accepted task-by-task implementation workflow. Run red, implement the smallest source seam, and run green before freezing the candidate.

**Goal** Carry verified Claude predecessor and later evidence through the existing monitor reader and writer custody so later journal adjudication can prove actual native succession.

**Architecture** Keep the legacy usage and checkpoint formats unchanged. Emit an ephemeral monitor-only causal witness where the Claude walk accepts an exact prior and successor. The fixed scanner read supplies physical ordinal and authenticated keyed row prefix, including untimed terminal evidence. ScopeState issues the witness only from the same confirmed source read and separately evaluates original attribution and later capture eligibility.

**Tech stack** Python 3.13, locked uv, current Claude scanner/adapter, Registry and ScopeState. No external dependency.

**Spec** #100 accepted design request ownership, provider adapters and routing/revision semantics, and #118's exact M08b split. The exact source tree is cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad on literal trunk 1452999b2f0f5a90161e39862458029c0084772c. [Verified delivery](https://github.com/kburson/aitm/pull/200)

## Scope and estimate

Codex owns #199 and closure. Proposed Size M, 3.75 implementation agent-hours. Checkpoint at 2.25 implementation hours. If the verified sideband or monitor diagnostic seam threatens the four-hour cap, stop Develop and return to independent planning for an explicit split with all #119 prerequisites intact. Rank 225 remains. Set Size and Estimate when exact Refine/JIT passes, and Start Date only on Develop. The clean locked literal-trunk baseline passed 920 product and CLI tests and 182 helpers, Ruff, whitespace, and raw line coverage of 10,101/11,029 product and 778/821 helpers. Native #118 is Closed Done and #119 reads #118 and #199 as direct prerequisites.

Read and write paths use packages/aitm-usage. Change only src/aitm_usage/sources/claude.py, sources/scan.py, sources/adapter.py, monitor_scope.py and focused tests/test_monitor_adapters.py and tests/test_monitor_scope.py. Reuse the exact Registry span disposition and capture confirmation. If a shared public data shape or persisted format change proves necessary, return to planning. M08b1 makes no journal, ledger or coordinator change. M08b2 owns durable decisions and successful progress. Production, release, live account activity, Epic #2 and C01 are outside this leaf.

## Review focus

- Multiple authentic revisions in one cold read must each bind exact material to its own predecessor, with ordered distinct later spans. A numeric revision or matching request ID alone gives no authority.
- A project or story switch at a later native position may change later requests without moving the original usage project, story, time or interval.
- A shared read can be legal for project B while the original project A has no capture entitlement for the later row or an indivisible cumulative span crosses a disable. Re-enrollment and a new location cannot legalize that update.
- An untimed cost-state row's physical ordinal differs from its preceding timed context and can land outside an allowed interval. A timed result is valid only on the existing successful exact reconciliation path.
- A fixed-prefix copied read may reproduce the logical witness. A copied handle, wrong writer, mixed physical read, changed prefix, unknown incarnation, foreign request, unknown usage or ambiguous overlap must not issue forward authority.
- Quota-only diagnostics retain exact monitor provenance. A same-code genuine usage/coverage gap remains a replay obligation. Legacy output stays byte-for-byte equivalent on the established fixtures.

## Interfaces

The private monitor producer callback receives the actual predecessor Revision, successor Revision and committing SourceFrame or SidebandFrame at the accepted emission. It creates one immutable adapter-side witness for the exact successor object. The witness contains the provider kind, service-keyed canonical observation and material fingerprints, original native identity and position, predecessor evidence ordinal, exact later evidence position, and keyed row-prefix witness. Physical locator, incarnation and complete cursor stay in the fixed-read context, separate from the copy-stable proof identity. No raw row or payload crosses the seam.

`ScopeState.verified_revision(batch: VerifiedScopeBatch, observation: NativeObservation) -> _VerifiedRevision | None` derives the ephemeral proof from the original issued batch and exact observation object. The result binds the original scoped owner and time, later capture eligibility and the exact writer and read. Its consumer must use the original proof with the exact batch, confirm current custody again before writing, and match the saved claim's original scope separately. The private typed producer distinguishes quota-only diagnostics before deduplication and labels one diagnostic quota-only only if no scanner or usage path emitted an identical diagnostic. The existing public diagnostics remain unchanged. M08b1 does not use this metadata to release progress.

## Tasks

### 1. Preserve the exact private producer edge

Files sources/scan.py, sources/claude.py, sources/adapter.py and test_monitor_adapters.py. Consume current complete FrameBatch and internal UsageWalk lineage. Keep logical proof private and bounded by the current fixed read, with no raw transcript payload in the witness.

- [ ] RED through the actual adapter for three valid rows of one Claude request, an unrelated row, a valid timed result and an actual untimed cost-state fixture. Require previous and successor normalized usage identities, original request/message/session/stream/epoch, later physical ordinal and keyed row-prefix witness. For terminal evidence use the actual committing row, keeping timed context separate.
- [ ] Record an edge only at the exact accept point with the real predecessor. Reuse the validated previous Revision object and exact new normalized record. Distinguish timed assistant, timed result and cost-state. The normal M08b1 proof does not issue for aggregate fallback, retractions or parser diagnostics. Invalid counts or changed original attribution do not gain forward authority.
- [ ] Carry scanner prefix evidence privately on the actual SidebandFrame when it is already inside the commit frontier. Keep the legacy typed result and checkpoint codecs unchanged. Keep predecessor/successor stable across exact physical archive copies and carry physical cursor custody independently. Derive keyed witness from the verified row and allowlisted material. Do not forward raw rows, paths, prompts, tool args, account IDs or unkeyed private payload digests.
- [ ] Preserve distinct monitor-only quota evidence provenance from the rate-limit or missing-account path. Leave existing emitted diagnostics intact in legacy service and journal routes. Exact rate-limit provenance must not mark a real scanner or usage gap with the same code as quota-only. Include a same-code negative and mixed case.
- [ ] GREEN adapter and Claude tests, including staged multiple edges and foreign, missing, disabled-source and ambiguous-lineage negatives. Compare legacy records, diagnostics and exact checkpoint serialization against existing fixtures.

### 2. Bind current writer-issued source and capture eligibility

Files monitor_scope.py and test_monitor_scope.py. Consume exact native edge attached to the same AdapterBatch observation and fixed physical read. Produce a private writer-issued proof available to M08b2. Expose no claim mutation.

- [ ] RED with real Claude transcript, Registry capture epochs, neutral marker and ScopeState. Verify an ordinary same-project story switch between original and update leaves original project, story and time intact. Exercise a real prospective handoff or shared-source path with original A still entitled and require A's proof rather than B's later scope. Disable A while B can still read, write later evidence during the disabled span and re-enable A. Do not issue forward proof for the affected update or a cumulative change spanning the disabled interval.
- [ ] Validate the exact issued batch, observation and producer edge, authenticated prefix, service key, exact original route, live original-owner span entitlement and distinct later evidence span. Check the exact successor row for every edge. For indivisible cumulative token changes also check the full predecessor-to-successor evidence interval. A terminal availability-only revision preserves exact previously eligible counters and requires its own later row eligibility. Confirm native/source and current durable scope/registry through existing writer authority before returning a proof. Treat any missing witness, changed epoch, original scope dispute or foreign source as held. A caller-created DTO or same-looking old object must not confer authority.
- [ ] RED/GREEN for untimed cost-state after a disabled boundary where its preceding timed context is eligible. Add physical replacement or mixed source witness rejection and exact copy identity without permission to overwrite the first owner's physical frontier. Keep older source evidence and historic attribution available, but no cursor release here.
- [ ] Run related Claude adapter, Registry, scope, journal and legacy Ledger tests, then the locked full product and CLI suite, fixed helper suite, Ruff and whitespace. Verify neither the accepted plan nor existing journal database code changed.

## Delivery

Publish one exact signed-source PR to literal trunk after local frozen checks. Retain the prior baseline and current exact SHA/tree, and require all six hosted jobs plus the trusted signed verifier and raw replay. Request a separate exact independent post-CI source verdict. Verify live requirements and exact ordinary merge parents, tree and source diff. Obtain original signed retrospectives and complete planning and Project Close before releasing the next pickup. #119 remains blocked through all split successors, including the independently verified folded producer and atomic journal intent.
