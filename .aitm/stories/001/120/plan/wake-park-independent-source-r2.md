[12:10:28]
SOURCE_120: PASS

The candidate fixes all four held items, and each fix is proven red→green. Ingress (`monitor_control.py`) and the sender (`sources/hooks.py`) did not change in this correction, so they keep their earlier acceptance. The scheduler changed in only two places: the stale-stop guard and `take_due`.

## Held items

| # | Hold | Correction | Status |
|---|---|---|---|
| 1 | Verified stop for a new turn was dropped | **Fix:** the guard in `Scheduler._admit` now requires `previous is not None` before comparing generations. A turn with no record now gets `self._generation + 1`, enters Settling and becomes due.<br>**Test:** `test_verified_stop_only_new_turn_gets_exactly_one_catchup` shows turn 2 in Settling with a higher generation. It gets one catch-up, then parks. A repeated stop is a no-op because the fact is the same and the turn is Parked. After restart, nothing is due and both turns are Parked.<br>**Stale-stop test:** `test_stale_stop_cannot_park_newer_turn` still refuses. Turn 1 has a record at generation 1, and turn 2 is at generation 2. | Resolved |
| 2 | Rotation was by slot, not by stream | **Fix:** `take_due` now groups due slots as group → stream → deque, and keeps a per-group `_last_stream_by_group` cursor. Each round takes one slot from the next stream after the last one served.<br>**Test:** `test_due_turns_rotate_by_stream_inside_one_project` puts two due turns on one stream, ordered ahead of a second stream by due time. The first two takes cover both streams, and the third returns to the first. Before the fix, ordering by `(due, name)` served the first stream twice, which the red run confirms.<br>**Unchanged:** group round-robin is the same, and `test_full_project_does_not_starve_another_due_project` stays green. | Resolved |
| 3 | No real #119 hold-and-ack test | `test_delivery_hold_retries_its_exact_cursor_while_other_project_can_ack` uses the isolated `independent` fixture with `cap=1`, and leaves `test_monitor_delivery.py` unedited. The test shows each step below. | Resolved |
| 4 | No stable endpoint identity test | `test_replaced_endpoint_is_refused_and_preserved` runs twice, once with `wake.sock` rebound and once with the root replaced. The test shows each step below. | Resolved |

**What the #119 test shows:**
1. Project A's wake reserves `held`, and the cursor stays at `prior`.
2. `finish(caught_up=False)` backs that wake off.
3. Project B is woken, reserved `pending`, committed and acked. The ack is idempotent (exact boundary) and produces one revision.
4. A's cursor stays at `prior`, and nothing becomes due early.
5. After A's original delivery is acked and 0.25 s passes, the retry has the same stream and the same generation.
6. The held item settles to `pending`, the cursor advances, and the retry finishes.

**What the endpoint test shows:**
1. `serve_once` returns `False` with no resolver call. The socket case fails `samestat`, and the root case fails `directory.check()`.
2. `_retire` leaves the replacement inode alone. The test checks this with `samestat` after the listener exits.
3. The socket case leaves no work due.
4. The root case makes the scheduler refuse with `Private ledger path`.

## Evidence consistency

- **Red run:** 2 failed and 3 passed, with 19 deselected out of 24 tests. The two failures are the behavior tests. The three passes are the new coverage tests, which check behavior that already existed, so passing on red is expected.
- **Local green runs:** the focused run passed 36, and the locked suite passed 1391.
  - The background-SIGINT launch issue is environmental: the shell ignored SIGINT.
  - The foreground run and the isolated base and candidate node runs justify accepting the results.
- **Signed hosted validation:** run 43743853023 covers:
  - head `b1713c7b`, base `3675e989` and tree `baa2bfb6`
  - reviewed tree equal to tested tree
  - control blobs equal to the prior verified gate
  - product coverage of 12954/14122, the same as the local run
- **Refresh:** `9de9dbbe→3675e989` touches only `README.md` and `docs/blocked-by.md`, and the patch is byte-identical before and after.
- **Scope:** still exactly 4 files, and `cli.py` is unedited.
- **Prior `SourceRef` note is closed:** `types.py` rejects a value where `type(value) is not str` with `ValueError`. That means `"session":123` is refused inside `serve_once`.

## Non-blocking

- **Concurrent leases on one stream:** two slots of the same stream can be leased at once, which the rotation test's third take relies on. #121 must either serialize per-stream scans or keep them idempotent.
- **Carried forward from the last review:**
  - readback-adopt after a dir-fsync failure
  - documenting Darwin `ECONNREFUSED`
  - no tests yet for `hooks.main()`, `WRONG_SOURCE_TYPE` or `STOP_WITHOUT_CURRENT_TURN`

## Gates

These gates are now met:
- focused red/green with `test_monitor_delivery.py`
- the locked local suite
- signed hosted validation for `b1713c7b`
- this independent source review

Still pending: verified delivery, then native Close. Native installer #320 and coordinator #121 remain separate.
