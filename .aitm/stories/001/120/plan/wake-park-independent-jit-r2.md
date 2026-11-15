[11:00:52]
JIT_120: PASS

The revision resolves all seven R1 hold conditions in packet text. It introduces no new scope, ownership crossing or budget breach. Residual notes below are non-blocking and are implementation-time checks.

## R1 holds against the revision

| # | R1 hold | Revision | Status |
|---|---|---|---|
| 1 | Issuer contract | `WakeResolver.resolve(request, *, lease)` returns a closed `WakeResolution` with four variants: resolved, unknown-locator, wrong-source-type, stop-without-verified-current-turn. The lease is `Registry.lease` → `ledger._PinnedPath`, which matches the excerpt. A module-private issuer mints `WakeHint`; no public frontier constructor exists. `notify` refuses a hint without the issuer capability. `test_wire_cannot_notify_without_approved_resolution` is named. | Resolved |
| 2 | Frontier vs cursor | The frontier is now a scheduler-local integer generation. It increments only on a fresh service-keyed fact and is never a native cursor, provider ordinal or offset. The wire supplies none. Persistence is limited to sealed keyed state, disposition, the fact and the generation. The privacy test scans every durable wake file for the raw path, session string, turn ID and cursor. | Resolved |
| 3 | Lease and durability | The TTL is injectable and positive, defaulting to 5.0 monotonic seconds. `scopes._publish` completes before a hint becomes due. A refused publish keeps the committed state and creates no in-memory-only due work. A link left by a dir-fsync failure needs a pinned readback and fsync before restart treats it as durable. | Resolved |
| 4 | Frame canonicality | Accepted bytes must equal `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True) + LF`. Limits: ≤2,048 bytes and 30 ms. `v` must be an `int`, with `bool` refused. NaN/Infinity, BOM and duplicate keys are rejected; byte-equality subsumes duplicate-key detection. The locator must be nonempty, contain no NUL and be ≤1,024 UTF-8 bytes while staying inside the frame. | Resolved |
| 5 | Linux non-follow chmod | The measured mechanism is `os.chmod(name, 0o600, dir_fd=root.fd, follow_symlinks=False)`, observed at mode `0600` on both hosts. The revision refuses when that call is unavailable. This is stricter than R1's permitted fallback, so it is acceptable. `EAGAIN`/`EINPROGRESS` and a successful connect count as live, and neither authorizes removal. | Resolved |
| 6 | Measurable fairness | With G eligible groups, each is served within G consecutive `take_due(now, 1)` calls. The next group is retained across calls. A capacity-held group is deferred out of the due set and cannot consume another group's turn. | Resolved |
| 7 | Estimate and cap | The split is 1.45 + 1.25 + 0.8 = 3.5 h. Ingress has 0.5 h of margin to its 1.75 h trigger, and the total has 0.5 h to the 4.0 h cap. This retains Refine's approved bound; R1's 3.5 h hard trigger was stricter than what Refine approved. The measured ctypes and chmod controls remove the main ingress unknowns. | Resolved |

R1's non-blocking items are all answered:
- The launcher lives in `sources/hooks.py`.
- No blob exists at either commit, so the file is newly owned here.
- Park settles every known turn of the session.
- A later append bypasses the prior quiet/backoff deadline.

## Verified

- **Exact four paths:**
  - `monitor_scheduler.py`
  - `monitor_control.py`, where park registers through `configure_monitor_commands` at `:587`
  - `sources/hooks.py`
  - `test_monitor_scheduler.py`
- **Run green but unedited:** `cli.py` already delegates to that parser, and `test_monitor_delivery.py` runs green without edits.
- **Named tests:** the five owned tests, plus the wire-resolution test and the full coverage list. The coverage list includes:
  - real same-UID socket intake and UID mismatch refusal
  - stable root inode and unsafe path/symlink refusal
  - oversize and noncanonical frame refusal
  - unknown locator
  - the privacy scan
  - work/park role
  - failed and expired retention
  - sender behavior against an absent, saturated or refusing endpoint
- **Ownership:**
  - #121 (Rank 250, open) keeps the coordinator, real resolver binding, native reads and cursor/resume.
  - #320 (open) keeps descriptors, adapter invocation, activation and the Grok marker producer.
  - #115 and #119 are closed.
- **Gates preserved:**
  - focused red/green with `test_monitor_delivery.py`
  - the locked local suite
  - signed hosted validation
  - independent source review
  - verified delivery
  - native Close
  - the stop-and-return-to-Refine trigger at ingress >1.75 h or total >4.0 h

## Non-blocking implementation notes

1. **Lone surrogates.** An escaped lone surrogate (`"\ud800"`) passes the canonical re-dump. Make the locator's strict UTF-8 encode fail closed rather than raise.
2. **"Frontier" naming.** Use "generation" in `WorkItem` and the older-frontier no-op. This avoids confusion with `Registry._frontiers` and `CaptureFrontier`.
3. **Crash between bind and chmod.** A crash there leaves a non-0600 socket that always refuses. Either document manual recovery or add a refusal test that names the operator action.
4. **Symbol check before the first red test.** Confirm `SourceRef`, `MonitorProvider` and the service-keying primitive at `e9b92172`. The packet's registry/scope blob parity makes drift unlikely.
