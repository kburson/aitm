# #368 queue-inclusive hosted qualification packet

The prior attempt stayed queued through its deadline after 11 minutes and 41 seconds. The HOLD recorded
zero allocated runners, job steps and product tests. The owner authorized a new admission window in the #368
Codex conversation before this packet's opening at `2026-11-17T13:03:02Z`:

> Go ahead and authorize a new admission window for #368 that allows for macOS runner queue time. Get the fresh packet reviewed by Opus 5.5/high, then rerun the full qualification. Keep #355 blocked until its trust requirements are met.

This packet gives review, GitHub queue time and preflight 105 minutes from opening through
`2026-11-17T14:48:02Z`. [Prior HOLD](2026-11-17-368-hosted-ancestry-run-findings.md) ·
[Accepted ancestry plan](2026-11-17-368-hosted-ancestry-implementation-plan.md) ·
[Previously reviewed execution packet](2026-11-17-368-hosted-ancestry-execution-packet.md).

## Exact time and authority

The owner's new admission authorization and Opus 5.5/high acceptance of this revised packet together replace the
exhausted 2.5-hour admission/preflight stop and the 3.75-hour exact-packet ceiling from the previous attempt for
this run. The fresh absolute dispatch deadline, including an exact-head retry, replaces the expired
`2026-11-17T12:52:24Z` cutoff. The unchanged overall limit is six cumulative hours.

| Limit effective for this attempt | Headroom at opening | Headroom at dispatch expiry |
| --- | ---: | ---: |
| New admission, review and preflight window (105 minutes) | 105 min | 0 min |
| New exact-packet ceiling (5.960 cumulative h) | 2.659 h | 0.909 h |
| Overall ceiling (6.000 cumulative h) | 2.699 h | 0.949 h |

Charge the conservative 3.301 cumulative hours at opening and all elapsed time thereafter, including queue, evidence
work and review. The charge at dispatch expiry is 5.051 h. Reserve a full 22 minutes for the hosted job, 12 minutes
for authenticated download and reparse, and 20 minutes for findings review and publication. The 54-minute tail
brings the worst planned charge to 5.951 h and gives absolute stops at `15:42:34Z` for this packet and
`15:44:58Z` overall. At the first applicable stop, cease active qualification or unfinished closeout, retain
authenticated evidence, and record a bounded HOLD. If review still runs at that stop, preserve its receipt and
report the pending review with the HOLD. No new execution or review starts after the stop.

Require Opus 5.5/high acceptance before push. The dispatch guard runs after the boundary and trace checks, runtime
import, report replays and calibration. It reads the runner's UTC decision and refuses product dispatch after the
bound instant or on missing or malformed input. At `14:48:02Z`, if the run is still queued without a runner,
request cancellation and retain the authenticated run and job observations with the cancellation time. If a job
has started, collect its protected decision and terminal evidence within the closeout reserve.

Workflow head `56428a6ccc7c525b374f087dc2aa0c06e4cc7eac`, tree `6f61e6d1a8a103d894c3607751cde3f42ca9abcd` and product base `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`. The only change from reviewed head
`f5f1cf8f48804c364375042ba32426a3125b9749` is the deadline string in `.github/spikes/368/stage-b-inputs.json`, blob `4e86f65edb976fc1179dcd9b511bd7a7f65d1b71` and SHA-256
`2741a763afe3434d232a05aab5f606242a1cacd02550539c7510a2264072bca0`. Both packets compared equal after replacing that one string. The other ancestry keys keep the prior
plan identity and acceptance for provenance. The dispatch guard in `integrated.py:327-336` reads only the deadline. The ten-path dedicated branch scope still applies.
Verify with `git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff f5f1cf8f48804c364375042ba32426a3125b9749 56428a6ccc7c525b374f087dc2aa0c06e4cc7eac -- .github/spikes/368/stage-b-inputs.json`. All 13 harness unit tests passed.

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
