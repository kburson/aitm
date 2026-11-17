<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-dabe24b06b8f23586f5a2582c5d60b9b"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md"
artifact_commit: "7035ab5d25e0ce724d595a3abb7a55b1da51b0f2"
artifact_blob: "b39329afa80d4b5800b0e53ee84c3d76a68127b1"
artifact_digest: "sha256:14f2576466bf4362c969f2099762957f485aa82495ae90b92d52cafd266fca41"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:798081e6024e566a3c838afa796a5d1589eec2b43d480ae37902c4d6555493c0"
  identity_source: "runtime"
started_at: "2026-11-17T05:52:31.375Z"
submitted_at: "2026-11-17T06:01:51.403Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised packet (blob `b39329a`, digest `sha256:14f25764…`, commit `7035ab5`) against:

- my turn-1 response and the author's turn-1 response;
- the new attachment `.aitm/stories/003/368/attachments/2026-11-16-368-protected-pytest-check.json`, read in full, including the embedded `driver_source`;
- the held worktree `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk`, read as working-tree files. The ref `refs/heads/codex/368-hosted-qualification` now holds `d06b0e7f21a447cabbcd808364377a6736d16892`, the head the revised packet authorizes. I read:
  - `admission.py`: the new `boundary_profile` (lines 131–148) and `prepare_boundary` (lines 151–257);
  - `qualification.c`: `check` (lines 60–89);
  - `test_integrated.py`: lines 1–100, including the new `BoundaryProfileTest`;
  - `calibration.py`.

**Turn-1 required change 1 is resolved.** The new attachment contains everything I asked for:

- **Profile binding.** It records both byte-exact profile texts and their SHA-256 values (`09fbd4b8…` revised, `87ff4fd5…` original), plus the substituted `ROOT`, `STAGED`, `SCRATCH`, `INPUTS` and `EXECUTABLES`. The embedded driver calls `admission.boundary_profile(public_inputs, executables)` after rebinding the module's `ROOT`/`STAGED`/`SCRATCH` globals. `prepare_boundary` now writes `boundary_profile(public_inputs, admitted_executables)` (`admission.py:197`), so the local and hosted profiles come from one generator. The two recorded texts differ only in the `file-read-metadata` literal line. Apart from path substitutions, the revised text has the same rule set as the Stage B shape I reviewed at turn 1.
- **Original-launcher failure.** The attachment records exit 2, errno 1, the denied path (the literal synthetic root), the pathlib leaf `pathlib/_local.py:515` in `stat`, and the last pytest frame `_pytest/config/__init__.py:454` in `_get_directory`. The driver asserts the `PermissionError` message on the root, not on a child path. The hosted record shows the same leaf, errno and literal root, and says plainly that the hosted traceback omits the pytest frame. That is the honest answer to the frame-match question, and the leaf/path/errno match is enough to identify the same mechanism.
- **Revised collection.** It records the exact option vector (`-p no:cacheprovider --rootdir <source> -c <source>/packages/aitm-usage/pyproject.toml --confcutdir <source>`), exit 0, the raw stdout and the two exact node IDs. The driver asserts that the IDs are the first two lines of stdout.
- **Driver.** The full source is embedded with its SHA-256, so it can now be reviewed.

**The turn-1 optional suggestions were taken, and they are correct in the source:**

- **Live child-metadata denial (suggestion 1).** `qualification.c:83–85` now requires `stat(argv[4])` (the root-owned `ROOT/outside` marker) to fail with `EACCES`/`EPERM`, else exit 80. `prepare_boundary` (`admission.py:248–253`) requires all three lines in order and records `root_child_metadata_denied`. A `subpath` grant would make this `stat` succeed, so the live control now tells a `literal` grant apart from a `subpath` one, which turn 1 noted the listing check could not do. The local Python control in the driver shows the same three outcomes under the revised profile (`protection_stdout`).
- **Offline policy test (suggestion 2).** `BoundaryProfileTest` asserts that the Stage A shape has no metadata grant. It also asserts that the Stage B shape has exactly one, `(allow file-read-metadata (literal "<ROOT>"))`. Twelve tests is consistent with eleven plus this one.
- **Local execution-phase run (suggestion 3).** The three synthetic calibration cases ran under the revised profile with the exact flags, `--basetemp` under scratch and `--maxfail=1`, and returned 0/1/1. The positive case runs `/usr/bin/ssh-keygen` with `check=True` and checks `owner.pub` under `tmp_path`. A passing result therefore shows the allowed native exec, the scratch write and the `tmp_path` path all work under the profile. The "failure-with-sibling" case collects both tests and stops after `test_failure`, which covers the hosted `calibrate-missing` shape. The packet correctly says that these runs establish nothing about DTrace outcomes, which the hosted gate must still prove.

`integrated.py` keeps blob `f0742ae6…` (the launcher I reviewed at turn 1), and its SHA-256 matches the turn-1 table.

One defect remains, in the authorization section itself (Finding 1). It is a stale-value problem, not a design problem, but it sits where exactness matters most.

Limits of this review:

- I did not run Git, compute SHA-256 or blob IDs, query GitHub, or run tests. I did not verify tree `618e81e5…`, the four blob IDs or SHA-256 values, the attachment's SHA-256 `bd0b7a61…`, or that `driver_sha256` matches `driver_source`.
- I did not see the launcher options at the accepted head `ffe77e3e…`. My statement that the driver's "original" options (`-p no:cacheprovider --rootdir <source>`) match the hosted original launcher comes from the packet.
- I did not see the hosted artifact `14302419973`. The `hosted_error` record comes from the packet and attachment.

## Findings

1. **The "Exact authorization" section still names the round-1 head in its delta command, and the charge was not updated.**
   - The packet now authorizes head `d06b0e7f…` with four changed paths. The reader instruction, however, is still `git … diff ffe77e3e… 3b603c6aa1c60b3dec895237beb2d3120a6914cf -- .github/spikes/368`. A reviewer or operator who follows it would see the round-1 delta: three paths, `admission.py` before the `boundary_profile` refactor, `qualification.c` without the child-metadata check, and no `test_integrated.py`. That is not the delta the table binds. The `3b603c6a…` head is no longer referenced anywhere else in the packet.
   - "The conservative combined charge at this submission is 1.921 agent-hours" is unchanged from the turn-1 submission, even though this revision added the factored generator, a new probe control, a test and a substantially longer local reproduction. Earlier packets in this series updated the charge at each submission. If the figure really is unchanged, the packet should say so; otherwise it is stale.

## Required changes

1. In "Exact authorization":
   - change the delta command to `git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff ffe77e3e2d8f5eac625add23b37c30f40025b4ec d06b0e7f21a447cabbcd808364377a6736d16892 -- .github/spikes/368`;
   - update the conservative combined charge to the value at this submission, or state explicitly that it is unchanged.

   No other change is required. I expect to accept once these two values are corrected and nothing else in the packet changes.

## Optional suggestions

1. The attachment's `code_source` sentence says that `prepare_boundary` delegates to `boundary_profile`. Consider also stating there, or in the packet, that the hosted launcher options at `ffe77e3e…` were exactly `-p no:cacheprovider --rootdir <PRODUCT>`, without `-c` or `--confcutdir`. The driver's "original" case reproduces that shape, and a reader without the old blob cannot confirm it.

## Decision

revisions-requested
