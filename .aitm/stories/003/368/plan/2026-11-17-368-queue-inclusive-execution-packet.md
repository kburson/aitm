# #368 queue-inclusive hosted qualification packet

The owner authorized a new admission window after the preceding attempt stayed queued for 11 minutes and 41 seconds through its
deadline. The prior HOLD recorded zero allocated runners, job steps and product tests. This packet grants two hours from
`2026-11-17T13:03:02Z` to `2026-11-17T15:03:02Z`. Review and GitHub queue time count toward the window.
The allowance covers the existing 22-minute job timeout after allocation and leaves time for allocation, preflight and
normal recovery. [Prior HOLD](2026-11-17-368-hosted-ancestry-run-findings.md) ·
[Accepted ancestry plan](2026-11-17-368-hosted-ancestry-implementation-plan.md) ·
[Previously reviewed execution packet](2026-11-17-368-hosted-ancestry-execution-packet.md).

## Exact time and authority

The owner’s fresh authorization supersedes the expired `2026-11-17T12:52:24Z` admission deadline for this attempt.
The clock is absolute UTC, including an exact-head retry. The dispatch guard runs after the boundary and trace checks, runtime
import, report replays and calibration. It reads the runner’s UTC decision and refuses product dispatch after the bound instant
or on missing or malformed input. If the run is still queued at expiry, cancel it and retain the authenticated run and job
observations. If a job has started, collect its protected decision and terminal evidence. The two-hour allowance conservatively brings
cumulative work from 3.301 hours at opening to 5.301 hours at expiry against the six-hour overall cap.
The new allowance replaces the exhausted admission sub-budget for this attempt. Require Opus 5.5/high acceptance before push.

Workflow head `a3249493cb4216c184a1384112ef316011f060d1`, tree `8dfc90adec7672b4ce3acdf305e8c1b520402b24` and product base `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`. The only change from reviewed head
`f5f1cf8f48804c364375042ba32426a3125b9749` is the deadline string in `.github/spikes/368/stage-b-inputs.json`, blob `3c0e8d65896b09e093b43e1f2313c118fd1cfdf9` and SHA-256
`8cbbd48d51511ebf73540f4ccc262eab81798800fddd096bec9771000a0cdb2e`. Both packets compared equal after replacing that one string. The other ancestry keys keep the prior
plan identity and acceptance for provenance. The ten-path dedicated branch scope still applies.
Verify with `git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff f5f1cf8f48804c364375042ba32426a3125b9749 a3249493cb4216c184a1384112ef316011f060d1 -- .github/spikes/368/stage-b-inputs.json`. All 13 harness unit tests passed.

## Runtime and required result

GitHub authenticated successful Stage A run `44024930299/1` at `e38d67d0254c0bac77761a48561c7ee5ecad315e`. Artifact `14302787413`
is available and its SHA-256 `3841df4cfeca31523065b63d6b66ba72aec58aad4041e91854225d36564936ca` matches the retained archive and the packet. The snapshot still binds image
`20261112.0504.1`, the archive, manifest, interpreter, Mach-O probe table and native inputs. The prior packet verified all
8,973 archive entries and the link boundary. The job verifies the archive before extraction and the restored runtime before use.
An image mismatch produces HOLD before qualification. Preserve it before an exact-head retry under this window.
Any other runtime binding requires independent packet review before product dispatch. [Admitted archive](https://github.com/kburson/aitm/actions/runs/44024930299/artifacts/14302787413)

Run fresh separate-UID isolation, worker/controller ancestry and ACL readbacks, all EPERM denials, benign DTrace observation,
runtime restore, three report replays, synthetic calibration and the full 30-ID scoped product assignment. Require 30 independently
observed passes, all 74 exact direct native child lifecycles, zero trace loss, actual driver exit and post-run custody for a bounded
hosted PASS. Download and reparse authenticated raw evidence on any hosted outcome. Protected local execution, unreviewed
candidate-code resistance, broader candidate inventory and impact completeness remain outside the bounded proof.
Keep #368 open and #355 blocked until the remaining trust requirements have their approved disposition.
