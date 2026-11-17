<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-84fdbdfe0dd75c4a33ae32978465093a"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-implementation-plan.md"
artifact_commit: "bd28ecf7fcaf212a6dfd3fae128e3a7871691dcb"
artifact_blob: "498c3cd756b0fe1dd7c6d817a262970abaa14cfb"
artifact_digest: "sha256:361618e5244f2c64aaffb98a31a3ea291ee62797f27c700304f41bc7b225885f"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:a3aefea571c34dba0defe3439ea1d9d5946cf7b46dd4524a6cd5b3df66a84530"
  identity_source: "runtime"
started_at: "2026-11-17T12:24:55.979Z"
submitted_at: "2026-11-17T12:30:58.055Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised plan at artifact digest `sha256:361618e5…885f` (commit `bd28ecf7`) against my turn-1 response, author response 1, and the evidence I verified in turn 1. That evidence is the retained `worker.sb`, the pinned `ledger.py`, `host_fs.py` and `monitor_registry.py`, the receipt timestamps, and the accepted hosted plan's stop rules.

**Turn-1 Required change 1 (budget headroom and feasibility) is resolved.** Item 7 now does each of the following:

- **Exact interval.** It states the historical closeout interval exactly: 2026-11-17 06:05:28 → 06:20:00 UTC. The start matches the receipt's `hosted_last_run_finished_at`.
- **Computed headroom.** It gives the headroom at the 12:26:15 UTC draft, and I checked the arithmetic:
  - 2.152 + 0.242 (06:05:28→06:20:00) + 0.293 (12:08:39→12:26:15) = **2.688 h** cumulative;
  - 3.75 − 2.688 = **1.062 h** to packet acceptance;
  - 6 − 2.688 = **3.312 h** overall;
  - 2.5 − 2.152 = **0.348 h** admission/preflight.
- **Clock classification.** It charges implementation, local verification, packet preparation and review, and the fresh in-job boundary and calibration to the admission/preflight clock.
- **Option (b).** It takes my option (b): an explicit 8 + 2 + 7-minute timebox, with the remaining time for hosted admission. It states that review latency or runner drift can leave a bounded HOLD, and requires the revision and its tests to be retained in that case.
- **Owner authorization and limits.** It says the owner authorized this pickup under the original limits, and requires the exact remaining budgets to be recalculated and written at acceptance.
- **In-job enforcement.** The deadline is now enforced inside the job, not only as an accounting rule. Item 6 records the decision time in the receipt and refuses product dispatch after the bound UTC admission deadline. Item 1 brings `integrated.py` and `stage-b-inputs.json` into scope for that check. Runner queue delay or slow calibration therefore fails closed instead of overrunning the phase.

The author declined owner re-authorization. My required change offered that as an alternative, not an obligation, so the decline is acceptable.

**Turn-1 optional suggestions:**

1. **Probe call site.** Item 3 keeps the probe inside the integrated-only condition, and the author reports that the unit suite preserves the Stage A generator. A dedicated call-site assertion is still not stated explicitly. This is not blocking.
2. **Basetemp.** Item 6 now states that the controller leaves the pytest basetemp to be created by pytest under the worker-owned scratch root. That closes the gap for ancestors below the scratch root.
3. **Rebind ambiguity.** Item 5 now refuses an allocation on the older image under this packet. Any new runtime pin needs a fresh Stage A build and independent review. The ambiguity is resolved.
4. **Source citations.** The packet still has to cite the ledger and ACL implementation, and the probe verifies the root:wheel 0755 and worker:staff 0700 expectations at runtime. That is sufficient.

**New strengthening in this revision (from the SAR), which I checked:**

- **Controller readback.** The controller now performs an independent outside-sandbox metadata and ACL readback, and every worker row must match it byte for byte. This closes a real hole: without it, a sandbox that masked ACL reads as ENOENT would make an ACL look absent and pass the probe.
- **Worker UIDs.** The worker's real and effective UIDs are pinned to the non-root worker UID. This matters because the product predicate uses `os.geteuid()`.
- **Canary creation.** The canary is now created by the controller with `O_CREAT|O_EXCL|O_NOFOLLOW`, mode 0644. Discretionary file permissions would allow the worker to read it, so an EPERM data-read denial proves the sandbox denied it, not file permissions. `/Users/Shared` is root-owned sticky with mode 1777, so the controller can create the file there.
- **opendir.** The enumeration negatives are now specified as EPERM from `opendir`. Directory reads are denied at open, so this is a precise test.

I have no remaining required changes.

## Findings

1. **Hosted admission has only about four minutes in the timebox.** (Optional, informational)
   - The 0.348 h admission/preflight balance is 20.9 minutes. After the reserved 8 + 2 + 7 minutes, about 3.9 minutes remain for:
     - the push;
     - hosted runner allocation;
     - compiling the probe;
     - fresh boundary admission and tracing;
     - runtime restore;
     - two report replays and the refusal case;
     - three calibrations and the intake refusals.
   - Prior receipts show individual Stage B steps taking several minutes each, so the in-job deadline is very likely to refuse dispatch.
   - The plan already acknowledges this and fails closed, so it is not a defect. The expected outcome is still worth stating plainly, so that the resulting HOLD is read as budget exhaustion rather than a new boundary finding.

2. **The byte-for-byte match needs the controller to compute owner class relative to the worker UID.** (Optional)
   - The worker emits an owner class (root or worker) relative to its own UID. The controller runs as UID 501.
   - For the byte-for-byte comparison to be meaningful, the controller readback must compute owner class against the pinned worker UID, not its own. Otherwise the scratch-root row cannot match, or the comparison is silently weakened to compare something other than class.

## Required changes

None.

## Optional suggestions

1. In the acceptance note or packet, state the expected outcome under the timebox. Given about 3.9 minutes for the whole hosted admission and calibration sequence, the most likely result is a deadline refusal before product dispatch. Label the resulting HOLD as budget-bound, distinct from a boundary or product finding.
2. Specify that the controller's outside-sandbox readback derives owner class from the pinned worker UID, and emits rows in exactly the worker's format, so that the byte-for-byte comparison checks the same predicate.
3. Add the call-site assertion from turn 1, optional suggestion 1: `prepare_boundary` invokes `ancestry` only for the integrated profile.

## Decision

accepted
