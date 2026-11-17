# #368 hosted Stage B restore retry

Review the exact restoration change before retrying the [accepted Stage B packet](2026-11-16-368-hosted-preflight-packet.md).
The first [hosted Stage B attempt](https://github.com/kburson/aitm/actions/runs/44023141637/attempts/1) verified the live
worker boundary, denied a same-named scratch executable and observed the benign independent process and USDT records.
The receipt reported `gate=runtime-install`, `failure_type=PermissionError` and `failure=PermissionError`. The worker boundary, provider inventory and early trace streams are present. The installed probe-table and pytest-identity streams are absent. Zero product tests ran.
The authenticated [artifact](https://github.com/kburson/aitm/actions/runs/44023141637/artifacts/14301926805) remains available.

A local filesystem-only replay of the exact authenticated archive reproduced a separate concrete defect in the restore code.
All ten symlinks were created at mode `0700` under the controller umask. The admitted manifest requires `0755`.
This replay used the ordinary account and never executed the downloaded interpreter.
The authenticated manifest has 8,570 files and 393 directories. Zero files lack other-read access and zero directories lack other-read/traverse access. This rules out missing ordinary-file or directory mode bits in the manifest. The remaining identified hypothesis is that the controller could not follow a root-owned `0700` symlink. The hosted retry tests it directly.

The corrected restore uses Darwin's lchmod on symlinks to restore the manifest mode on the link itself.
Regular files and directories retain the previous mode handling. The normal job still requires the exact
manifest, symlink targets, protected ownership, interpreter digest and Mach-O probe table before calibration.
The local dry restore extracted and copied the exact tree with real ditto under the ordinary account. All 8,973 entries and the probe table digest matched. The driver stopped before executing the interpreter. The hosted root chown remained outside this local check. [Dry restore receipt](../attachments/2026-11-16-368-hosted-dry-restore.json) at SHA-256 `b10bd2365341a05e6a59ee0c21a5b6580799d19e5b2adf33cc479d136c33b5f9`. Eleven offline tests passed, including private-umask symlink modes and a simulated permission failure. A future OS failure reports errno, the innermost spike and leaf frames, and a path relative to the controlled runtime or private evidence directory when available.

## Exact retry authority

Workflow head `3a0859d163681562b0aeb96c3330846224bb8cc6` and tree `d6144f2d9d57927218653ffd93b6a1ce95cdf4bd`, based on accepted Stage B head `58ebe2c2845c87411fab33e8a15d42fc81f077e8`.
The exact retry modifies two files in the existing ten-path allowlist.

| Path | Blob | SHA-256 |
| --- | --- | --- |
| `.github/spikes/368/integrated.py` | `bae337ea4881666824d450786d74d4474e8e3cbf` | `ac40cdaf446770c124f6065fd784abd89e8c64350335d08956afe88f7393ae74` |
| `.github/spikes/368/test_integrated.py` | `dcff8e45ae9ccc2a471497e63e08914192423fd8` | `b1b02de4b574759dfc893f916112c64e7df3142293f19eca858638f91bcda624` |

The Stage A runtime, packet, assignment, worker and observer policy, workflow and evidence allowlist are unchanged.
Read the exact delta with `git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff 58ebe2c2845c87411fab33e8a15d42fc81f077e8 3a0859d163681562b0aeb96c3330846224bb8cc6 -- .github/spikes/368`.

The retry uses a fresh hosted Stage B push. It must repeat the live admission controls and calibration.
Local execution, strict candidate-code resistance and the dependent #355 requirements stay unqualified.
The conservative combined admission and preflight charge is 1.436 agent-hours at packet submission.
