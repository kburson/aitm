<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-465e6e343ae2e7bc3ff567f646c08386"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-qualification-findings.md"
artifact_commit: "e7962ba930426006eeb272d3c80fca452123e11a"
artifact_blob: "446cd92432e686752db37e48b4fea612b613313e"
artifact_digest: "sha256:0b980ca1b80eeb8588bc803d0fdcf1a76f6d721595cd18e011b22eb0c00b35d2"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:ca2e6e5dd8544fac11d41eec2903c201b5ea9783bb31dcfd24948053f30276aa"
  identity_source: "runtime"
started_at: "2026-11-17T06:10:27.377Z"
submitted_at: "2026-11-17T06:14:40.658Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-hosted-qualification-findings.md` (blob `446cd92`, digest `sha256:0b980ca1…`). I checked it against these sources:

- the paired receipt `.aitm/stories/003/368/attachments/2026-11-16-368-hosted-qualification-receipt.json`, read in full;
- the accepted [hosted observation plan](../../../../2026-11-16-368-hosted-observation-plan.md), the [Stage B preflight packet](../../../../2026-11-16-368-hosted-preflight-packet.md) (native-obligation section), the image re-admission and discovery-retry packets (artifact and runtime bindings), and the turn-1 reviewer response in review `dabe24b0…`;
- the [independently reviewed local findings](../../../../2026-11-16-368-live-tracing-findings.md);
- the trusted local cache named in the artifact, `/Users/kpburson/Library/Caches/aitm-368-hosted.MVxC2n1K/integrated-44028499403-a1/`. There I read `reparsed.json` in full, the top-level structure and the `scoped-product` assignment of `raw/receipt.json`, `raw/worker.sb`, `raw/worker-boundary.stdout` and `raw/hosted-report-3.json`, and the failure tracebacks and short summary in `raw/scoped-product.stdout.log`.

The following claims hold up against that evidence:

- **Headline counts.** 7 passed, 22 setup-failed, 1 call-failed and 0 missing match `final_summary`, `product_native.failed_phases` and the reparse. The 30 assigned node IDs in the controller receipt are the 23 failed IDs plus the 7 passed IDs, with nothing extra or missing. Driver exit 1 and DTrace exit 0 match.
- **Native multiplicity.** 74 = 22 fixture consumers × (generate, sign, verify) + 4 profile-revising bodies × (sign, verify). This matches the preflight packet's static derivation. 22 observed `keygen_generate` with 0 sign and 0 verify, and 52 remaining, match the receipt and the reparse.
- **Retained-attempt table.** All ten rows match the receipt for run, attempt, image, gate and failure text. The artifact IDs match the ones bound in the preflight, restore-retry, re-admission and discovery-retry packets. The final integrated run used runtime `402dda54…` from admission run `44024930299`/artifact `14302787413`. That is the re-admitted 0504 bundle.
- **Report replays.** The local pair `be365757…` and the post-run local replay match. The hosted extra-path report (`hosted-report-3.json`) is `{"mode":"unavailable","node_ids":[],"reason":"unsupported-change"}`. Its digest `261a5127…` equals the trusted-local extra-path digest, as the artifact implies. The two hosted positive reports share `5d75994a…`. They differ from the local positive digest, which fits the stated per-side snapshots (`6ee7f9b6…` hosted, `4c200d09…` local).
- **Failure texts.** `scoped-product.stdout.log` contains `PermissionError: [Errno 1] Operation not permitted: '/Users'` from `os.path.realpath` inside `monitor_registry._directory` (test line 576). It also contains the `LedgerError: Private ledger ancestry is unavailable` frames raised from the generic `except OSError` branch of `ledger._validated_path` at `ledger.py:217`. The artifact's hedge is accurate: the ledger error does not say which ancestor failed or whether `lstat` or `_check_acl` raised.
- **Timing.** 04:38:49Z → 06:05:28Z is 1.444 h, and 1.444 + 0.708 = 2.152 h. This agrees with the preflight packet's 1.317 h cumulative charge at 05:15:20Z, which implies the same hosted start time. Both checkpoints are inside the plan's 3.75 h and six-hour limits.
- **Local summary.** The local paragraph matches the reviewed local findings: no network adapters or shares, scratch-write and protected-path denials exercised, network denial configured but not exercised, `proc:::create` refused, zero `proc`/`syscall` probes, zero product tests.
- **Disposition.** HOLD, #368 open, #355 blocked, and the four `unqualified` coverage fields follow from the plan and the receipt.

I am requesting revisions for two reasons. First, the document states the cause of the integrated failure only in general terms, and it gives no resume condition, even though the retained sandbox profile identifies the cause precisely (Finding 1). Second, one calibration claim has no retained live evidence (Finding 2).

Limits of this review: I did not run Git, compute any SHA-256, query GitHub, or open the GitHub run or artifact links. Bash was limited to the two prescribed peer-review commands. I did not parse the raw DTrace streams myself; the native counts come from the receipt and `reparsed.json`. I did not read the product source beyond the traceback excerpts in the driver log.

## Findings

1. **The cause of the 23 failures can be identified from retained evidence, but the document leaves it general and gives no resume condition.** The artifact says the run "exposed the incompatibility between this worker policy and the product's ancestry checks" and calls the outcome "a result for the exact protected configuration". The retained profile `raw/worker.sb` makes the cause specific:
   - The profile starts with `(deny file-read*)`. Its only grant above the admission root is `(allow file-read-metadata (literal "/Users/Shared/aitm368-hosted"))`. `/` has only `file-read-data`. Neither `/Users` nor `/Users/Shared` has any read or metadata grant.
   - Worker scratch, and with it every pytest `tmp_path` (`/Users/Shared/aitm368-hosted/worker/pytest/...`), sits below `/Users` and `/Users/Shared`.
   - `ledger._validated_path` calls `lstat` and `_check_acl` on every ancestor from `/` downward. `monitor_registry._directory` calls `realpath(strict=True)`. Both therefore have to touch `/Users`, which the profile denies. The one direct errno, EPERM on `/Users`, is what this predicts.

   This is the same risk that review `dabe24b0…` Finding 1 raised for the literal-root rule ("If pytest 9.2.0 also stats another denied path (for example `/Users/Shared` …) the literal rule does not cover it"). The product hit it rather than pytest. The distinction matters for the disposition. The HOLD comes from a narrow, identifiable sandbox omission in the harness. It does not come from a runner-family capability limit or a product defect: the tracing, boundary, runtime, calibration and replay gates all passed. The document's final paragraph lists the hosted route as unresolved without saying so. A reader planning #355 cannot tell whether the hosted route is viable after one reviewed policy change or whether it is exhausted. The local findings set a precedent by stating an explicit resume condition. This document has none.

2. **The "controlled intake refusals completed" claim has no retained live record.** The calibration bullet says the refusals "completed, including worker-only green, stale or wrong identity, incomplete or duplicate phases and assignment, and missing or unassigned native children". Neither the paired receipt nor the hosted controller receipt (`raw/receipt.json`, top-level keys `admission`, `boundary`, `export`, `identity`, `invocations`, `trace`, …) contains a field, invocation or exported stream for any of these cases. The only recorded invocations are `calibrate-positive`, `calibrate-failure`, `calibrate-missing` and `scoped-product`. The preflight and re-admission packets cite nine and then eleven *offline* harness tests that "protect the early intake". The plan (Stage B.2) requires these refusals to be exercised "in these fenced invocations" of the live job. If they ran in the live job as in-process assertions that would have aborted the run, the document should say so and point to the code and evidence that show it. If they were covered only by the offline tests, the sentence overstates what the live job proved. In the same way, "uncertainty" in "Phase counts, uncertainty and identity are in the paired machine receipt" has no matching field in the receipt.

## Required changes

1. In "Integrated hosted result" or the closing disposition, replace the general incompatibility statement with the concrete cause from `worker.sb`. The worker profile grants metadata only on the literal admission root `/Users/Shared/aitm368-hosted`. The scratch ancestors `/Users` and `/Users/Shared` have no metadata grant, and `/` has `file-read-data` only. Cite the retained `worker.sb` (by cache path, and by digest if the export manifest has one). Keep the existing hedge that the ledger error does not identify which ancestor or call failed. Then state the resume condition, or state that none is planned. For example: a reviewed protection change granting literal `file-read-metadata` (and whatever ACL read `_check_acl` needs) on each scratch ancestor, with listing still denied, followed by fresh re-admission, a new packet and a fresh integrated run under the existing budget. Under plan Stage A.1, that change is a protection change and needs review before any rerun. Say explicitly that the passed gates (boundary, tracing, runtime, report replays, calibration) are not what blocked the run.
2. Make the intake-refusal claim match its evidence. Either cite where the live job recorded each listed refusal (receipt field, stream or code path that aborts on failure, with path and digest), or reword it to say what was actually shown, for example "covered by the N offline harness tests at <head>; not separately recorded in the live job". Also drop "uncertainty" from the receipt sentence, or add the field it refers to.

## Optional suggestions

1. The table shows that the images alternated rather than rolled forward once: 0473, 0473, 0504, 0473, 0504, 0473, 0504, 0473, 0504, 0504. "The hosted image rolled between allocations" understates this. Allocations are drawn from a mixed fleet, so a resumed run can land on 0473 again and HOLD at the drift check. Consider saying so, and naming the mitigation (re-run on drift, or keep both images admitted).
2. "A second fresh run was needed to test those capabilities against #354's exact assignment" reads as if one further run followed admission. There were five integrated attempts. Consider "Further fresh integrated runs were needed …" with a pointer to the table.
3. "Keep #368 open as the verified native cause blocking #355" is hard to parse; #368 is the blocking story, not a cause. Consider "Keep #368 open; it remains the verified native-observation blocker for #355."
4. The paired receipt's `admitted_runtime` block lacks the run and artifact it came from. The hosted receipt's `admission` block has them (`44024930299`, `14302787413`, head `e38d67d0…`). Copying them into `admitted_runtime` would let a reader bind the runtime digest without opening the cache.
5. Consider one sentence noting that the native multiplicity shortfall (52 missing sign/verify launches) follows from the setup failures and is not an independent observer finding. The artifact implies this, but the table row "22 of 74 direct children matched" could be read as a separate tracing gap.

## Decision

revisions-requested
