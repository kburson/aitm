# AITM usage collector

The per-user macOS LaunchAgent captures supported local Codex Desktop and Claude Code records in a private SQLite ledger. It polls every 15 seconds while the Mac is awake. The fixed-sequence export preserves normalized usage, scoped pseudonyms, pricing basis and coverage. Keep the same production project UUID, state directory and pseudonym key through the life of AITM.

## U11 qualification runbook

Use the approved #83-only controlled workload on the project Mac. The planning and review tasks exercise actual requests against disposable draft identities within #83. Use a dedicated #83 qualification worktree for the development-owner action and a marked housekeeping action. Keep #2 untouched. Use short synthetic task inputs and privately retain the selected native source and collector evidence. Stop at the first unmet mandatory gate and retain the specific gap for review.

### Prepare the approved artifacts

1. Record the reviewed trunk commit and clean tree. Build the primary pure wheel from that source using the locked build backend and canonical Python 3.13+ interpreter. CPython 3.13.9 was used in verification. In a disposable build copy change only the project version in `pyproject.toml` and update the local build lock as needed for the sibling rehearsal wheel. The package source and resources inside both wheels must match byte for byte. Record both lower-case wheel SHA-256 values from the built artifacts. Obtain source and wheel approval independently of the qualification receipt.
2. Install an operator CLI from the approved primary wheel. A disposable tools venv is sufficient. For example, use `uv venv --python "$PY" "$TOOLS"` followed by `uv pip install --offline --no-deps --python "$TOOLS/bin/python" "$WHEEL"`. `PY` is the canonical absolute base binary, `WHEEL` the absolute primary wheel path and `TOOLS` the private tools venv. Make its console available as the bare command `aitm-usage` on the approved clients' PATH. Check `command -v aitm-usage` and the console version in each client before using the marker route. Resolve a PATH conflict before the run. Use the absolute verified console for other operator commands.
3. Confirm the logged-in user's `gui/$(id -u)` launchd domain. Allocate one stable production project UUID and absolute state root outside Git. Use distinct UUIDs and state roots for recovery and controlled arrival-order exercises. Create a private evidence directory outside the project store and Git with mode 0700 and use `umask 077` for evidence files. Preserve the independent per-project writer guard.
4. Each registration input is a private JSON object with `project_id`, `source_roots`, `checkout_anchors`, and a UTC ISO-8601 `cutoff` chosen before the authorized workload. Supply physically resolved, approved directories. Retain the actual provider-reported checkout and the approved planning worktree privately. A shell tool's workdir alone establishes only where that shell ran. Use the provider-reported checkout for the applicable anchor and conduct the planning operations in the shared planning checkout. Use only authorized source roots. The optional registration `retention_limits` contains `{"provider":"codex","seconds":86400}`-shaped entries using the actual approved retention limit, if known. An omitted limit stays Unknown, with an independent 15-minute freshness bound for qualification.

Complete the separate recovery rehearsal below, including the upgrade and explicit version rollback, before applying the production install. Use the following commands for the production root after that prerequisite.

```sh
aitm-usage --project "$ROOT" register --config "$CONFIG" --json
aitm-usage --project "$ROOT" service install --wheel "$WHEEL" --interpreter "$PY" --wheel-sha256 "$WHEEL_SHA256" --dry-run --json
aitm-usage --project "$ROOT" service install --wheel "$WHEEL" --interpreter "$PY" --wheel-sha256 "$WHEEL_SHA256" --json
aitm-usage --project "$ROOT" status --json
```

Run applied lifecycle commands as the logged-in GUI user. Save each JSON response privately and check the actual exit code. `installed` records an observed launch of the owned, enabled LaunchAgent with `RunAtLoad`, `KeepAlive` and the exact isolated `service run` console. Retain the original install result, not a later `already-active` response, for first startup. An actual bootstrap may wait up to 120 seconds for the matching service heartbeat. The U09 activation receipt includes `producer_mode`, positive `producer_pid`, actual UTC `producer_started`, and a post-start `heartbeat`. It also supplies `project_id`, `label`, `version`, `wheel_sha256`, `interpreter_version` and `poll_interval_seconds`.

Status reports `read_gap` for the ledger snapshot and separately reports `registration_gap` for the accepted configuration and anchors. Require both false. The producer version/interpreter fields describe the polling service. The unprefixed version/interpreter fields describe the status command. Require `producer_mode=service`, the activation PID and matching `collector_version` and `collector_interpreter_version`. Require zero `invalid_inbox` and `relationship_halted=false` when capturing production evidence. `root_gaps`, `missing_sources`, `held_sources` and `deferred_sources` describe the whole scan. Unrelated unbound sources can be held as part of normal project isolation. Qualification checks the selected author and reviewer streams individually for fresh authenticated progress, live readable source continuity, and any hold or relevant integrity gap. `status_sequence` is the settled poll's sequence. `sequence` is the separately read ledger head. A `collect-once` heartbeat represents a one-shot producer and cannot certify launchd. Qualify independently inspects the owned plist, enabled loaded job, verified active wheel and runtime, and actual process start and PID before and after checking status.

### Exercise the actual provider marker routes

Use the pinned observed clients, Codex Desktop `0.167.0-alpha.3.2` and Claude Code `2.1.318`, both format 1. Use an opaque command UUID selected before writing each marker. In an operator process with the approved package, use `aitm_usage.cli.open_project` to open that registered ledger, and `aitm_usage.scopes.session_reference(ledger, provider, raw_session_id)` to derive the authenticated session reference. Read the real Desktop thread from `CODEX_THREAD_ID` in the trusted operator process that prepares the marker. Keep the value out of tool output. For Claude reserve a fresh UUID, launch the normal native client as `claude --session-id "$CLAUDE_SESSION"` from the approved checkout, and verify its actual retained native session ID matches that reservation. Keep the raw IDs and wire commands in private state.

Use `codex_request_boundary_reference` and `codex_receipt_reference` from `aitm_usage.sources.codex` for Codex. Use `claude_request_boundary_reference` and `claude_receipt_reference` from `aitm_usage.sources.claude` for Claude. All four take the ledger, session reference and command UUID. Build the wire input with the following installed Python types.

```python
from datetime import UTC, datetime
from aitm_usage.types import (
    BoundaryKind, DevelopmentBinding, ScopeMarker, encode_binding, encode_marker,
)

# Resolve these operator inputs from the registered project and the chosen action.
marker = ScopeMarker(
    marker_id=command_id, provider=provider, session_ref=session_ref,
    scope_sequence=next_scope_sequence, boundary_kind=BoundaryKind.REQUEST,
    boundary_ref=boundary_reference(ledger, session_ref, command_id),
    published_at=datetime.now(UTC), item=item, phase=phase,
    participant_ref=ledger.pseudonymize("participant", controlled_participant_label),
    project_id=ledger.identity.project_id, role=role,
    receipt_ref=receipt_reference(ledger, session_ref, command_id),
    attempt_ref=attempt_ref, review_ref=review_ref,
)
wire = encode_marker(marker)
# For owner binding only, use the approved worktree's authenticated reference.
if development_owner:
    wire = encode_binding(DevelopmentBinding(marker, anchor_ref, generation))
```

Write the exact wire bytes to a new private absolute file. Use increasing `scope_sequence` within each native session. Select `ItemKey(ItemKind.ISSUE, 83)` for the epic and `ItemKey(ItemKind.DRAFT, draft_uuid)` for each draft. Use `ReviewRole.AUTHOR` for planning and `ReviewRole.REVIEWER` plus a pseudonymous `review_ref` for document review. A development binding uses `WorkPhase.DEVELOPMENT`, a private pseudonymous `attempt_ref`, and the current positive binding generation. Obtain `anchor_ref` from `aitm_usage.sources.scan.checkout_anchor_reference(ledger, absolute_worktree)` after the worktree is an accepted anchor. For an added anchor submit the private `{"command_id":"<uuid>","project_id":"<uuid>","checkout":"<absolute-directory>"}` proposal with `aitm-usage --project "$ROOT" source add-anchor --anchor "$PROPOSAL" --json` and confirm the accepted disposition before using it.

For Codex Desktop send exactly one `functions.exec` call with this JS source. Supply the shell string constructed with Python `shlex.join` from the displayed argument vector and encode it as a JSON string in the wrapper. The only option is `cmd`. Keep the marker receipt inside the same native turn so the next provider request has the proven boundary.

```javascript
const marker = await tools.exec_command({"cmd":"aitm-usage --project '/absolute/private state' scope mark --marker /absolute/marker.json --json"}); text(marker.output);
```

For development use `development bind --binding` in place of `scope mark --marker`, keeping the same argument positions. In Claude use the canonical shell-quoted invocation as one native **Bash** tool call, with the verified reserved ID in this exact position. These examples use a placeholder UUID and canonical shell quoting.

```sh
aitm-usage --project '/absolute/private state' scope mark --marker /absolute/marker.json --session-id 3f32952e-83ea-4427-98f4-121bf30263e0 --json
aitm-usage --project '/absolute/private state' development bind --binding /absolute/binding.json --session-id 3f32952e-83ea-4427-98f4-121bf30263e0 --json
```

The actual native tool result must be the single queued JSON receipt for that command. Claude's native tool result must link to the Bash tool ID and the invoking assistant UUID. The following independent assistant request must follow the native UUID chain and match the intervening `api-request.id` via `requestRef`. The Codex adapter joins the Desktop tool output to the tool call and the first supported request in source order. Use the exact source-proven first request for each scope. Elapsed timestamps corroborate native order.

### Record the live #83 workflow and restart

1. In the shared Desktop planning session hydrate #83 and two disposable draft children. Queue each parent with `aitm-usage --project "$ROOT" item parent --child "$DRAFT" --epic 83 --json` and observe the accepted relationships. Mark planning scope in the order epic batch, child A, child B, then return to #83. Each sample is the first measured request following its distinct native marker. Keep one provider session, participant and accepted checkout anchor for these four.
2. Overlap an actual Claude Code reviewer with that author. Mark document-review scope under #83 or one of the two children, using a distinct participant and review reference. Collect a measured first request and another request while the same review scope is active. Their observed request interval must overlap the author interval from epic batch through return.
3. After return, graduate A with `aitm-usage --project "$ROOT" item alias --draft "$DRAFT_A" --issue "$DISPOSABLE_ISSUE" --json`. Use a controlled issue identity in the collector without creating a fake GitHub issue. Record the commit sequence of that alias effect. Establish the #83 ancestry with accepted `item parent` commands. Compare the last pre-graduation draft direct rollup to the first post-graduation issue direct rollup. At the final fixed view, record epic direct and inclusive counts and each child's direct count.
4. In the approved dedicated qualification worktree, use the native route with the actual provider-reported worktree to bind the authorized owner for a child or other approved descendant of #83. Collect the first measured request in that binding. Where available, observe an unmarked nonowner and then an explicitly marked compatible reviewer to confirm independent attribution. Separately mark a housekeeping action for #83 or an approved descendant and observe its first request. Capture both providers' supported model or effort switches, retry/error and nested activity where evidenced. Preserve provider-specific gaps for unavailable signals. Keep supported API-equivalent pricing separate from billed spend and task quota.
5. After the collector settles, copy the exact private `$ROOT/status.json` to the evidence directory and save the accompanying `status --json` privately. Use the raw snapshot's `report.sequence` as `FIXED`. Retain a fixed export and the original status/launch evidence before stopping. `RATE` is the installed `load_rate_card().version`; both exports use the same installed rate card.

```sh
aitm-usage --project "$ROOT" export --as-of "$FIXED" --rate-card "$RATE" --output "$EXPORT_BEFORE" --json
aitm-usage --project "$ROOT" service stop --json
```

6. While the same project service is confirmed stopped, perform one more measured native request in each of the original author and reviewer streams. Retain their two stable usage keys for catch-up. Reinstall the identical approved wheel to resume the same project and ledger. Wait for the matching service producer and the two catch-up rows. Re-export the original fixed cutoff to a new private directory and compare both files byte for byte. Capture a fresh exact `status.json` snapshot after the project settles, and retain the matching `status --json` to read its authenticated offsets and observation times. Refresh these observations close to the final qualification check.

```sh
aitm-usage --project "$ROOT" service install --wheel "$WHEEL" --interpreter "$PY" --wheel-sha256 "$WHEEL_SHA256" --json
aitm-usage --project "$ROOT" export --as-of "$FIXED" --rate-card "$RATE" --output "$EXPORT_REPLAY" --json
aitm-usage --project "$ROOT" status --json
```

### Establish both collection orders independently

Use the same genuine native route and scope the isolated cases to issue #83. Collector processing order can differ from the native order even though the native queued tool receipt always precedes its request. For each provider perform each case in isolated registered state. A fresh isolated UUID, source root and unanchored controlled native session per case is the simplest way to make the held source unique. Preserve the original canonical inbox publication from `<isolated-root>/inbox/<command-id>.json` and an exact, complete-line prefix of the actual selected native source. Hold and deliver those original bytes under private mode with the collector stopped between transfers. Keep the native telemetry in its original location and use an append-only copy of the exact prefix at a single stable path inside the registered isolated source root. Preserve source order and every byte. Keep the exact copy, its byte length and digest until validation.

- **Marker first.** Queue the actual native marker while the isolated collector is stopped and retain the original inbox publication. Keep the copied source at its prefix before the target boundary, or withhold that source until the first poll. Run `aitm-usage --project "$CASE_ROOT" collect-once --json` and retain the exact `status.json` for that poll. Require a durable `pending` command with no proven boundary and zero held sources at this stage. Deliver the exact source prefix through the real next request and the measured usage, then poll to settled.
- **Boundary first.** While stopped, move the exact original inbox publication outside the inbox into a private evidence directory before running the first poll. Expose the actual source prefix through the requested boundary in the registered isolated source root, using an unanchored segment so the collector holds it. Run one poll and retain that poll's exact `status.json`. Require one held source, no durable disposition for the withheld command, and no qualified first request at the fixed sequence. While stopped, transfer the original bytes back to the exact same private inbox filename without re-enqueueing or replacing existing evidence. Poll to settled and retain the accepted command and its first measured request. A second poll can be needed after accepted enrollment.

Use owner-only files and authorized stopped state for these private transfers. Capture `before_sequence` from the first poll's exact status and `after_sequence` after acceptance and usage commit. Use `Ledger.as_of` to verify the pending/absent and accepted transitions. The installed verifier replays read-only discovery, scanner and adapter evidence against the authenticated historical frontier. An export row alone cannot establish either processing order. Keep the case transcripts, private ACK files and proof paths separate from the publication.

### Rehearse recovery in separate existing state

Register a separate recovery project with the approved source and checkout authority. Seed it with an authorized measured workload so the fixed export contains rows. An exact retained prefix from the authorized #83 ordering exercises is suitable when the rehearsal cutoff precedes the selected requests and its registration approves the actual checkout. Install the primary wheel and retain the exact response. Create and verify a backup while the service is running. Use its fixed `sequence` for every rehearsal export. Confirm stopped state before restoring into that same existing registered root. Keep the bundle outside the replaceable store.

```sh
aitm-usage --project "$REHEARSAL" backup --output "$BUNDLE" --json
aitm-usage --project "$REHEARSAL" export --as-of "$RECOVERY_FIXED" --rate-card "$RATE" --output "$RECOVERY_BEFORE" --json
aitm-usage --project "$REHEARSAL" service stop --json
aitm-usage --project "$REHEARSAL" restore --backup "$BUNDLE" --json
aitm-usage --project "$REHEARSAL" export --as-of "$RECOVERY_FIXED" --rate-card "$RATE" --output "$RECOVERY_RESTORED" --json
aitm-usage --project "$REHEARSAL" service install --wheel "$WHEEL" --interpreter "$PY" --wheel-sha256 "$WHEEL_SHA256" --json
aitm-usage --project "$REHEARSAL" service upgrade --wheel "$SIBLING" --interpreter "$PY" --wheel-sha256 "$SIBLING_SHA256" --json
aitm-usage --project "$REHEARSAL" export --as-of "$RECOVERY_FIXED" --rate-card "$RATE" --output "$RECOVERY_UPGRADED" --json
aitm-usage --project "$REHEARSAL" service upgrade --wheel "$WHEEL" --interpreter "$PY" --wheel-sha256 "$WHEEL_SHA256" --json
aitm-usage --project "$REHEARSAL" export --as-of "$RECOVERY_FIXED" --rate-card "$RATE" --output "$RECOVERY_ROLLED_BACK" --json
```

Capture UTC completion times for the backup and restore calls. Their JSON responses agree on project, key, schema, fixed sequence and authenticated manifest digest. The two successful upgrades each retain an independent verified backup under `service-backups/<backup_id>`. Keep both directories and both exact retained wheels. A failed upgrade returning `activation-rolled-back` is a nonzero outcome with the prior service recovered. `recovery-required` keeps the private operation evidence and leaves the rehearsal open. Resolve that evidence through the reviewed U09 lifecycle path before resuming a successful rehearsal. Fixed exports before restore, after restore, after upgrade and after the explicit version rollback must match byte for byte. Verify the successful command dispositions, process-start evidence and hashes before continuing.

### Assemble and check the receipt

Use `tests/fixtures/activation/receipt.json` as the closed public field layout. Its basis is `fixture-only` and its values are for tests. Create the real U11 receipt from the observed values below. Use `real-controlled` for the approved #83 exercise. UTC values use ISO-8601 with UTC offset zero. All SHA-256 digests and sample pseudonyms use exactly 64 lowercase hex digits. A validated ledger `SourceRef.value` is `hmac-sha256:<digest>:<authentication-tag>`. Publish only its middle component. An export row's `source` already omits the tag. Take its digest component as the public sample key.

| Public group | Derive from these observations |
| --- | --- |
| Header | Fixed schema `aitm-usage-activation/v1`, registered project UUID and cutoff, independently reviewed source commit, and current UTC `observed_at` after capturing the status and other proof. |
| `collector` | Exact approved wheel digest, U09 version and interpreter, original install's `producer_started`, pre-stop captured raw status heartbeat, restart's `producer_started` and initial heartbeat, then final captured raw service heartbeat. The poll interval comes from U09. Set the three agreement flags only after checking owned unattended registration, exact producer agreement and private files. |
| `providers` | Select the original author and reviewer streams in final `status --json`. Use provider, verified route, client/format version, digest of `source_ref`, offset, authenticated `observed_through` and retention limit (or null). The matching raw snapshot and exact ledger sequence authenticate these values. |
| Provider `coverage` | For each selected stream, use `observed` for a model or effort switch with two distinct known values in the fixed collected usage, otherwise `source-gap`. Use `observed` for a supported native error between measured requests, or a source-linked independent nested request. Use `source-gap` when that evidence is unavailable. `task_quota` and `actual_spend` are `unknown`. Preserve partial quantities and known API-equivalent prices in the fixed export. |
| `workflow` | Use the eight selected fixed export row keys from the scoped workload. Use the sequence at which the draft alias first appears. Roll up #83 and both children at that same fixed export cutoff. Use the actual observation counts, including the inclusive #83 count. |
| Each `orders` entry | Isolated project UUID, provider, order, digest of `ledger.pseudonymize("inbox-command", str(command_id))`, SHA-256 of the original canonical publication bytes and exact retained source prefix, accepted first request's stable usage key, and the two fixed ledger sequences. |
| `export` | Fixed export and replay CLI cutoffs, matching SHA-256 and row counts, and the two distinct catch-up keys from the original provider streams in a settled post-restart view. |
| `recovery` | Rehearsal project UUID, backup sequence and manifest digest, observed initial process start, recorded backup and restore times, exact sibling and rollback activation heartbeats, sibling version and wheel digest, and matching SHA-256 and row counts from the four rehearsal exports. |

For historic state use the installed Python interfaces with the same package as the operator console. `open_project(Path(root)).as_of(sequence)` supplies the validated view. `rollup(ItemKey(...), view)` from `aitm_usage.rollup` gives the fixed direct and inclusive totals. At the alias commit, the current typed `DraftAlias` first appears compared with `as_of(sequence - 1)`. The exact command's typed `CommandReceipt` contains its accepted boundary. Match that boundary to a `UsageObservation` in the fixed view, verify its effective scope with `aitm_usage.scopes.resolve_scope`, and select the digest from the corresponding `Revision.key`. For the two catch-up observations, use the settled post-restart view and select measured records absent from the pre-stop view with observed times after the pre-stop heartbeat and before the new process start. The raw status snapshots are the actual `status.json` bytes written by U08. Public `status --json` output is a mapping aid and cannot substitute for those snapshots.

Write the matching closed private proof to `$ROOT/activation-proof.json`, mode 0600, in the registered project root. These are its exact keys. Embed each captured lifecycle or backup JSON result as its original object, including any null fields. Path values are canonical absolute paths to the retained private evidence. Construct this file after reviewing the saved artifacts and the independently approved source/wheel values.

```text
schema                  aitm-usage-activation-proof/v1
source_commit           approved source commit
approved_wheel_sha256   independently recorded approved wheel digest
previous_lifecycle      original production install JSON object
previous_stop           production stop JSON object
lifecycle               production restart install JSON object
previous_status         path to exact pre-stop U08 status.json snapshot
status                  path to exact post-restart U08 status.json snapshot
export_before           path to pre-stop fixed export directory
export_replay           path to post-restart fixed export directory
orders                  JSON array in exactly the order of the public orders array
  root                  isolated registered state directory
  publication           file with original canonical inbox bytes
  source                stable approved path containing the exact native prefix
  prefix_bytes          byte length of the retained prefix from offset zero
  before_status         path to exact first-poll U08 status.json snapshot
recovery                JSON object
  root                  registered rehearsal state directory
  bundle                retained backup directory
  initial               rehearsal original install JSON object
  stop                  rehearsal stop JSON object
  backup                rehearsal backup JSON object
  restore               rehearsal restore JSON object
  resumed               rehearsal install-after-restore JSON object
  upgrade               rehearsal sibling upgrade JSON object
  rollback              rehearsal upgrade back to primary JSON object
  before                fixed export directory before restore
  restored              fixed export directory after restore
  upgraded              fixed export directory after sibling upgrade
  rolled_back           fixed export directory after rollback
```

Run the installed command against the same registered root and pass the receipt's canonical path. The capture heartbeat must be within 45 seconds of `observed_at`, both live watermarks must be within 15 minutes and any known shorter retention, and `observed_at` must be within five minutes of the check. A check spanning an unstable status read can be retried with a new coherent capture of the same running process. Keep the exact prior artifacts and fixed sequence.

```sh
aitm-usage --project "$ROOT" qualify --receipt "$RECEIPT" --json
```

Exit zero with `{"status":"qualified"}` certifies the installed read-only checks. A nonzero result gives a bounded disposition such as `fixture-only`, `source-watermark`, `process-incarnation`, `wheel-mismatch`, `processing-order` or `export-parity`. The pure Python receipt validator checks only structure and internal consistency. Keep the installed result with the reviewed evidence. Publish the sanitized receipt after scanning it for raw IDs, paths, credentials, content and authentication tags. Keep status snapshots, transcripts, inbox publications, recovery artifacts and the private proof in the authorized local evidence location.

Leave the qualified production LaunchAgent and same registered ledger in service. Future upgrades must use verified wheels and same-schema recovery. Preserve the fixed export and local revision history for later C44 compatibility and idempotent receiver qualification.
