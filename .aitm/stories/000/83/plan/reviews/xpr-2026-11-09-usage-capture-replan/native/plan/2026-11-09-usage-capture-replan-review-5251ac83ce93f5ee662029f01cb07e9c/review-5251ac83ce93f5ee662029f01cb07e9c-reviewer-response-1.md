<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-5251ac83ce93f5ee662029f01cb07e9c"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-replan.md"
artifact_commit: "76a9cfd325d507523d18e6c83620b1a927f83605"
artifact_blob: "60e80e32c0318687fe3c113424756653326a186d"
artifact_digest: "sha256:45eb4be3089c1eeaa744f98b1c90e2c1329364e682492b0e8e8c363807ef0d44"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:be2e1af31a171c19a3157ffccc748eaf9c79acb8ac3da44acd18b46ef3aa1d6e"
  identity_source: "runtime"
started_at: "2026-11-09T15:09:08.408Z"
submitted_at: "2026-11-09T15:12:58.833Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 1 of an independent XPR review of `.aitm/stories/000/83/plan/usage-capture-replan.md` at sealed digest `sha256:45eb4be3089c1eeaa744f98b1c90e2c1329364e682492b0e8e8c363807ef0d44` (commit `76a9cfd`, blob `60e80e3`).

**Read evidence.** A line count reports 39 lines. The Read tool returned two contiguous ranges of the artifact: lines 1–20 and 21–39. The second range reached EOF at line 39. Neither output was truncated or replaced with an omission marker. This is the first turn of this review ID, so there is no prior response and no dispositions to verify. For context I read the full baseline `usage-capture-implementation-plan.md` (lines 1–190, EOF, no truncation), the full accepted design `design/usage-capture-design.md` (lines 1–50, EOF, no truncation) and `plan/leaf-issue-receipt.json` (lines 1–193). I also read lines 1–45 of the earlier plan XPR turn-1 reviewer response, but only to match its format. I also ran a targeted search over #83 markdown for the U11 and Core #2 wording. I did not rely on the conclusions of the SAR, SPR or earlier XPR rounds. The only shell commands available to me were join and submit, so I did not recompute the baseline raw SHA-256 on line 3. Its value `07919dde…42daf5` does match `plan_sha256` in the leaf-issue receipt.

**Verified as sound.**

- *Estimate arithmetic.* The prior-hours column matches the baseline table and the receipt for U02 (3.5), U13 (2.5), U06 (3) and U08 (3.5). Each of the four increases is +0.5, so 46 + 2 = 48, which matches line 24. Every leaf stays at or under 4 hours. U01 stays at 4 hours, and its repair is forecast within the remaining U01 budget. Line 13 has a stop rule for cap pressure, scope change or dependency change. This follows the owner's instruction to pause and return to planning when an estimate deviates.
- *Issue mapping and DAG.* U02/#85, U13/#86, U06/#90 and U08/#92 match the receipt. The new edge U13→U06 (#86→#90) does not create a cycle, because U13 depends only on U02 and U06 depends on U04 and U05. It also adds no critical-path delay, because U13 and U03 both start after U02. U07 already depends on both. Line 24 requires the edge in the native dependency, the planning records and the U06 JIT.
- *CAS and schema (line 16).* Rejecting a stale expected checkpoint, including when the desired checkpoint equals the current one, closes the silent-continuation hole. A true retry adds no history, so it stays idempotent. The test set (rollback, true retry, continuation with the correct prior) is adequate. A structural schema check that refuses a same-column rebuild without PK or STRICT is the right regression.
- *Writer identity (line 15).* A per-project guard outside the replaceable state tree is the right fix for lock-file replacement during restore and for replaced roots or ancestors. The guard is taken before the state lock, which gives a consistent lock order. U09 reuses the guard, and readers and backup keep their lease-free snapshot contract. Line 15 covers refusal of a second process after lock, root or ancestor replacement, and refusal of drifted state.
- *Sanitized metadata and pseudonyms (line 17).* Unsupported labels become Unknown, possibly with a keyed pseudonym, and free text is not retained. Source references are authenticated and bound to project and key context. The test set covers a genuine round-trip and rejection of foreign-key and fabricated references. Line 17 also exposes the same check to inbox writers and requires project identity on every LedgerView, including sequence zero. All of this matches design line 19.
- *Closed union (line 18).* A closed typed union with an explicit codec, no plugin registry and no opaque payloads is the right constraint. The per-record verification gate is good.
- *Lifetime, Core exclusion and resume.* Line 35 keeps C44 as a later consumer of the same collector and ledger. Line 39 keeps the #83 activation gate before Core C01 and leaves Epic #2 unstarted. The resume gate requires SAR, SPR and XPR acceptance, then resumption on the preserved #84 candidate, and integration only after the repaired exact source is accepted. Line 20 says the repair does not authorize feature logic in U01.

**Areas needing revision.** The amendment exists because downstream ownership and proof obligations were left unnamed. It repeats that gap in three places. The file and command-path edits for later leaves are still unnamed (F1). Crash-window recovery of the atomic inbox has no required proof (F2). The new ACL rule does not cover the private bytes that leave the state tree in U09's backup bundle, which holds the pseudonym key (F5). Two estimate-discipline gaps remain. U11's evidence route moved from incidental Core #2 work to dedicated controlled #83 sessions without changing the plan text or the estimate (F3). The QuotaEvidence type was added to U01 without proofs or a place in the forecast (F4).

## Findings

1. **F1 (required): Downstream file and command-path ownership is still implicit.** Line 9 gives the replan's cause as ownership that "assumed a shared typed ledger without naming the changes that let downstream leaves persist their own records". The new table still leaves these points open:
   - U13, U06 and U08 must "register their codecs" (lines 29–30). Line 18 forbids a runtime registry, so registration has to edit a static codec table. The amendment does not say where that table lives. If it is `ledger.py`, these leaves would edit a file that line 28 assigns only to U02.
   - U08 must "add the anchor command to the U02 command path" (line 31). That path is in `scopes.py` (U02's file in baseline line 80), in `ledger.py`, or in both. U08's baseline files are `{service,cli}.py` only.
   - U13 queues alias and parent commands through U02's inbox (line 29). The amendment does not say whether that needs a dispatch edit in `scopes.py` or `ledger.py`, or whether U02's dispatch handles the closed union by data alone.
   - No sentence states that U03, U04, U05, U07, U09, U10 and U12 make no edits to `types.py`, `ledger.py` or the inbox dispatch. U03 runs in parallel with U13 after U02. If U03 needs a persisted type, line 35 ("follow the published pickup order") does not serialize it against U13.

   Line 35 hands the exact changes to each JIT. A JIT cannot grant ownership that the plan has not assigned, so the plan must close these points.

2. **F2 (required): Atomic inbox recovery has no required crash-window proof, and "original disposition" conflicts with pending markers.** The only inbox proof in U02's row (line 28) is "a repeated command returns its original disposition and conflicting bytes do not overwrite it". Atomic consumption needs proof at the actual failure points:
   - (a) a crash after the ledger transaction commits the command and its disposition but before the acknowledgment is published or the inbox file is retired;
   - (b) a crash during publication, which leaves a temp or partial file;
   - (c) a fresh process that replays (a) without applying the command twice and that ignores or quarantines (b) without consuming it.

   U12's SIGKILL points (baseline line 158) are between scans and inside an uncommitted provider batch. They do not cover the inbox commit-to-acknowledgment window. Baseline line 82 also says markers return `pending` until the adapter validates the boundary and then become `accepted`. Taken literally, "returns its original disposition" would freeze a pending marker or hide its acceptance.

3. **F3 (required): The #83-only U11 route is not written into U11, and its effort is not estimated.** Line 35 says only "Use #83-only real qualification for U11". Baseline U11 step 1 (line 183) still names "scheduled Core #2 child preparation for C01/#3 and C02/#4" as the normal shared-chat observation and requires "an overlapping normal Claude review". Line 3 says the amendment "controls only the changes listed here", and this sentence does not clearly replace that bullet. Under the owner's exclusion, every U10-required element must now come from controlled #83 sessions. Those elements are hydration, two child scopes, graduation with disposable IDs, an overlapping author and reviewer, the inclusive rollup, development ownership and housekeeping, on both provider routes and in both marker arrival orders. Baseline line 183 kept observed planning and review time outside U11's 3.5 hours because it was normal Core work that would happen anyway. That reason no longer holds, since these sessions exist only for qualification. Their effort is now unestimated, outside the 48-hour aggregate, and has no deviation stop. Also, after activation little or no real #83 work may remain to supply a "normal" overlapping Claude review.

4. **F4 (required): The QuotaEvidence addition to U01 has no proof obligations and is not in the forecast.** Line 33 makes U01 own the QuotaEvidence type and a typed AdapterResult field. The type has provider, pseudonymous account and bucket, UTC times, a fixed-point percentage with precision, and a closed source classification. That is new U01 scope. The repair section (lines 13–20) does not list it. The repair forecast covers only "focused regressions, repair and exact-head review". Line 18's verification gate applies to "every new command and record", and QuotaEvidence is a shared envelope that U01 may not persist, so it is unclear whether the gate applies. The type will be fixed before U04 and U05 consume it and U06 interprets it. A defect found later would therefore cross three leaves.

5. **F5 (required): The ACL and ancestry rule does not reach U09's backup bundle or restore source.** Line 15 requires validating macOS extended ACLs, including inherited permissions, "before private bytes can be created or accepted", with refusal proven on the real Mac. All of its obligations sit in U01. U09 writes a bundle containing the database and the private pseudonym key (baseline line 166) to a caller-chosen `--output <directory>`, and accepts a caller-chosen `--backup <directory>` on restore. Both are outside the validated state tree. An inherited allow ACL on the destination would expose the key and history even with POSIX modes of 0700 and 0600. That is the defect class line 9 names, and U09's 4-hour estimate does not account for the proof. The amendment also does not say explicitly that the control guard location gets the same ACL validation.

## Required changes

1. **(F1)** Add an explicit ownership statement for downstream leaves.
   - (a) Name the module that holds the closed union and its static codec table, preferably `types.py`. State that U13, U06 and U08 add record types and codec entries only there.
   - (b) Say whether U02 delivers a dispatch that is data-driven over the closed command union, so later commands need no `ledger.py` or `scopes.py` edit. If not, give each consuming leaf (U13 for alias and parent, U08 for anchor) the exact file and function edits it may make, and check that its estimate covers them.
   - (c) State that U03, U04, U05, U07, U09, U10 and U12 do not edit `types.py`, `ledger.py` or the inbox dispatch, and that a need to do so stops the leaf and returns to planning.
   - (d) Add these files to the `Files` lists of U13, U06 and U08, or say that those lists are amended.
2. **(F2)** Extend U02's proof, or U12's if you prefer, and keep the estimate consistent.
   - (a) Record the disposition in the same ledger transaction as consumption.
   - (b) Kill the process after commit and before acknowledgment or inbox retirement. Show that a fresh process acknowledges with the recorded disposition and applies the command exactly once.
   - (c) Leave a torn or temp publication and show that a fresh process does not consume it and handles it deterministically, by ignoring, cleaning or quarantining it, with no raw content in diagnostics.
   - (d) Restate the replay rule: a replay returns the current recorded disposition for the command ID. `pending` may advance only to a final disposition, final dispositions are immutable, and conflicting bytes never overwrite either.
3. **(F3)** Add a U11 amendment that explicitly replaces baseline U11 step 1.
   - (a) Name the controlled real #83 sessions and routes that supply each element U10 requires, including the overlapping Claude review, which becomes controlled rather than normal. Label them controlled, with disposable scoped identities for graduation.
   - (b) Confirm that U10's validator accepts controlled-labeled evidence for every required element and still rejects fixture-only evidence.
   - (c) Either estimate the dedicated controlled-session effort, folding it into U11 or a separately recorded qualification activity and updating the aggregate if it counts as implementation effort, or state a reason that still holds for keeping it outside. Apply the same stop and return-to-planning rule if U11 would exceed its cap.
4. **(F4)** List QuotaEvidence and the AdapterResult field in U01's repair scope and retained regressions. Prove a strict field shape and bounded fixed-point values with precision, a closed source classification, UTC-only times, a pseudonymous account with no raw handle, and rejection of a task-level burn field. State that this work is inside the two-hour forecast, or revise the forecast.
5. **(F5)** Require U09 to apply U01's ACL and ancestry validator to the backup destination before writing any bundle bytes. It must also apply the validator to the restore source before accepting any bytes. Add a real-Mac inherited-ACL refusal case to U09's test. Say whether U09's estimate changes. Also state that the control guard location gets the same ACL validation as the state tree.

## Optional suggestions

1. **O1 (guard lifecycle).** Define what `Ledger.open` does when the ledger exists but the control guard is missing. Refusing with a recovery diagnostic is safer than silently recreating the guard. Also check, at each write commit, that the guard path still resolves to the held descriptor (dev/inode), so a deleted-and-recreated guard cannot let a second writer in. The CAS on line 16 limits the damage, but the guard should stand on its own.
2. **O2 (deviation rule for all revised leaves).** Line 13 states the stop and return-to-planning rule only for U01. U02 and U08 are now exactly at the 4-hour cap with no headroom. Add one sentence applying the same rule to every leaf whose estimate this amendment changes.
3. **O3 (resume gate completeness).** On line 39, list the recorded preconditions explicitly. These are the native #86→#90 dependency, the updated estimate fields for #85, #86, #90 and #92, a refreshed leaf-issue receipt with the new aggregate, and the updated #84 leaf plan and JIT. Line 24 already requires some of these, but the gate names only "issue references".
4. **O4 (QuotaEvidence wording).** On line 33, "pseudonymous account and bucket" can be read as pseudonymizing the bucket. Say that the bucket is an approved normalized label, falling back to Unknown plus a pseudonym, consistent with line 17.

## Decision

revisions-requested
