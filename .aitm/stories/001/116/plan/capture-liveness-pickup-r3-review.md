# #116 M06 liveness pickup review round 3

Claude Opus 5.5, high effort, completed the independent local pickup review on November 10, 2026.

# Verdict: PASS

B1 is fixed. I found no new blocker. I used only the packet and no tools.

## B1: disable rejected because of source state

**Resolved.** The revised text says:

> "A proven substituted root, unsupported tuple or discontinuity can reject an enable. It cannot reject an otherwise valid disable. Apply that disable with the last verified prefix and an open-ended gap … Do not read the replacement root. Commit disabled permission so restoring the original root or binary cannot resume capture."

I traced each way a disable can end:

- **Proven substitution, tuple mismatch or discontinuity.** The disable applies. Permission is committed off, the affected streams get their prefix plus an open-ended gap, and nothing is read from the replacement root.
- **Source failure that cannot yet be classified.** This includes a ValueError inside a valid tuple, duplicate candidates and transient I/O. The command stays queued with a sanitized reason and fail-closed read bounds. Each stream is read no further than its persisted fence, or its existing authorized prefix if it has no verified position. If the source is later restored, the held command applies normally. Saved arms are never moved, so restoration cannot widen reads.
- **Rejection.** This happens only for invalid typed input, an invalid envelope, or an unknown project or source. All of these come from the registry or the request, not from the source's physical state.
- **Required test.** "A committed disable still blocks reads after the original source root or supported tuple is restored" is listed.

So a source-side substitution or tuple change can neither reject a valid disable nor let reads resume when the source is restored. The previous reviewer's preferred fix was adopted, and holding is kept only for cases that genuinely cannot be classified.

## Prerequisites checked against the source excerpts

**Claude original ordinal: satisfied.**
- `RequestPrefix` stores `ordinal` (it must be non-negative) and `complete`.
- `ProviderCheckpoint.request_prefix` keeps those entries, including provisional ones, because `RequestPrefix(req, msg, record.boundary.ordinal, counts, stopped)` takes `stopped` as its `complete` value.
- The revision path uses `replace(record, tokens=…, …)`, which leaves `boundary` unchanged.
- `lineage()` requires `record.boundary.ordinal == prefix.ordinal`, so a revision cannot change the stored ordinal.

The original ordinal is therefore available from the existing checkpoint without changing any format. The excerpt does not show whether `request_prefix` is ever pruned. That should be covered by the dead-Claude-commit-run test rather than treated as a blocker.

**Durable submission order: satisfied, with one caveat.**
- `_QueuedCommand.order` is a positive integer stored inside the published bytes, and `_decode_publication` checks those bytes exactly.
- It is assigned under `publication()`.
- An exact retry reuses the earlier publication or receipt and never assigns a new order.
- `_pending` refuses duplicate orders, and `iter_pending` sorts by order.
- The terminal receipt is committed before `discard`, so a retry after retirement gets the receipt.

**Caveat:** the order is `max(pending)+1`. It correctly ranks the commands currently pending, but numbers can be reused once commands are retired. It is not a global sequence. The registry may use it only to compare commands pending together in the same pass. It must never be persisted as an identity or compared after retirement. The pickup keys identity on the envelope, so this is consistent, but the implementation must not cross that line.

**Arm at or after the persisted cursor: stated.** "Must equal or exceed" is in the text. A lower position is effectively covered by the truncation and discontinuity rules, which keep the prefix and gap the rest.

## Earlier clarifications (all addressed)

- A stream armed in a later pass uses that later position and gaps the interval since its prior prefix.
- The absence walk matches the prior file incarnation anywhere in the installation.
- The modules touched are named: scanner, adapter, Codex and Claude readers, registry and status, with their existing tests.
- Persistent holds show a sanitized proof-unavailable reason.

## Optional wording edits (not blocking)

1. **Tuple mismatch scope.** State that a tuple mismatch, like root substitution, applies prefix plus gap to every stream of the source and takes no new physical arm under the mismatched tuple. The outcome is already safe because permission is committed off. This only affects how complete the accounting is.
2. **Partial row that completes.** Name the test where a partial final row completes after arming and stays inside the gap. The "growth race after arming" test probably covers it, but not explicitly.
3. **Persistent holds.** Say outright that a persistent hold blocking later commands on the same edge is accepted as fail-closed.

## Already accepted (unchanged)

- Only writer-owned native proof reaches the direct calls, and the proof namespaces stay separate.
- The strict absence walk, absolute physical ordinals, and refusing an origin for an empty file.
- Per-stream read limits while a disable is pending.
- No reads after revocation.
- Budget: 4.0 − 1.7 = 2.3 hours, with planning reopened if exceeded.
- Codex owns integration.

## Later integration (M07 and beyond)

- Collection and arming are serialized under the coordinator lease, using the freshest persisted cursor.
- The pending-disable read bounds are enforced by the coordinator. M06 only exposes them.
- Unread rows below the fence when a disable applies are reported as a coverage gap at settlement, which uses only already-staged evidence.
- Scope, qualification, the scheduler, migration and operations stay with their current owners.
