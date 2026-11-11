# Independent post-CI source review for #188

**Verdict** PASS. No material source findings remain for the candidate below. Signed by Codex, independent source reviewer, on 2026-11-11 UTC.

## Exact candidate and proof

- Repository `kburson/aitm`, PR #213 targeting `trunk`. [Pull request](https://github.com/kburson/aitm/pull/213)
- Base `f7646bc4da35173e9b0e468e4810b4e9265b0f47`, head `f557062c55dafb02990b02480d88213163eac094`, tree `0df8ed8cfebd9b597d20e6c4851f060cfada0618`.
- Tested merge `24239fc92359801b53d157361f8510cc0a29dd3a`. The signed evidence verifier reported PASS for run `42957581045` attempt `1`, artifact `13828600206`, subject digest `1c2fce3a3da29f0a346db06659062c8125bbd7b62ab23302b36d6de5066001f7`, and six jobs `aitm-ci`, `collect-evidence`, `file-checks`, `python`, `python-base`, and `quality`. The local head and tree matched the signed record. The tested merge identity comes from the signed record. [Hosted evidence run](https://github.com/kburson/aitm/actions/runs/42957581045/attempts/1)
- The clean checkout and base-to-head diff show only `tools/story_dashboard/timing.py` and `tools/story_dashboard/tests/test_timing.py`. `git diff --check` passed. The accepted #181 design and #188 A03 pickup govern the scope.

## Findings and verification

- Turn work includes admitted tool time and applies owner-wait and idle exclusions within the evidenced logical actor and direct story scope. An ambiguous phase exclusion leaves a partial result. A wait assigned to another story leaves independently evidenced work available. Pending wait needs a positive observation checkpoint. A wholly held work conflict leaves independent wait and elapsed coverage intact.
- Both input orders for simultaneous starts of distinct attempts yield Unknown implementation elapsed and age without an authoritative Develop selecting the attempt, and preserve both conflicting start references. With authoritative Develop, the matching Done yields complete elapsed for the selected attempt. Conflicting same-attempt boundaries remain Unknown. Reset to Plan prevents stale implementation age. Backlog and Ready for Planning can display evidenced all-phase age. Calibration requires complete Actual and matching estimate phase and roles.
- Independently ran the 19 focused timing tests and the 48-test dashboard suite on the exact head. Both passed. The exact-candidate log also records passing Ruff checks. The historical parity test and retained candidate proof preserve all ten legacy direct and inclusive values and the seed watermark across the historical and current planning pins. #111 retains 774,000 ms implementation elapsed and Unknown all-phase elapsed. The measured legacy values retain partial coverage.

This is a signed off-platform source review. Native GitHub review is absent.
