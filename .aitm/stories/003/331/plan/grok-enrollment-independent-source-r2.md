[16:51:48]
SOURCE_331: PASS

Reviewed candidate `1f8534d9` (tree `622f1ab6`) against base `8be6d460`, using the r1→r2 recovery diff and the full base diff. `monitor_scope.py` is unchanged since r1 (`a7d7b4ea`). Only `monitor_registry.py` (`21143cba → 58143602`) and the test file (`faedaf89 → 77b05fc8`) moved. The full diff still touches only the three permitted paths.

## Hold 1 – Pre-witness gap on reissue enrollment: resolved

**Fix.** In `_apply_grok_capture`'s enabled branch, when `current is not None and additions`, each addition is now appended to `current.witnesses` as `_GrokFrozenCut(row.identity, row.start)`. This uses `replace(row, witnesses=...)`, which:
- keeps `command_id`, `digest` and `generation`;
- keeps `generation = current.generation`, so there is no bump and no new grant.

**Consistency with load validation.** The witness cut is the same `_GrokCut` object as `_GrokEpoch.start` at the grant's generation. That satisfies `_check_grok_grants`, which requires exactly one matching epoch with `start == witness.cut`.

**Quiet case.** The reissue commits the epoch and its witness at cut N, giving the gap row `[0, N)`. A repeated `enroll_grok` takes the `prior` path:
- the mint returns the same cut, so `prior == witness`;
- nothing is saved;
- it returns `None`, a readback only.

`read_source` shows no observations, so nothing before the witness is admitted.

**In-flight case.** The arm stays in `_GrokPending`, and gaps are `()` while it is held. It resolves through the same branch after the verified terminal. The gap is `[0, len(turn))`, which includes the excluded in-flight turn, as J8 requires.

**Pre-grant epochs.** Untracked active #329 epochs are still excluded by `active_identities`, so they get no witness, as J5 intends. Edges without a persisted grant still take #329's literal `1+max` path.

**RED by construction.** Under r1, `(gap,) = _gaps_after_reopen(f)` fails on an empty tuple, in both parametrizations.

## Hold 2 – Retired grants after an approval change: resolved

**Fix.** The approval lookup and the root and installation equality now run only for `grant.active`. A missing approval for an active grant still raises `LedgerError("Grok grant installation changed")`. The test confirms this by saving `sources=()` over an active grant.

**Retired grants still require:**
- the original receipt to be present and APPLIED, with the exact enable digest;
- witness/epoch consistency (exactly one epoch per frozen witness at the grant generation, and no epoch for an arm).

The post-receipt disable scan and the permission membership check stay active-only, as J3 requires.

**Reuse.** A retired grant cannot be reused:
- `_grok_enrollment_grant` and `current` both select `row.active`;
- a regrant always mints a new `_GrokGrant` from the new command.

**Same-ID root replacement.** This remains refused: `approve_source(... root=replacement)` with the old ID raises `ConflictError("identity changed")`.

**Replacement path.**
- The replacement uses a new source ID (`UUID(int=33121)`) and an explicitly enqueued, applied `CaptureChange` (`33122`), with no synthesized command.
- The result is `{(old, retired), (new, active)}`.
- The old gap row survives reload both with the retired source omitted from the approval set and after the new grant.

**RED by construction.** Under r1, `_source(view, old_id)` raises on reload after the snapshot that omits the source.

## Existing conditions rechecked

- **Physical JIT pins.** The pre-images of the writable files are still `766ddf80` and `bb2a781b`. The #330 merge to `8be6d460` touched neither, and no read-only path is modified.
- **Old wire.** The populated #329 bytes round-trip through `_OldRegistryWithGrok`. A grant view fails closed in the old reader. There is no codec edit and no extended-empty encoding.
- **Reissue of a tracked arm.** It keeps the original grant ID and a single generation, and repeated readback is identity-only. An incarnation change on a tracked stream holds without a receipt.
- **Disable.** It retires only the edge's active grant and ends epochs atomically. An unresolved arm becomes an unknown gap row that persists across reload. A later enrollment is refused after the disable.
- **Gates and evidence.**
  - Signed control blobs (gate, lock, observer, policy, verifier, workflow) are identical to the prior verified gate.
  - The hosted run `43770857943` passed on head `1f8534d9`, with tree `622f1ab6` matching the reviewed tree.
  - Local and hosted product coverage are identical (14214/15632). Local tests: 1487 passed, focused tests: 114 passed.
  - The fixture IDs are fixed UUID ints, and the tests make no live provider turns.

## Non-blocking notes

- **Indirect assertion.** The new parametrized test does not directly assert `grant.command_id == enable.command_id` or the generation on the untracked-reissue path. Both follow structurally from `replace(...)` and are enforced at load by `_check_grok_grants`. The tracked-arm test pins them explicitly.
- **Simulated snapshot.** The restored approval set is simulated through `_save`, not through a revoke API. This is acceptable as snapshot evidence.
- **Unloadable registry on approval loss.** When an active grant loses its source approval, the registry is made unloadable with `LedgerError`; the grant is not retired. This matches "source approval loss still refuses an active grant".
- **RED log not reviewed.** The contents of `source-recovery-red.log` were not supplied. Only its hash is bound. The RED status above is inferred from the r1 code.
