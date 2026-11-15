[15:28:25]
REFINE_331: HOLD

The story's prerequisites, ownership and authority model hold. One wire-scope sentence contradicts accepted M11e condition 2, and two authority derivations are unstated. All three can be fixed in the story text without adding files or prerequisites.

## Verified

- **#329 delivery.** #329 is closed and Done. PR #332 is MERGED into trunk as `30e1a13d`. The literal base was `84b936d1`, the delivered tree is `f69375a6`, and ordered parents and zero diff were verified. #331's only blocker is cleared. The `in: 329 open` entry in the issue snapshot is a creation-time artifact.
- **Rank and estimate.** The board holds Rank 249.5 (condition 5), and #330 at 249 and #121 stay ordered. The 2.75 h estimate is still provisional and needs a separate future JIT. No JIT is implied here.
- **Path disjointness.** #330's paths are `monitor_journal.py`, `monitor_writer.py` and `test_monitor_grok_delivery.py`, and it explicitly excludes `monitor_registry.py`, `monitor_scope.py` and the coordinator. #331's paths are `monitor_registry.py`, `monitor_scope.py` and `test_monitor_grok_enrollment.py`. The two sets are disjoint (condition 4 on paths).
- **Legacy codec.** `_decode_registry` tries strict `RegistryView` first and falls back to `_RegistryWithGrok`. `_RegistryWithGrok` rejects empty `grok_records`. `_grok_view` emits plain `RegistryView` when no records exist. A new closed alternative in `grok_records` therefore leaves empty-registry bytes literal, and an older binary fails closed on it (condition 1 mechanism).
- **Live authority.** `_require_live_source`, `_check_capture_root` and the profile-generation filter on active epochs already exist. A replaced generation cannot match an existing epoch. The story bars watch events, timing and paths as authority (native set).
- **Pending disables.** The story reads queued disables at admission inside the same guarded transaction (condition 3). An in-registry `_GrokPending` for the edge already blocks.
- **Explicit exclusions.** No provider reader, `types.py`, journal, writer, coordinator or #330 edit, and no rollout, production or Epic #2 work.

## Required amendments

**1. Gap retention conflicts with the "only when needed" wire rule (condition 2).**
- `_GrokEpoch(identity, generation, cut)` has no field that distinguishes an enable-time cut from an enrollment-time cut.
- For an enable-time epoch, `[0, cut)` is intentional pre-grant exclusion. For an enrollment epoch, `[0, cut)` is an unobserved pre-witness gap.
- The story allows a new element only when an empty registry cannot apply a grant. For a previously enabled source, nothing durable retains the gap across restart.
- **Required:** one same-file closed grant alternative that exists whenever an edge has an empty-root grant or at least one enrollment. It holds:
  - the applied command ID and digest, project, source, pinned installation and live generation;
  - each enrolled identity with its witness cut.
- Enrolled streams remain ordinary `_GrokEpoch` rows at the grant's existing edge generation, not `1+max`. This keeps #330's epoch selection unchanged.
- Bytes stay identical whenever no grant or enrollment exists.
- The current known owner is the grant's project, used for post-cut spans only. The gap stays unattributed and is never retroactively claimed.

**2. Grant source for a previously enabled #329 state is undefined.**
- Applied #329 state keeps the command ID only in `receipts`. `_GrokPending` (command, digest, change) is removed on apply.
- **Required:** the grant is derived only from a receipt whose exact command ID and digest resolve, through the existing ControlInbox publication record, to this edge's enabled `CaptureChange`, plus a live permission and active epochs at the current profile generation. Otherwise enrollment holds.
- If ControlInbox exposes no locked read of the applied publication or the queued disables without editing `monitor_control.py`, that is a scope stop that needs independent review, not a silent fourth file.

**3. The #329 empty-enable wait is changed but not named.**
- `if change.enabled and not offers: raise BoundaryUnavailable(...)` must become a grant apply for a qualified empty root.
- The story must state this explicitly.
- If any #329 test pins that wait, the change needs an independently reviewed test exception outside the three-file scope.

**4. Invariants and disable retirement.**
- `_RegistryWithGrok.__post_init__` must reject:
  - more than one live grant per edge;
  - a grant whose command ID is not in `receipts`;
  - a grant command ID that collides with a pending command;
  - an enrolled identity without its epoch.
- An applied disable ends the grant atomically with the epoch ends.

**5. Epic citations (condition 6).**
- Cite the exact Epic sections for M06, M11 and M18/M19 instead of the spliced excerpt.

## Smallest required scope

Same three files, with the story text amended per items 1–5. No new prerequisite is established.

## Carried to JIT

- Read back #330's Refine map and freeze the `monitor_scope.py` admission handle API that #330 consumes.
- Pin the runtime API and the gap and coverage handoff to #121.
- Confirm whether `_grok_span_disposition` can surface the grant-recorded gap without a `types.py` change.
- Re-confirm the estimate. 2.75 h holds only if item 2 needs no `monitor_control.py` edit.
