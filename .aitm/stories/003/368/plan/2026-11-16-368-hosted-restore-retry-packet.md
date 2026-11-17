# #368 hosted Stage B restore retry

Review the exact restoration change before retrying the [accepted Stage B packet](2026-11-16-368-hosted-preflight-packet.md).
The first [hosted Stage B attempt](https://github.com/kburson/aitm/actions/runs/44023141637/attempts/1) verified the live
worker boundary, denied a same-named scratch executable and observed the benign independent process and USDT records.
It returned HOLD at runtime import with a generic `PermissionError`. Zero product tests ran.
The authenticated [artifact](https://github.com/kburson/aitm/actions/runs/44023141637/artifacts/14301926805) remains available.

A local filesystem-only replay of the exact authenticated archive reproduced a separate concrete defect in the restore code.
All ten symlinks were created at mode `0700` under the controller umask. The admitted manifest requires `0755`.
This replay used the ordinary account and never executed the downloaded interpreter.
It did not conclusively attribute the hosted `PermissionError` to the mode mismatch.

The corrected restore uses Darwin's lchmod on symlinks to restore the manifest mode on the link itself.
Regular files and directories retain the previous mode handling. The normal job still requires the exact
manifest, symlink targets, protected ownership, interpreter digest and Mach-O probe table before calibration.
The local dry restore matched all 8,973 entries and the probe table digest after the change, then stopped before native interpreter execution.
Nine offline tests passed. An OS failure now includes a sanitized errno and source frame so the next HOLD can be diagnosed.

## Exact retry authority

Workflow head `1f036b387b52c91bc0475de46e6b9430f45ff720` and tree `a2180efee3a0a7015a859d68e56708d43ade7dd4`, based on accepted Stage B head `58ebe2c2845c87411fab33e8a15d42fc81f077e8`.
The only updated path is `.github/spikes/368/integrated.py`, blob `837402c5521cee307ea95938f5e65231c0967cb7` and SHA-256 `3e4bf1a64da3fd1e6f25c6d397f4644c50dd7b1314df139d9a75d087e33d6087`.
The original ten-path allowlist, Stage A runtime, packet, assignment, reviewer-approved worker and observer policy,
workflow and public evidence allowlist remain the same. Read the exact delta with
`git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff 58ebe2c2845c87411fab33e8a15d42fc81f077e8 1f036b387b52c91bc0475de46e6b9430f45ff720 -- .github/spikes/368/integrated.py`.

The retry uses a fresh hosted Stage B push. It must repeat the live admission controls and calibration.
Local execution, strict candidate-code resistance and the dependent #355 requirements stay unqualified.
The conservative combined admission and preflight charge is 1.436 agent-hours at packet submission.
