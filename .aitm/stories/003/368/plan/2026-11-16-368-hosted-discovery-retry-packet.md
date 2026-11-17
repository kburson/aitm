# #368 hosted discovery retry

The [re-admitted integrated job](https://github.com/kburson/aitm/actions/runs/44026166553/attempts/2) verified the
fresh hosted boundary, kernel process facts, benign USDT, protected runtime restore and all three trusted report replays.
The two scoped reports matched and contained all 30 exact #344 IDs. The extra path produced exit 2 and `unsupported-change`.
The protected installed pytest readback was 9.2.0. The runtime restore fix passed in the hosted job.

Positive synthetic calibration then returned HOLD before dispatch. The controller trace contains only
`collection-end 0` and `dispatch-refused inventory-mismatch` for the attached Python PID. Driver exit was 4 and DTrace exit was 0.
Pytest's driver reports a sandbox `PermissionError` while statting the known admission root
`/Users/Shared/aitm368-hosted`. The expected calibration fixture was absent from collection and no product tests ran.
The authenticated [artifact 14302419973](https://github.com/kburson/aitm/actions/runs/44026166553/artifacts/14302419973)
preserves the original receipt and raw driver, observer, platform, runtime and report streams.

The revised launcher supplies the already admitted product `pyproject.toml` as the explicit config and sets
the admitted source tree as both pytest root and conftest cutoff. Pytest 9.2.0 also stats the admission root itself.
The restricted worker policy now allows exactly `file-read-metadata` on that literal directory.
It still denies data reads of that directory, recursive discovery of its contents, writes and reads of the protected controls and evidence.
The synthetic boundary probe requires the allowed stat, denied real directory listing, and denied stat of an unadmitted child under the same root before calibration.
The existing same-named executable, denied collector device, network, checkout, control, credential and write cases still run.

The stronger local reproduction called the same `boundary_profile` generator used by `prepare_boundary` with
Stage B-shaped arguments and substituted only the synthetic admission, staged, scratch, source, trusted Python and venv paths.
It preserved the exact baseline and revised policy texts and digests. With the original options and profile, pytest returned
exit 2 and errno 1 on the literal synthetic admission root. Its final pytest frame was `_pytest/config/__init__.py:454` in
`_get_directory`. The hosted trace used shorter output, so this pytest frame is unavailable there. The hosted and local traces
both show `pathlib/_local.py:515` in `stat`, errno 1, and the corresponding literal admission root.

Under the revised profile with the same config, root and conftest flags, collection returned exit 0 with
`calibration/test_probe.py::test_failure` and `calibration/test_probe.py::test_success`. The sandbox also denied directory listing
and stat of the unadmitted child. Three local synthetic calibration runs returned expected exit codes 0, 1 and 1, including the
stock keygen launch on success and an omitted sibling under maxfail. These local runs exercised the worker only. The hosted
job still must establish independent DTrace outcomes. Twelve offline tests passed, including the literal policy assertion.
[Full local dry-check receipt and driver](../attachments/2026-11-16-368-protected-pytest-check.json) at SHA-256 `bd0b7a612ca299619b3b7608bb3d81dd10543a4d25ee1a52a34904603b1b67f9`.

## Exact authorization

Workflow head `d06b0e7f21a447cabbcd808364377a6736d16892` and tree `618e81e5c8981b54694ac2e97e5ee8eb8d28caf3`, replacing accepted head `ffe77e3e2d8f5eac625add23b37c30f40025b4ec`.
The exact delta changes four paths within the existing ten-path allowlist.

| Path | Git blob | SHA-256 |
| --- | --- | --- |
| `.github/spikes/368/admission.py` | `f0d168d5a4dd365e16f9c1f6f0313ae511c56ba7` | `9b1cea56e7605ddc297ed94abd1c6dec64ea48df7c0a835bd5ead25086798343` |
| `.github/spikes/368/integrated.py` | `f0742ae6b85ade9a9bb78a3471cc9486701835b1` | `86e1b2453e3f8db754e2b4ab4ea46fe5caddc48ef272a445a4e837f3558dc2df` |
| `.github/spikes/368/qualification.c` | `e4a1f9939b1797e5cff91076c69b74bd2746fa1b` | `f31a878d331cc001311fac102954a4c0c918409c6b743b2cbfbceae74082346e` |
| `.github/spikes/368/test_integrated.py` | `cd5c849c7b4a14a8ef708703d56f3edfea1840bc` | `b8e753626340fd06dc33e3788d5e5cd934d3f9dc49b167770124fb35224b302b` |

The refreshed Stage A image, archive digest, scope records, product tree and assignment are the same. The workload and controls
use the same independent observer. Read the exact delta from the held worktree using
`git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff ffe77e3e2d8f5eac625add23b37c30f40025b4ec d06b0e7f21a447cabbcd808364377a6736d16892 -- .github/spikes/368`.
The conservative combined charge at this submission is 2.107 agent-hours.
A fresh hosted job must recheck the admitted image, new live boundary controls, runtime, replays and calibration before product execution.
#355 remains blocked.
