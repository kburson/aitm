# #368 local and hosted qualification findings

**HOLD for the exact reviewed comment-only closure and the pinned 30 Grok scope-receipt obligations.** The local experiment
stopped before calibration. The hosted experiment completed calibration and observed the whole assignment, with
**7 passes, 22 setup failures, 1 call failure and 0 missing test outcomes**. Local integrated execution, resistance to
unreviewed candidate code, candidate inventory and impact completeness remain unqualified. #368 stays open and #355 stays blocked.

## Why both experiments were necessary

**Disposable local guest.** This tested the intended offline pre-commit runner boundary. The APFS macOS 26.6.2 guest
(build `25G83`, SIP enabled) showed no VM network adapter or directory shares and exercised restricted-user scratch writes and
protected-path denials. Its stock DTrace refused the required `proc:::create` probe before launching the synthetic trace child.
The inventory exposed no `proc` or `syscall` probes. Worker network denial was configured and remained unexercised in this trial.
There were zero product tests. This establishes why the actual local environment could not finish qualification.
[Independently reviewed local findings](2026-11-16-368-live-tracing-findings.md) · [Local evidence receipt](../attachments/2026-11-16-368-live-tracing-receipt.json).

**GitHub-hosted macOS from #146.** The earlier #146 work justified trying this runner family; its runtime, source and assignment
were different. Fresh admission on this spike established the separate non-sudo worker, restricted filesystem and loopback
boundary, positive and negative kernel observations, independent USDT and protected instrumented runtime. A second fresh run
was needed to test those capabilities against #354’s exact assignment and fixture requirements. It reached the integrated
test and exposed the incompatibility between this worker policy and the product’s ancestry checks.
[Hosted plan](2026-11-16-368-hosted-observation-plan.md) · [Hosted plan SAR](reviews/2026-11-16-368-hosted-plan-sar.md) ·
[Final hosted run](https://github.com/kburson/aitm/actions/runs/44028499403/attempts/1).

## Integrated hosted result

- The final runner used ARM64 macOS 26.7.2 build `25G332`, runner image `20261112.0504.1` with its stock disabled SIP setting.
  The protected worker passed admitted-input read, scratch write, protected path and loopback checks, denial of a same-named
  scratch executable, allowed stat of the literal admission root and refusal of directory listing and of child metadata.
  Controller-owned DTrace captured the benign process lifecycle and user-space event. The authenticated runtime restored with
  exact file and symlink modes, interpreter digest, Mach-O probe table and pytest 9.2.0.
- Trusted local replays produced all 30 exact archive IDs and rejected an extra untracked path with exit 2 and
  `unsupported-change`. The two hosted positive replays agreed, bound hosted snapshot `6ee7f9b6d76eb68c95f6063acca447b3c41aa332c47fe36e718d2456542674ff`, and matched
  the exact base, file bytes, mode, archive and IDs independently checked on the trusted local side. Each side used its own stable
  checkout snapshot. The hosted extra-path case likewise refused with no IDs. A subsequent local replay remained byte-identical.
- A protected positive calibration observed the passing body and the expected successful direct keygen child. The separate
  assertion failure remained visible. The max-fail control retained that failure and reported the unexecuted assigned sibling
  as missing. The controlled intake refusals completed, including worker-only green, stale or wrong identity, incomplete or
  duplicate phases and assignment, and missing or unassigned native children.
- The protected product trace independently confirms all 30 discovered, collected and dispatched IDs, with no extra IDs or
  missing outcomes. The test driver exited 1 and DTrace exited 0 without a trace-loss diagnostic. Seven tests completed every
  required phase. Twenty-two fixtures stopped at `Ledger.initialize` with `Private ledger ancestry is unavailable`. One test body,
  `test_ordinary_checkout_mode_can_be_physically_identified`, reported `EPERM` resolving `/Users` in its ancestry. This is a
  result for the exact protected configuration. The ledger fixture error is less specific about which ancestor access failed.
- The intended success path required 74 direct `ssh-keygen` processes: key creation, signature and verification in the
  fixtures, with additional sign and verify pairs for four profile-revision cases. The trace records 22 successful key
  generations, fully attributed to setup. The other 52 expected sign and verify launches were absent when setup and the
  relevant bodies stopped. The integrated gate refused at native multiplicity and did not reach the post-run hosted custody
  check. [Final byte-exact evidence archive](https://github.com/kburson/aitm/actions/runs/44028499403/artifacts/14303613657).

## Retained hosted attempts

| Gate | GitHub run and attempt | Runner image | Result |
| --- | --- | --- | --- |
| Admission | [44019483743/1](https://github.com/kburson/aitm/actions/runs/44019483743/attempts/1) | `20261102.0473.1` | HOLD · worker boundary controls refused at -6 |
| Admission | [44019831612/1](https://github.com/kburson/aitm/actions/runs/44019831612/attempts/1) | `20261102.0473.1` | HOLD · missing, duplicate or unbound process trace record |
| Admission | [44020125444/1](https://github.com/kburson/aitm/actions/runs/44020125444/attempts/1) | `20261112.0504.1` | HOLD · python3.13 exited 1 |
| Admission | [44020525466/1](https://github.com/kburson/aitm/actions/runs/44020525466/attempts/1) | `20261102.0473.1` | PASS · Protected boundary, benign process and USDT, runtime bundle |
| Admission | [44024930299/1](https://github.com/kburson/aitm/actions/runs/44024930299/attempts/1) | `20261112.0504.1` | PASS · Protected boundary, benign process and USDT, runtime bundle |
| Integrated | [44023141637/1](https://github.com/kburson/aitm/actions/runs/44023141637/attempts/1) | `20261102.0473.1` | HOLD · PermissionError |
| Integrated | [44024727968/1](https://github.com/kburson/aitm/actions/runs/44024727968/attempts/1) | `20261112.0504.1` | HOLD · authenticated runner image or toolchain drifted |
| Integrated | [44026166553/1](https://github.com/kburson/aitm/actions/runs/44026166553/attempts/1) | `20261102.0473.1` | HOLD · authenticated runner image or toolchain drifted |
| Integrated | [44026166553/2](https://github.com/kburson/aitm/actions/runs/44026166553/attempts/2) | `20261112.0504.1` | HOLD · positive observer calibration did not pass |
| Integrated | [44028499403/1](https://github.com/kburson/aitm/actions/runs/44028499403/attempts/1) | `20261112.0504.1` | HOLD · 30 dispatched, 7 passed, 23 failed, 22 of 74 direct children matched |

The live trials found and corrected sandbox startup, user-space probe registration, protected runtime installation,
runtime restore metadata and pytest discovery gaps. The hosted image rolled between allocations. The mismatch checks refused
before runtime loading, and a new authenticated admission and Opus-reviewed packet tied the final run to the newer image.
The individual receipts preserve which gates each run reached.
[Stage B packet](2026-11-16-368-hosted-preflight-packet.md) · [Restore retry](2026-11-16-368-hosted-restore-retry-packet.md) ·
[Image re-admission](2026-11-16-368-hosted-image-readmission-packet.md) · [Discovery retry](2026-11-16-368-hosted-discovery-retry-packet.md).

## Evidence custody and disposition

The executor authenticated the GitHub run, attempts, job, exact workflow head, tree and per-file source hashes, retained each
archive before retry, verified archive, receipt and export hashes, then independently parsed the raw trace, driver exits,
assignment, direct native lifecycle and outcomes. Phase counts, uncertainty and identity are in the paired machine receipt.
[Paired receipt](../attachments/2026-11-16-368-hosted-qualification-receipt.json) at SHA-256 `04685c0606acd541b69cb7e8ee5daffd8601d7325f9c1fae434cfcb5c41998bd`.

The final raw files from the controller export are retained in a trusted local cache at `/Users/kpburson/Library/Caches/aitm-368-hosted.MVxC2n1K/integrated-44028499403-a1/raw` for independent readback. The relevant byte-exact
streams are `scoped-product-dtrace.stdout.log`, `scoped-product.stdout.log`, `hosted-report-1.json` through
`hosted-report-3.json`, and the three `calibrate-*-dtrace.stdout.log` streams. The reparse is at `/Users/kpburson/Library/Caches/aitm-368-hosted.MVxC2n1K/integrated-44028499403-a1/reparsed.json`.
The headed source for the scoped workflow is [the exact hosted experiment branch](https://github.com/kburson/aitm/tree/d06b0e7f21a447cabbcd808364377a6736d16892).

The conservative recorded charge through the final hosted job is 1.444
hosted hours plus the prior measured local 0.708 admission hours, totaling 2.152 hours. It includes tool and review
waits during continuous work, and ends at the final hosted job completion before independent closeout review. The disposable
local guest remains shut down, with private retained evidence, and the hosted jobs used disposable runner VMs.

An observed assignment failure requires HOLD under the accepted plan. The current evidence leaves the protected local route,
a fully passing hosted assignment with all native observations and the final custody check, and resistance to unreviewed candidate
code unresolved. Keep #368 open as the verified native cause blocking #355.
