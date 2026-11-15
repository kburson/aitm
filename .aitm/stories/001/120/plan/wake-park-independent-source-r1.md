[11:50:22]
SOURCE_120: HOLD

The decoder fix is correct and the recorded red→green run proves it. The transport, framing, issuer, persistence and restart paths match the accepted JIT. One scheduler defect drops a verified stop, and two required JIT behaviors or tests are missing. The candidate must be revised before signed delivery can proceed.

## Blocking

1. **A verified stop for a new turn is dropped. (`monitor_scheduler.py`, `Scheduler._admit`)**
   - **Cause:** the stale-stop guard counts every other turn as newer when `previous is None`. The condition is `(previous is None or item.generation > previous.generation)`.
   - **Effect:** say turn 1 has a record and turn 2 sends only a stop, as a text-only turn without a change hook would. The resolver has verified turn 2 as current, but the scheduler still returns `False`. No `WakeHint` is issued, nothing enters Settling, and turn 2's final catch-up is never scheduled.
   - **JIT conflict:** the JIT says a validated stop "puts eligible current work into Settling and requires one final verified catch-up." The rule against parking newer work applies only to an *older* turn. A turn with no record is not older, because its hint would take `self._generation + 1`.
   - **Required fix:** compare generations only when `previous is not None`.
   - **Required test:** turn 1 changes and parks, then turn 2 sends a verified stop only. The test must show turn 2 is Settling, receives one catch-up and then parks, and that turn 1's state is retained. `test_stale_stop_cannot_park_newer_turn` must stay green.

2. **Within-group rotation is by slot, not by stream. (`take_due`)**
   - **Cause:** `by_group[group]` orders slots by `(due, name)`.
   - **Effect:** a stream with two due turns is served twice before another due stream in the same project.
   - **JIT conflict:** the JIT requires "within a group take one due stream per round before taking its next."
   - **Required fix:** rotate streams inside each group.
   - **Required test:** two streams in one project, one of them with two due turns, under `take_due(now, 1)`.

3. **Required JIT tests are missing.**
   - **#119 hold boundary:** `test_full_project_does_not_starve_another_due_project` models capacity by calling `finish(caught_up=False)` directly. The JIT requires the isolated coordinator fixture to exercise #119's hold and exact acknowledgment boundaries. Drive the full-project case through that hold.
   - **Stable root inode:** this item is named in the JIT's Include list and has no test. After `listen()`, replace or rebind the root or `wake.sock`. Assert that `serve_once` and `_retire` refuse, and that the foreign entry is left untouched.

## Verified sufficient

- **Decoder failure:**
  - `RecursionError` is now converted to `ValueError` inside `_parse_frame`. It is reachable within 2,048 bytes through about 1,000 levels of nesting.
  - `UnicodeDecodeError` and `JSONDecodeError` are already subclasses of `ValueError`.
  - `serve_once` refuses exactly one frame and the listener stays live.
  - The test asserts no resolver call and no due work, then a successful second intake.
  - The red log shows the unpatched `RecursionError` escaping.
- **Frame:**
  - Accepted bytes must equal the canonical re-dump plus LF, which covers repeated or unknown keys, spacing, escapes and trailing data.
  - `v` must be an `int`, so `bool` is refused.
  - A BOM fails in `json.loads`.
  - A lone surrogate fails closed as `UnicodeEncodeError`, which is a `ValueError`.
  - The limits hold: 2,048 bytes, a 1,024-byte locator, no NUL, one bounded read at a time and a 30 ms deadline.
- **Endpoint:**
  - The address is checked against the 103-byte limit before bind.
  - The absolute `lstat` is compared with the `dir_fd` `lstat`.
  - The socket must be same-owner.
  - Mode is set only through non-follow `chmod`. `NotImplementedError` refuses.
  - The inode is rechecked before `listen`.
  - Cleanup removes only an unchanged inode.
  - Reclaim requires mode 0600, `ECONNREFUSED`, an unchanged path and the lease.
  - An unsafe endpoint refuses with an operator-named removal message.
- **Peer credentials:**
  - UID is checked before parse.
  - The Darwin and Linux ctypes calls pin argtypes, restype, size and `pid > 0`, and fail closed.
  - The Linux decoder control passed.
- **Issuer:**
  - `WakeHint` has `init=False`.
  - The capability belongs to one scheduler and is consumed on use.
  - A bare `WakeHint()` and unresolved requests never reach `notify`.
- **Durability and privacy:**
  - Publication completes before work becomes due.
  - A refused publish creates no due work.
  - Restart re-reads, re-seals, checks and fsyncs every slot, and drops in-flight leases.
  - Only keyed references, disposition, the fact and the generation are persisted.
- **Leases and retry:**
  - The TTL is positive, injectable and rejects `bool`.
  - Stale and expired completions are refused.
  - Backoff runs from 0.25 to 8 seconds.
  - A later append reopens Parked and clears the backoff.
  - Group round-robin is retained across calls.
  - `limit` is capped at 64 or below.
- **Sender, park and launcher:**
  - The sender covers absent, refusing and saturated endpoints within 30 ms, with write-side EOF and no reply wait.
  - Park touches only wake slots.
  - The scope is exactly 4 files, with `cli.py` unedited.
- **Inherited helpers:** `_publish`, `_read_private`, `_private_child`, `_publication`, `_pin_directory`/`check`, `Registry.lease`, `source_evidence`/`validate_source_ref` and `default_monitor_root` are sufficient as excerpted. Blobs are identical between the frozen JIT base and the current base.

## Non-blocking

- **Dir-fsync failure:** a failure after the link leaves on-disk bytes ahead of memory. Later *different* updates to that slot fail closed until restart, while an identical retry recovers. Consider a readback-adopt path and a fault test.
- **Darwin saturation:** a saturated AF_UNIX backlog can also return `ECONNREFUSED` on Darwin. Reclaim safety therefore rests on coordinator-lease exclusivity. Document that assumption.
- **`SourceRef` validation:** `SourceRef` (`types.py:148`) was not excerpted. Confirm it rejects a non-`str` value, so a park frame like `"session":123` cannot raise `AttributeError` past `serve_once`.
- **Untested items:** `sources/hooks.py:main()` and the `WRONG_SOURCE_TYPE` / `STOP_WITHOUT_CURRENT_TURN` variants have no tests.

## Gates

Native installer #320 and coordinator #121 remain separate. After revision, re-run:
- the focused red/green with `test_monitor_delivery.py`
- the locked local suite
- signed hosted validation for the new head
- this independent source review
- verified delivery
- native Close

The current hosted pass (run 43741359310) covers head `519e470c` only.
