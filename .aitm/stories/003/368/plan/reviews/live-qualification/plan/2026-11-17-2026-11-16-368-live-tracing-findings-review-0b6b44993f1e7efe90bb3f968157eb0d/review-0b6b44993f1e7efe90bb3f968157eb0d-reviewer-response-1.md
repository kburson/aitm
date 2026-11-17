<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-0b6b44993f1e7efe90bb3f968157eb0d"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-live-tracing-findings.md"
artifact_commit: "1ad21a4654234095258cc1f190285405b141b8f6"
artifact_blob: "6c737a235b31d057135232071db66fdca91807d6"
artifact_digest: "sha256:f220ce6cdc5e09c566328e6e2f1460cf68bd4ea7d10280631266790f9cc86ac3"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:65c6e6a93b23f3d9e2ed4dc77dc4e1db015e70a4506e6e0242517e4f12e4d187"
  identity_source: "runtime"
started_at: "2026-11-17T03:26:12.853Z"
submitted_at: "2026-11-17T03:30:02.244Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-live-tracing-findings.md` (blob `6c737a2`) against three sources. The first is the accepted plan `2026-11-16-368-protected-local-observation-plan.md`. The second is the prior checkpoint `2026-11-16-368-qualification-results.md`. The third is the receipt `attachments/2026-11-16-368-live-tracing-receipt.json`. I also read the retained private evidence under `~/Library/Caches/aitm-368-live.1R0LSSSt/`. That covered the pinned `diagnostic-v3/media/{guest-preflight.sh,run-preflight.sh,SHA256SUMS}`, the v3 export (`preflight.log`, `probe.d`, `worker.sb`, `sha256`, `interfaces.log`), `aitm368-probes.log`, the v2 export and initial logs, `diagnostic-v3/test-route.sh`, `diagnostic/qualification.c`, and `native-vm/provision-resumed.swift`.

The HOLD verdict and first stop are correct and supported. The plan's §1.4 tells the run to stop at the early capability probe on failure. The pinned `guest-preflight.sh` exits 83 (`HOLD trace readiness`) when DTrace never prints `READY`. The v3 `preflight.log` ends with that line, and the `trace.stderr` text matches the receipt. The `dtrace -l` log lists exactly 3 `dtrace` and 13 `profile` probes (IDs 1–3 and 31–43), with no `proc` or `syscall` entries. Several other claims also match the evidence:

- The 0.225 h (810 s) and 0.708 h (0.483 + 0.225) totals are correct.
- The guest runs 26.6.2 `25G83` with APFS and SIP enabled.
- The four `fe80::%utunN UGcIg` defaults pass the awk scope check. `anpi0` and `en0` both report `status: inactive`.
- The five `NO_ROUTE` lines are in the log.
- Controller UID is 0 and worker UID is 502.
- There are eight `DENIED` lines, and the nine `shasum -c` entries all report OK.
- `provision-resumed.swift` sets `networkDevices = []` and `directorySharingDevices = []`, attaches the input disk `readOnly: true`, and exits 64 on usage errors.

The two earlier helper failures are described accurately. The initial run logged `HOLD guest IPv6 default route`. The v2 run logged `HOLD guest has usable route -inet default` with `not in table`. Both earlier helpers failed closed. The final helper relaxes both checks, and that relaxation is justified by the zero-NIC VM configuration and by the tighter scope test. Zero product tests ran. #368 stays open and #355 stays blocked, as the plan requires on HOLD.

Before acceptance, the record needs these fixes:

- the custody of the decisive probe inventory;
- traceability of the route-parser controls that justified relaxing a fail-closed check;
- a few isolation claims that go beyond what was exercised;
- one mislabel of prior evidence;
- the residual guest state.

None of these changes the HOLD verdict.

Limits of this review: I could not compute SHA-256 values in this session. Because of that, I did not independently confirm the receipt's digests, including `inventory_sha256` and `manifest_sha256`, against the retained files. I checked only that the hashes listed in the export's `sha256` manifest match the receipt's `fail_closed_records_verified` entries, and they do. I did not inspect the guest disk.

## Findings

1. **The decisive `dtrace -l` inventory is outside the controller export and its custody is not stated.** The stop rests on two pieces of evidence: the compile refusal and the provider inventory. The inventory shows the `proc` provider is absent. The compile error alone does not explain why. The inventory file `resumed-export/diagnostic-v3/aitm368-probes.log` sits next to the export directory `aitm368-export.hrfXWUfm/`, not inside it. `run-preflight.sh` never runs `dtrace -l`. The export's `sha256` manifest does not list the file, and neither does the receipt's `fail_closed_records_verified`. The artifact's evidence paragraph says "The controller exported the logs and hashes from the guest… matched the exported manifest" and that the receipt "pins … provider list". A reader will assume the inventory went through that verified export path. It did not. The receipt has only a free-standing `inventory_sha256`, with no record of how the file was produced, by whom, or how it reached the host. The cleanup record says the guest was "shut down after the stock inventory", so the inventory was captured in a separate later step, likely a console session.

2. **The route-parser controls that justify relaxing a fail-closed check are not recorded.** Both earlier helpers stopped fail-closed, and the final helper accepts conditions the earlier versions refused. The artifact rests the change on the claim that "Its parser controls accepted the captured negative response and refused both a positive interface and an ambiguous error." Those controls are `diagnostic-v3/test-route.sh`, a host-side stub that redefines `route`. The receipt does not list that file or a digest for it, and no output from running it was kept. The script also copies `assert_no_route` instead of sourcing the pinned `guest-preflight.sh` (SHA `76dc6cdf…`). By eye, its lines 2–14 match the pinned helper's lines 49–61, but nothing binds the tested copy to the admitted bytes. As recorded, the claim is the executor's word.

3. **Some isolation claims go beyond what was exercised or recorded.**
   - (a) "The worker also ran under a sandbox that denied network operations." `worker.sb` contains `(deny network*)`, but the preflight never tries a network operation. The denial is configured, not observed.
   - (b) The worker's isolation depends on that sandbox. The `check-outside` sentinel is mode `0666`, so only the sandbox blocks the write. Yet the receipt never mentions the sandbox or `sandbox-exec`, and has no direct digest for `worker.sb`. The digest `8d27bf92…` appears only inside the export's `sha256` manifest. The profile is `(allow default)` plus write and network denials. Read isolation therefore rests on Unix permissions alone. That is fine, but it is part of the configuration the plan's §1.3 says the proof must be bound to.
   - (c) The plan's §1.3 also asks to "independently read back ownership and digests". Digests were read back (`shasum -c`), but no ownership or mode readback was captured.
   - (d) "The worker could read the admitted input" was tested with `test -r` and `test -x`, which are access checks, not actual reads or executes.

   The artifact does say "bounded isolation controls that were exercised", but the opening "passed … protected worker filesystem checks" and the network sentence read stronger than the evidence.

4. **"Static replay evidence" mislabels the prior assignment evidence.** The artifact says "The previous static replay evidence identifies the 30 archived IDs." The prior checkpoint says the IDs were "rechecked statically" and that the "trusted delivered CLI replay … [is] pending". The receipt says "prior static 30-node inventory only; live selection replay and assignment admission were held". The plan's §3.1 replay has not happened. Calling the prior evidence a "replay" could lead a reader to think it has.

5. **The residual guest state is not recorded.** The plan says to record setup and cleanup. `guest-preflight.sh` permanently creates the `aitm368worker` account (UID 502, home in the run directory) and the run directory `/private/var/tmp/aitm368-run.yOfK42bj`. It also writes `/private/var/tmp/aitm368-last-evidence`, and the export copy sits under `/Users/aitmcontroller`. None of these is removed. The pinned helper refuses to run if the worker account already exists (`HOLD worker account already exists`, exit 76). Re-running the same pinned preflight on the retained guest will therefore stop before isolation checks. The receipt's `cleanup.guest` and the artifact's "remains shut down with private evidence retained" leave this out, and the artifact does not say whether owner-approved cleanup of the disposable guest is still pending.

## Required changes

1. State how the `dtrace -l` inventory was run and captured: the identity, the boot, whether it was before or after the controller export, and the transfer path. Make clear in the evidence paragraph that it was not part of the manifest-verified controller export. Add its file name and role to the receipt next to `inventory_sha256`. If its custody cannot be attested, label it as executor-captured corroboration. The plan says to label live and offline evidence separately; apply the same care here.
2. Record `test-route.sh` in the receipt with its digest, its three control cases, and their observed outcomes. Either show that its `assert_no_route` is byte-identical to the pinned helper's, or say that the controls exercised a copy. If no run output was kept, reword the sentence to say the controls were run but their output was not retained.
3. Reword the isolation paragraph so the sandbox network denial is described as configured, not exercised. Add the worker sandbox mechanism (`sandbox-exec`, profile `worker.sb` and its digest) to the receipt's `preflight`. Note that ownership and mode readback was not captured, and that a resumed run must include it under the plan's §1.3. Describe the worker read check as an access check, or soften "could read".
4. Replace "previous static replay evidence" with wording such as "the prior static inventory check". Keep the existing statement that the §3.1 CLI replay has not run.
5. Record the guest's residual state in the artifact's disposition and in the receipt's `cleanup`: the persistent `aitm368worker` account, the run directory and pointer, and the export under the controller's home. Say that the pinned preflight will refuse to re-run on this guest (exit 76) unless that state is removed or a fresh guest is used. State whether owner-approved cleanup of the disposable guest is still pending.

## Optional suggestions

1. Explain the compile error. The helper runs `dtrace -Z`, which allows probe descriptions that match zero probes. Because `proc:::create` matched nothing, DTrace could not type `args[0]` and reported "matches an unstable set of probes". The inventory then confirms the provider is absent. Also note that `pid` and USDT providers are created per process and never appear in a bare `dtrace -l`. User-space probe capability was therefore not tested; it was not shown to be absent.
2. Before naming a protection change for resumption, record whether the missing `proc`, `syscall` and `fbt` providers come from the VM-guest kernel or from SIP. The DTrace SIP warning in the log is suggestive but does not settle it. One way is an owner-approved, read-only `dtrace -l -P proc` on the host. Another is to check how the #146 hosted macOS runner was configured. Either result points to the specific approval needed: a guest SIP DTrace relaxation, a different observer such as an entitled Endpoint Security client, or a hosted route.
3. Say explicitly that the 02:46:12Z–03:11:39Z interval between the checkpoint stop and the owner's acceptance is not charged, and why: the attempt was formally stopped, and review is accounted separately. The prior checkpoint did charge owner waits, so the word "conservatively" needs that explanation.
4. Make some small clarity edits. Change "test inputs" to "diagnostic inputs", so it is not confused with product tests. Name the "deliberate shutdown", meaning which guest shutdown and why it was triggered. Consider replacing the first-person "my console checks" to match the impersonal tone of the rest of the report.

## Decision

revisions-requested
