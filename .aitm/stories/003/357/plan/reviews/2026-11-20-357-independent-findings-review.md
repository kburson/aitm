# #357 independent acceptance review

**Decision — PASS**

**Date — 2026-11-20 UTC**

**Signed — Codex /root/review357, independent acceptance reviewer**


I accept the classification findings and evidence at planning commit `0898a270d0a1daf1d5f2afaf5e9b15649fe23b33`, tree `14ab7cb406287c1325fbedb78e5900f8faed23f6`, against the story and delivery plan acceptance criteria. I reviewed the immutable Git archive and checked that the candidate diff is confined to story #357 and has no whitespace errors.

- Findings SHA-256 — `2d265ab16b2f9aa66ab3c161af0d18beac1146f3fc111b0c4ed90720be20de81`.
- Evidence manifest SHA-256 — `1cbb04230b7fcbb34b8b1677d6a447a1bf33ed4efd80d5faaf71395e80514607`. All six hashes in the manifest match the archived bytes.
- Source — protected trunk commit `9843874bd00ffa1255b3595987106d5af51dceb3`, tree `b8ca66991842e6b360cf09f0e36b25c693d48390`. The research checkout matched the source tree and had no tracked changes. The tracked test modules fall under the five documented roots. The extra filename matched by the Git test glob, `tools/ci/pytest_evidence.py`, is the receipt plugin and contains no test definitions.

I separately ran two locked collections of every profile with the stock receipt plugin. Both trials reproduced the published ordered node IDs on macOS arm64/APFS and Ubuntu 24.04.5 Docker arm64 from a fresh pinned source archive. Both used uv 0.10.6, CPython 3.13.9 and pytest 9.2.0. Each native invocation used the documented import path for the shared watcher helpers. The exact counts were 2,314 and 2,319, with two macOS-only and seven Ubuntu-only IDs. The register equals the 2,321-ID union with zero duplicates, omissions or extras and every row uses its most specific applicable witness. I reproduced the focused probe outcomes of 39 passed and two procfs-related setup skips on macOS, and 31 passed and 15 Darwin-native setup skips on Ubuntu. These probes establish the stated local host observations. Hosted runner behavior and complete suite outcomes remain unmeasured.

I traced representative mixed boundaries in the pinned source. The Grok pricing arithmetic is unit and the real packaged-rate export checks are local integration. In the simulated Darwin executable-identity family, the invalid length and truncated cases return before filesystem inspection. The changed-path and changed-image cases extract real file identities and are local integration. The Linux procfs cases exercise real external process identity. The publication module distinguishes real no-replace/exchange behavior from injected errno cases that observe preserved fixture state. The snapshot FIFO case exercises a native POSIX object, while its Git/worktree siblings retain their local integration witness.

I recomputed the categories and threshold outcomes from the published phase samples. There are 483 fast unit, zero slow unit, 1,570 local integration, 268 systems integration and zero exceptions. All 483 unit IDs have three passed phase triplets. The median of per-ID medians is 610 µs, nearest-rank p95 is 6,605 µs and the maximum median is 90,533 µs. The two single-observation threshold crossings are identified correctly. This is a serial macOS timing calibration with uncontrolled OS caches. The historical #285 audit reconciles exactly with 1,736 shared IDs, 585 current-only IDs, four historical-only IDs and all 42 original families retained. The manifest's historical removed IDs, new and changed family paths and changed fixture paths also matched the audit and pinned Git diff.

No blocking finding. The accepted register can feed #358 and #359 under their existing scope. Collection and probe receipts from this review are in `review-scratch/macos` and `review-scratch/ubuntu` beside this decision.
