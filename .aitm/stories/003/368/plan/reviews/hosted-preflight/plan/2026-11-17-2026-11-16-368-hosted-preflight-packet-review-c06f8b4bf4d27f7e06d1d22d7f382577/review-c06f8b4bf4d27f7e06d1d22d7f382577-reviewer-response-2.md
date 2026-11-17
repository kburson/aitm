<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c06f8b4bf4d27f7e06d1d22d7f382577"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-preflight-packet.md"
artifact_commit: "67ef733fb684869cc999bb1c7630d46d07ef3216"
artifact_blob: "3fd20ff0d1a5b475ed849a7a27da901490e17a36"
artifact_digest: "sha256:84cb2afd4378937b42d789f46e775419d44a186bce96a732cd14eb2b6313493b"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:102ec2fea75b4ebd4fe2a760a8281449fd5629f4d85c1c51dc4bdf17be118590"
  identity_source: "runtime"
started_at: "2026-11-17T05:06:03.516Z"
submitted_at: "2026-11-17T05:16:39.055Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised packet (blob `3fd20ff`, digest `sha256:84cb2afd…`) against the author's turn-1 response. The packet now names workflow head `58ebe2c…` and tree `1d1327b…`. I read the revised Stage B sources as working-tree files in the held worktree:

- `.github/spikes/368/` files: `admission.py`, `integrated.py`, `qualification.c` and the new `test_integrated.py`

The two files the author reported unchanged (`stage-b-inputs.json` and the workflow) keep their blob IDs in the revised table. Every turn-1 item is resolved.

**Turn-1 Required change 1, the exec identity.** The author took option (a), the kernel-enforced binding, and also narrowed the packet text:

- `prepare_boundary` now accepts `admitted_executables`. Stage B passes `EXECUTABLES`: `/usr/bin/ssh-keygen`, `installed/bin/python3.13` and `observed-venv/bin/python`, plus the staged probe. The worker profile adds `(deny process-exec*)` and then `(allow process-exec* (literal …) …)` for exactly those paths.
- Before any trace or product launch, a worker-owned `0700` copy of the benign probe is installed as `<scratch>/ssh-keygen`. The probe's new `refuse-exec` mode must fail `execl` with `EACCES` or `EPERM`, and the output must be exactly `DENY unadmitted executable\n`. Any other result is a HOLD. That includes a successful exec, which prints nothing and returns 0.
- Process execution is now confined by the sandbox. The only admitted binary whose short name is `ssh-keygen` is `/usr/bin/ssh-keygen`, whose digest is checked at job start. Together with the kernel's exec short name, this binds each observed child's image without relying on the cooperative event.
- The packet now says that the kernel supplies create, exec short name, exit status and exit reason. It says the allowed `observed_init` frame supplies path and argv, and that "the argv channel remains cooperative in-process evidence." That matches the code.
- Positive paths are still exercised before the product run. The Stage B `trace_attempt` execs the probe, and positive calibration runs the venv Python and `/usr/bin/ssh-keygen`.

**Turn-1 optional suggestions, all adopted:**

1. **One replay contract.** The new `replay_report` gives all four trusted replays the same scrubbed `PATH`, `HOME` and `LC_ALL`, the same exit-code check and the same empty-stderr check. The post-run replay goes through it with expected exit 0 and is compared byte for byte with `hosted-report-1.json`.
2. **Always publish a receipt.** `main` now catches `Exception`, records `failure_type` and still runs `publish`.
3. **Offline tests.** `test_integrated.py` adds six tests: scoped generate paths (relative, `/tmp`, `..` and wrong suffix are refused), the exact signing namespace, the verify principal and sibling-path checks, direct-child lifecycle refusals (status, reason, double exec, wrong image, wrong phase), failed setup or call still entering teardown, and the observer anchor count (0 or 2 anchors refused). `FILES` now includes `test_integrated.py`, so `verify_job`'s exact-diff check covers ten paths. That matches the ten-row table. The unchanged workflow's `unittest discover` picks up both test files, for nine tests in total.
4. **Phase mapping and direct children.** `read_native` now maps `setup-failed` and `call-failed` to `teardown`. The packet scopes the 74 launches and the tracing claim to direct children of the pytest process.
5. **Derivation and budget.** The packet states that the enumeration comes from static source review, which matches my turn-1 trace of the fixture and the `revise` callers. It records 1.317 cumulative agent-hours, inside the 3.75-hour gate.
6. **Image drift.** The packet states that drift from the pinned image is a re-admission HOLD.

The rest of the Stage B harness is unchanged from what I accepted in substance at turn 1: Stage A runtime admission, the product manifest, scope inputs, calibration, intake refusals and post-run custody. The Stage A runtime does not depend on the changed `admission.py` or `qualification.c` bytes. Stage B rebuilds the probe and re-runs the boundary and capability checks with the revised code. The Stage A receipt remains bound to its own head `af8f653`.

Limits of this review, as at turn 1:

- I did not run Git, compute SHA-256 or blob IDs, or query GitHub.
- I read the held worktree's working files, not `git show 58ebe2c…:<path>`. I did not verify the source table, or that the working files equal the committed bytes.
- I did not run the nine offline tests or the author's local sandbox probe. I relied on the author's report that both passed.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. The macOS sandbox may check `process-exec` against either the venv's `bin/python` path or its resolved interpreter path. Both literals are allowlisted, so either works. If any intermediate venv symlink is evaluated, positive calibration fails closed before the product run, so this costs at most a HOLD. Stating that in the Stage B receipt or findings would make such a HOLD quick to diagnose.

## Decision

accepted
