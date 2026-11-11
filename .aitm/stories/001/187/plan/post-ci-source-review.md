# #187 independent source review

**Verdict — accepted.** Signed 2026-11-10 America/Chicago (2026-11-11 UTC) by Codex `/root/pickup186`, a separate agent from the implementer. Off-platform review. Native GitHub approval absent. No actionable blockers for this source revision.

PR #208 targets `trunk` at base `1282538954dc5a7e7f7b27da4e3ab096892e3add`. Reviewed source head `27abd178ce3e0b1e076e2c94c3a4a3f863179254`. Reviewed source and hosted tested tree `f62fbd48047f73baf52f65f86b33d475328b2f1f`. Hosted tested merge `ecf070613b90ad20f8a833134477bbd615065150`. [PR #208](https://github.com/kburson/aitm/pull/208)

Reviewed `tools/story_dashboard/attribution.py` and `tools/story_dashboard/tests/test_attribution.py`, the complete diff against the declared base, against the accepted 25-line pickup packet, SHA-256 `bd55fc1bb49d54d311230f7e0d48ecb7389f82c1709e5c18744c8052b6d06de1`, and the #181 A02 contract. The candidate normalizes direct observations, resolves replay and overlapping attribution, preserves coverage and provenance, and admits the digest-pinned legacy observations and separate readback values. It retains raw tool evidence for A03 to qualify and pending wait evidence with the recorded checkpoint and replay chronology.

## Findings resolved

1. The missing-evidence handler at `attribution.py:433` now reports a scoped gap for a boundary with both endpoints missing. A supported one-ended boundary stays available. Verified by the regression at `tests/test_attribution.py:266`.
2. The v1 resolver at `attribution.py:318` now holds related observations by story and stable project-scoped identity. A second receipt cannot revive a same-scope supersession-held observation. The regression at `tests/test_attribution.py:291` confirms unrelated observations in the replay receipt and foreign-story evidence remain available.

## Verification

- Confirmed the clean checkout matches the reviewed head and tree, the declared base is an ancestor, and `git diff --check` passes. Independently ran all 21 dashboard tests, including the 10 attribution tests and both remediation regressions. The exact candidate log also records Ruff check and format passing.
- Independently resolved the planning pins `17761cc1928fd916cf32a9c078d4a742bfcb32b8` and `b9210e349ad680b32b05b58a151bdbb992b9cbe0`. Both have 10 legacy readback entries and 114 retained direct intervals, with exact per-story millisecond parity and 2,186,725 ms of direct observed work for #111. Both preserve inherited planning input gaps. The earlier independent reference check passed 500 deterministic cases for the interval endpoint sweep.
- The delivered trunk verifier returned pass for canonical run 42946905299 attempt 1. PR, head, base, tested merge and tree match this review. The signed proof covers `python-base`, `python`, `quality`, `file-checks`, `collect-evidence` and `aitm-ci`. Evidence artifact `13824055031` has archive SHA-256 `afce44dd1e65c8847bd2315a989cfcae87e7d105e10d8853c2cc772236431d62`. [Hosted run](https://github.com/kburson/aitm/actions/runs/42946905299/attempts/1)
