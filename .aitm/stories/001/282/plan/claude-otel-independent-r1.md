[05:20:28]
# HOLD on #282

**Verdict: HOLD.** The disposition itself is honest. It stays bounded, every percentage checks out, the zero denominator is handled correctly, and it claims no prevalence, ownership or live retransmission. It is on hold only because two of its evidence claims can't be reproduced from the supplied material. Both fixes are small. I reviewed only the provided material and ran nothing.

## Numbers checked (all consistent)

| Claim | Calculation | Result |
|---|---|---|
| Child requests | 2/4 | 50% ✓ |
| Child input tokens | 4/8 | 50.0% ✓ |
| Child output tokens | 128/324 | 39.5% ✓ |
| Child cache-read tokens | 1942/18723 | 10.4% ✓ |
| Child cache-creation tokens | 2149/2790 | 77.0% ✓ |
| Child cost share | 10574/22406 | 0.471927 → 47.2% ✓ |
| Earlier child cost | 8987/22406 | 40.1% ✓ (the final child cost 1587 is the part in the parent result) |
| Replay child totals vs feasibility child totals | | identical ✓ |
| Replay parent minus Agent-prompt parent | 3 / 16 / 0 / 8296 / 50025 | a plausible cold-cache control prompt ✓ |
| Replay deliveries | 8 = 2×4, then 4 → 1 gap → 5 | ✓ |
| Control sample | 2 sessions / 5 prompts / 5 joined / 1 scoped / 1 story | matches the narrative ✓ |

## Blocking findings

1. **The positive-control result can't be reproduced.** The sample script hard-codes `start = 2026-11-10` and `end = 2026-11-13`, so it can only produce the zero-window JSON. The control JSON (Nov 9 23:06:05.589056 to 23:16:20) needs a different script or a modified run that wasn't supplied. **Fix:** make the window a pair of arguments and record the exact command for both runs, or supply the variant and its hash.

2. **The replay's integrity anchor isn't supplied.** The replay checks hashes against `trial/verified-replay.json`, but the only artifact provided is the feasibility output, which is written to `feasibility.json`. Two related gaps:
   - `wire.jsonl` is hashed but no script uses or checks it.
   - Nothing links `telemetry.json` to the raw capture, so the claim to "replay the original local OTLP payload" isn't shown.

   **Fix:** state or show that `verified-replay.json` is byte-identical to `feasibility.json`, or give its hash. Also show how `telemetry.json` derives from `wire.jsonl`, or narrow the wording.

3. **"Authenticate its registration against the accepted activation receipt" overstates the check.** The script only does `assert ledger.identity.project_id == approved["project_id"]`. It never compares the registration (anchors, source roots) to the receipt. Because it's an `assert`, it also disappears under `python -O`. **Fix:** either compare the registration digest or anchors to the receipt with an explicit `raise`, or reword the claim to "project identity matched".

## Non-blocking findings (wording or hardening)

4. **"No overlap was observed" depends on how overlap is detected.** The sample script only finds children through a completed foreground `toolUseResult` that has both `agentId` and `usage`. These are invisible to it:
   - interrupted, background or orphaned `subagents/agent-*.jsonl` sidecars
   - sidecar rows that aren't filtered to the time window

   Either qualify the sentence ("no completed foreground Agent result observed") or also count the sidecar files in each session's `subagents/` folder.

5. **"Restart" and "reopening the store" overstate what happened.** Each `store()` call opens a new SQLite connection inside the same process, so there was no process restart. The field name `duplicate_delivery_attempts_before_restart` and the narrative should say "reconnect" instead.

6. **The surface details are typed in, not checked.** `"macOS Claude Code 2.1.318"` is a literal string in the feasibility script. Check it against the telemetry's `service.version` and OS fields.

7. **Two other claims aren't checked by the scripts.**
   - "Tool content disabled": only prompt redaction is tested, not tool-detail attributes.
   - "Tool-free control prompt": nothing tests that the fifth request belongs to one.

8. **"Earlier child" depends on event order.** `child_requests[0]` takes the first child request in whatever order the telemetry batches arrived. Sort by timestamp, or match it against the order of the child transcript rows.

9. **"Read only identity, scope, time and counters" is inaccurate.** `metadata()` parses every full transcript row, including message text, into memory. Nothing is kept or exported, but the claim should say "retain/export only".

10. **Privacy notes.**
    - The output JSONs contain no paths, IDs, prompts or labels ✓.
    - The sample script itself hard-codes `/Users/kpburson/...`. If the scripts are published with the disposition, they expose a home path.
    - The replay leaves `scratch-reconciliation.sqlite3` behind, keyed by unsalted SHA-256 of provider request IDs. Delete it, or confirm `target` is a temporary folder.

11. **The zero-window reason doesn't say why the window is empty.** Its `reason` text is the same boilerplate as the control's. It doesn't say whether the zero means no Claude use or no admission/ingestion after activation. This is acceptable under the brief, but one sentence would make it clear.

## Confirmed boundaries

- Production prevalence, per-story exposure and the correction factor are left unknown.
- Live retransmission and original ownership are explicitly unproven.
- The control is described as a planned workload that the ledger's selection depends on.
- Nothing changes in dependencies, the ledger, reports or production.
- #204 and Epic #100 are kept separate.

After fixes 1–3 this should get a PASS. Findings 4–11 can go in as wording changes.
