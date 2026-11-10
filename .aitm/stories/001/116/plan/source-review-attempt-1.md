# #116 independent source review hold

Declared-manual Claude Code `claude-opus-5-5` with medium effort requested. Exact head `91dd5852caa9519c7cee7e300ef1cb661e24b02d`, tree `4971d96e969c882fbb16c7183bb6ae9b6cfb4b87`. The [signed exact hosted run](https://github.com/kburson/aitm/actions/runs/42872458320/attempts/1) passed.

## HOLD: AITM #116 M06 at tree `4971d96e`

This review covers only the supplied packet. I ran no tools, did no live runtime check and did not replay CI myself. The hosted evidence agrees with itself: it names the reviewed tree, and the test counts add up (629 + 22 + 8 + 11 + 1 = 671). I'm relying on that evidence as given; I did not check its signature.

## Blocking finding 1: a capture change can be dated to an old native boundary, so re-enable can backfill disabled time

**Code evidence**
- `Registry.verify_boundary` accepts any boundary that appears in `ProviderAdapter().read_delta(locator, cursor)`. The caller picks `cursor`, and `None` rereads the whole stream. Nothing ties the proof to the stream's current frontier (its newest position) or to when the command was queued.
- `_epoch`'s only freshness rule is `proof.ordinal > previous.ordinal`. Nothing records how far the stream had reached when the last fence was set.
- `self._verified` keeps every proof made during the writer session. A proof verified long ago can still be applied later.
- `span_disposition` then trusts the fence ordinal as written.

**Scenario (re-enable backfill)**
1. Enable at ordinal 1, then disable at ordinal 50 (the stream's newest boundary at the time).
2. Usage continues at ordinals 51–200 while capture is disabled.
3. The owner re-enables. The verifier calls `verify_boundary(SOURCE, locator, ref_51, None)`, which finds `ref_51` in the full reread, so the proof is accepted. `_epoch` also accepts it because 51 > 50.
4. `span_disposition(..., 51, 200)` now returns `ELIGIBLE`.

That breaks the leaf rule that "re-enable cannot backfill the disabled interval" and the pickup rule that "a span in a disabled interval stays excluded after re-enable."

**Scenario (backdated disable)** The same path lets a disable be placed at ordinal 10 after spans 10–100 were already admitted. Those spans flip to `EXCLUDED`, which breaks the rule that work wholly inside an admitted epoch stays eligible.

`test_disable_reenable_excludes_late_disabled_interval` doesn't catch either case because it only uses the boundary that naturally comes next (`restart`).

**Needed:** store a native frontier for each stream (its cursor or last observed ordinal) alongside each epoch. Only accept a fence boundary that comes first after the frontier observed when the change is applied, read from that stored cursor. Throw away cached proofs once they've been used or the frontier moves.

## Blocking finding 2: a temporary lack of proof permanently rejects a command instead of keeping it queued

**Code evidence**
- `_apply` calls `verifier(payload)` inside `apply_pending`'s `try`.
- That `try` turns `ConflictError`, `LedgerError`, `OSError` and `ValueError` into a durable `REJECTED` receipt.
- `verify_boundary`'s normal signal that the next boundary hasn't been written yet is `LedgerError("Expected one verified native capture boundary")`.
- Only `_AwaitBoundary` keeps a command queued, and that is raised only when the verifier returns fewer streams than are known.

**Scenario:** The owner submits `monitor capture disable`. When the writer drains the inbox, the native reader has no new boundary yet, or a read fails briefly. The verifier raises, the command is recorded as `rejected`, and capture stays enabled.

The pickup requires that the coordinator "keeps it queued while required proof is unavailable." On a disable, this failure leaves capture running.

**Needed:** have verifier errors and missing proof raise `_AwaitBoundary`. Reserve `REJECTED` for invalid requests and stale or contradictory requests.

## Non-blocking risks (fix alongside the above)

- **Disable can't anticipate unenrolled streams:** a disable is rejected when the verifier supplies an unenrolled stream (`supplied != known`). The verifier only receives the `CaptureChange`, so it has no way to know which streams are enrolled. Pass the set of known streams to it.
- **One idle stream can stall an edge:** a held capture command on an edge also holds back every later command on that edge (`held_edges`). If an enrolled stream never produces another boundary, a later disable is stuck behind the held command indefinitely.
- **Doomed config is queued:** the `darwin` config in the CLI test queues successfully but can only be rejected at apply, since `_approve` requires `Darwin`/`Linux`.
- **Path checks that may misfire:**
  - In `check_legacy_mutation`, `root.absolute()` keeps `..`, which `_directory` rejects. That only fails closed after a project is adopted.
  - The monitor-root separation check compares an unresolved `self.root` against a resolved state path.

## Areas that pass on the evidence

- **Registry identity:**
  - Project UUIDs and state `(dev, ino)` identities are pinned.
  - Metadata and remotes can change without changing identity.
  - Identical or nested anchors and symlink aliases are refused in both directions (`_separate_anchors` checks ancestry both ways).
  - A changed state inode or adopted key is refused.
  - Readers don't take the coordinator lease and never create the root. A missing root reads as "not adopted" or "unavailable".
  - Reading a snapshot survives an atomic replacement.
- **Command contract:**
  - Command IDs are stable and digests are canonical.
  - Retrying the exact same command converges to one receipt, and reusing an ID for different content conflicts, both before and after cleanup.
  - The receipt is committed before the queue entry is removed, and a replay re-syncs it. Status prefers the durable receipt and rereads it if the queue entry disappears mid-lookup.
  - Lock order is coordinator, then publication. Enqueue and status never take the coordinator.
  - Raw paths stay out of CLI output.
- **Legacy adoption:**
  - There's a check before reading any input. Register uses the read-only opener first and checks again under the writer guard, and again after a writer-lock refusal.
  - The anchor command checks again under the legacy inbox lock, before staging or publishing, using the split `_enqueue_locked` body with no nested `flock`.
  - Behaviour before adoption is kept, including enqueueing while the collector holds the writer guard.
- **Ownership:**
  - M06 never sets `adopted_key_id` outside tests, so actual cutover stays with M16.
  - Both locks are exposed for M16 (`Registry.writer`/`lease`, `ControlInbox.publication`, `_inbox_publication`).
  - Legacy `enqueue_command` behaviour, which M07 owns, is unchanged apart from the refactor.

**Verdict: HOLD on findings 1 and 2.**
