[17:10:13]
# JIT_335: PASS

This was decided on the supplied packet at literal trunk `4ba4354f603ad861c897111dcaaf2342fc68da86`, without tools. No accepted obligation needs another owner, a fourth file or a gate edit. Four symbol-level facts are not in the packet. They are listed at the end as pre-RED gates, using the return-to-Refine triggers Refine already set.

## Entry and binding verification

| Check | Result |
|---|---|
| **Entry shape** | The raw `{hookEventName, sessionId, promptId, workspaceRoot}` row, plus `GROK_HOOK_EVENT` and `GROK_SESSION_ID`, is the shape the #329 qualified pilot observed on Grok 1.0.77 (`_hook`). `hooks.py:main()` only accepts a `_parse_frame` `HookEvent`, so a separate module is required. Two observed-shape facts matter: `start_hook` records the hook only when `runs` has length 1 and succeeded, and a second configured hook yields `runs` of length 2, so there is no boundary. |
| **Cold binding** (no Grok checkpoint) | The `GrokAdapter` parses the file from offset 0. `start_hook` fixes `prompt` and `hook`. On the `end_turn` completion, `verified_boundary` requires `hook.time <= update.time`, then calls `verify_receipt(session, prompt, event_id)`. The lookup ignores `event_id` and returns the `scope-receipt` ref only if a committed one-use receipt exists for `(session, prompt)` and still re-verifies. `boundary_ref` binds the observed `event_id`. The core then requires receipt equality and the first unique ordinal. |
| **Resumed binding** | `_recheck_grok_prefix` re-verifies the origin and the already-observed prefix against the persisted `GrokCheckpoint` (strict). Any in-place change to observed rows, including a substituted `event_id`, raises `_GrokCaptureHeld`. |
| **Root and source key** | `_authority` requires `key_id == view.source_key_id`. `open_grant` requires `grant.account == _directory(root)`, `authority_key == view.source_key_id`, and the project state, ledger key and adoption. `build_grant` takes `authority_key` from `writer.source_evidence().key_id`. So the hook-side key from `_authority` and the core-side key from `registry.source_evidence()` are the same key. |
| **Owner lease** | Staging runs under `writer.lease`. It does a readback of the published bytes and calls `lease.check()` before returning. The hook holds no lease. Its continuity comes from three things: the root pin, the keyed attempt seal, and the `open_grant` identity checks. The lookup runs inside the lease-holding monitor, where the core calls `self.registry.lease`. |
| **Registration and approval** | Under the same root pin, the hook re-reads `registry.view()` for the project through `open_grant._project` and for the staged approved source. A source that is missing or no longer approved is refused. |
| **Ancestry** | This is real physical ancestry. #329 qualified that the native hook runs under the live Grok child (`_under_process`). |

## Observed-prefix replay vs. cold replacement (settles R2)

- **Observed-prefix replay.** These are bytes the reader already checkpointed.
  - An exact replay gives the same `boundary_ref` and the same receipt, and the command stays one-shot.
  - A substitution fails `_recheck_grok_prefix`.
  - These are both actual obligations, and both are owned here through the real `ScopeState`.
- **Hypothetical unauthenticated cold replacement.** This is a row edit made before any reader has observed it. No component authenticates it, and nothing claims to. The Grok hook input has no event ID, so no independent event-ID witness exists to compare against.
  - Its effect is limited to the `boundary_ref` label. The prompt, session, receipt, ordinal and owner are unchanged.
  - Per-row native integrity before the first read is #329's custody boundary.
- **R2 settlement:** R2 does **not** require a cold-reader event-ID comparison. Tests must not claim cold refusal.

## The eight conditions

1. **Receipt domain.** `scope_admission.py` gets one helper, `scope_receipt_ref(evidence, command_id) = evidence.pseudonymize("scope-receipt", str(command_id))`. Both the new `MarkRequest→Mark` conversion and the lookup call it.
   - The core's non-Grok branch proves this is the canonical value.
   - `command.receipt_ref`, `command.command_id` and `_scope(command)` on `Mark` confirm the carrier fields exist.
   - The conversion takes no receipt input, so an arbitrary `SourceRef` cannot enter.
   - RED: an `isolated-grok-prompt-v1` ref for the same command fails `boundary.receipt_ref == command.receipt_ref`.
   - The exemption line stays untouched. **Residual:** for Grok, the domain is enforced only by this construction, so #121 must build Marks only through this conversion.
2. **Event ID is not durable.** The lookup is pure on `(session, prompt)` plus the persisted receipt. It re-verifies with `_read_private(inbox_dir, _filename(id))`, `open_grant`, `seal_request(current, request) == staged envelope` and `not revoked`.
   - It does **not** require revision equality or a fresh witness. That way, renewal at the same generation is invariant, while a rotated or revoked grant fails the seal or open check.
   - RED (real adapter and `verify_boundary`):
     - a second hook in the same turn gets `OVERLAP_UNVERIFIED`;
     - two same-receipt turns in one batch, where the later target is refused;
     - an in-place `event_id` substitution after a checkpoint is held;
     - a lock-free, write-free test showing the root and receipt directory listings, inodes and mtimes are unchanged.
3. **Ancestry** lives in `grok_scope_hook.py`.
   - Walk from `os.getppid()`. At each hop, take two reads of `_BSDProcessInfo` through `_libproc()` and check:
     - same start time and same `parent_pid`;
     - `uid == geteuid`;
     - not a zombie;
     - the parent started no later than the child.
   - Stop when `(pid, started)` matches the staged values and `_process_identity(pid).executable` matches the staged stat identity (dev, ino, size, `mtime_ns`). The walk does not hash a large image on each prompt.
   - Fail at PID ≤ 1, at depth 8, or on any `OSError`.
4. **Namespace.** Use `registry.root/grok-scope-receipts-v1/`, a sibling of `INBOX_NAME`, so `iter_verified` never enumerates it.
   - It is created 0700 by `stage_grok_attempt` under `writer.lease`.
   - File names are pseudonyms keyed by the source key.
   - The hook writes the receipt only inside `ControlInbox.publication()`, which is a lazy import to avoid an import cycle with `monitor_control`.
5. **Checkout.** At staging, store `pseudonymize("grok-scope-checkout", dev:ino)` of the pinned checkout. The hook stats `workspaceRoot`, recomputes the value and compares.
   - The hook gets evidence through `_authority(registry, root)`, with no lease. Its type matches `source_evidence()` because `build_grant` uses `.key` and `.key_id` identically.
   - The session, prompt, process and image are stored only as keyed tags. No raw path, PID, prompt text or native ID is written to disk.
6. **The selector is not authority.** The selector, nonce and `GROK_*` variables are all inherited by model tools, which also descend from Grok and so pass ancestry.
   - The bound is: first bind wins, the adapter requires a native `hook_execution`, and prompt UUIDs are unpredictable.
   - A forged prompt before the real bind is possible only in a replacement-attempt window. It yields denial, not misbinding: the real prompt's lookup returns `None`.
   - RED covers both orderings, replay after bind, and missing or mismatched env markers.
   - The hook prints nothing to stdout, because UserPromptSubmit stdout may reach the model context, and always exits 0.
7. **Fixtures.** Import the #329 helpers as they are from `test_monitor_grok_capture`. This works with pytest's default prepend mode, since there is no `[tool.pytest]` section. Mark imported fixtures `# noqa: F401, F811` in the new test file only.
8. **Platform and coverage.**
   - The walk takes an injectable hop reader.
   - Cross-platform tests monkeypatch `install._libproc` with a fake whose `proc_pidinfo` fills the ctypes struct. This covers every branch on non-Darwin hosts without `pragma: no cover`.
   - Real libproc custody tests are marked macOS-only.

## Ownership and offline execution

| File | Contents |
|---|---|
| `grok_scope_hook.py` | Raw-row and env parsing, the ancestry walk, `main()` |
| `scope_admission.py` | Attempt and receipt records, stage, bind, read-only verifier factory, conversion |
| `test_grok_scope_receipts.py` | Tests |

Offline tests can run the one-use component for real:

- a real `Registry` writer, #182 grant, `enqueue_scope` and witness;
- a stand-in native parent (`sys.executable`), staged as the launch context, which spawns `python -m aitm_usage.sources.grok_scope_hook`.

The owner is the existing lease holder and the signer is the existing source key. No owner or signer is invented.

## Pre-RED gates (return to Refine if any is false)

- Every field `Mark` requires can be derived from `MarkRequest`, the envelope generation and the evidence.
- An existing atomic private-write helper in `scopes` can write the new directory without an edit.
- The stat or `_directory` identity works for a non-0700 checkout without an edit.
- `Ledger.open` and `_committed_grant(confirm=True)` neither lock nor write. The condition 2 no-write test proves this.

The checkpoint at about 1.9 h is unchanged: valid, conflicting and wrong-owner attempts, shown end to end through the real `GrokAdapter` and `ScopeState`.
