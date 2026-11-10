# #117 independent source review, attempt 1

Reviewer **Claude Opus 5.5, medium**. Verdict returned November 10, 2026 at 21:01 UTC. Off-platform packet review. Exact head `da288f5381e2c263756c577f3f820927d169bff4`, tree `5d65dbb000c15f14c41740e7f4517768de79d4d7`, base `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`. Signed hosted run 42899470371 attempt 1.

# HOLD: #117 M07a at `da288f5`

**Verdict: HOLD.** There is one source-backed blocker. Everything else I was asked to check passes against this packet. I reviewed only the packet you provided and used no tools. I treated the signed CI evidence as given and did not replay it myself.

## Blocker: a resolved hold lets the same command take effect later

**Where it is:** `monitor_scope.py`, `ScopeState._apply`, in the hold branch:

```python
if hold is not None:
    ...
    if hold.state is not HoldState.RESOLVED:
        return HandoffDisposition(HandoffStatus.HELD, hold.affected)
# RESOLVED falls through to _timeline(...) and _save(... events + event)
```

`dispose(..., release_previous=True)` marks a hold `RESOLVED` only when it has proven that the prior scope continues. That means the held proposal was rejected. But `_apply` treats `RESOLVED` as permission to apply the same command. `hold()` and `dispose()` also remove the authorization, yet `authorize()` doesn't check holds or events, so the command can simply be authorized again.

**Scenario, built from the delivered `test_verified_disposition_only_releases_its_covered_hold` fixture on an append-only stream:**

1. Mark A‑116 is applied at `marked`, which sets generation 1 on the retained checkout A.
2. Handoff H (A→B‑117, before‑generation 1, retained A) has its receipt and target at `held_at`. `state.hold(...)` turns it into a `HELD` proof hold. H is valid against the timeline.
3. Disposition D's receipt target is already within the hold's span. `dispose(D)` passes the continuity check and the hold becomes `RESOLVED`. Routing at `held_at` returns `original` (A‑116).
4. A retry or restart runs `authorize(H, operator(A))`, then `read_source`, then `verify_boundary`. The first receipt target and digest are unchanged, so the position and digest checks pass. `apply_handoff(H, proof)` then reaches `_timeline`, which returns **APPLIED at generation 2**, and the event is saved.
5. Routing at `held_at` now returns B‑117. The span that was released to A is re‑attributed to B with no new evidence, and `receipt(H)` changes from returning the hold to returning `applied`.

**What this breaks:**
- "Exact retries have one effect."
- "Release to prior scope only when continuity and absence of another claim prove it." The release check ignores the held claim itself, and that claim can still be applied afterwards.
- The hold is meant to be owned and terminal. Right now a disposition can be reversed by the very proposal it rejected.

**Required fix:** In `_apply`, treat any existing hold for that command ID as terminal. Return `HELD` for `HELD` or `GAP` holds and `REJECTED` (or the recorded hold) for `RESOLVED` ones, and never append an event. Add a regression where H and D both stay in an append‑only stream, H is retried after resolution, and the test asserts:
- no new event is saved;
- routing at `held_at` still returns `original`;
- `receipt(H)` returns the same result before and after the retry.

## Areas that pass

- **Same‑read receipt and first target:** The target has to come from the issuing writer's own batch and is matched by object identity. The batch is rechecked against the registry and the pinned native prefix at both verify and apply. The read always starts from the beginning of the stream (`cursor=None`), up to the physical capture limit. The target must be the earliest unique occurrence of that receipt. For Codex and Claude, the receipt is tied to the command ID by the `scope-receipt` pseudonym.
- **Source and anchor custody:** The reader uses the approved candidate check, admitted unbounded readers and the prefix-continuity check. Anchor matching is unique across pinned anchors and rechecked at apply. A cloned proof, a substituted stream, or a changed inode, prefix or anchor all fail.
- **Capture span and unanchored rescan:** If the scope changes inside an observation's native span, the result is held. Only applied, eligible, unanchored Marks can enroll frames during a rescan. If the prefix changes during the rescan, every boundary and observation in the batch is dropped.
- **Owner/generation and A→B→C:** Generation zero starts at the anchor. A handoff needs the current project, before‑generation and retained checkout to match, and a new unrelated checkout is held. For Develop, the binding is checked against the current owner generation and the destination worktree, and the origin checkout can't stand in for it.
- **Conflicts and late suffix:** Competing proposals are grouped by stream and target ordinal and checked against the generation in force before that target, so receipt IDs and boundary refs can't hide a shared target. The whole timeline is recomputed on every read, so a late earlier handoff holds the later one that went stale. The affected span and observation keys are merged into the returned outcome.
- **UTC holds:** Holds use an injected, timezone-aware clock, and the first-seen time is clamped so it never moves backwards. Expiry is fixed and survives a restart. Once 256 holds are unresolved, new ones become a `GAP` without displacing existing holds. The snapshot is capped at 1 MiB and fails closed. Expired and `GAP` holds release no usage.
- **No activation and no invented Grok capture:** Grok positions are the marked completion for a Mark and the next turn for a Handoff. Grok is never eligible, so its routes stay held, and no capture epoch is created. The only file written is `scope-v1.json`, through the existing pinned publisher under the lease. The registry and project ledgers are asserted unchanged, there's no CLI or launcher wiring, and raw identifiers stay out of the snapshot.
- **CI:** Head, tree and base match the packet, all six jobs are present and the status is `pass`. Product coverage is 91.03% (9086/9981) and helper coverage is 94.76% (778/821).

## Advisory (not blocking)

1. The replay reports `baseline_tests: 713`, but the pickup recorded 714. The total of 747 equals 714 plus the 33 new tests, so the 713 needs reconciling before closure. The replay also doesn't show the 182 helper tests.
2. A Develop **Handoff** skips the same-session check against the owner marker that a Develop **Mark** gets in `_same_legacy_stream`. This matches the plan's literal wording, but someone should confirm it's intended for the M07b/M11 work.
3. After A→B on a retained A checkout, an ordinary Mark for B conflicts because the anchor is still A. A B→B handoff is refused, so there's no way to switch stories within B until the checkout changes. This fails closed, so nothing is misattributed.
4. A late reprojection or a later conflict doesn't update the `reported` outcome stored for an event that was already applied, so `receipt()` keeps returning the original result. Downstream journal work (M09/M13) needs to rely on the affected spans that are returned.
5. The `_read_state` error messages changed from "registry" to "state". Confirm those strings aren't part of the M06 control or terminal bytes that have to stay compatible.
6. Conflicts recorded in the event timeline hold routing indefinitely until scope is proven again. They never expire into a reported coverage gap the way proof holds do.
