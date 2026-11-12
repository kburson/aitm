# Wave 50 #143 formal independent SAR — round 1

Date: 2026-11-12

**Verdict: ACCEPTED. Ready to merge on the reviewed identities, subject to the existing delivery controls.** No blocking findings.

## Reviewer and independence

Signed: OpenAI Codex, independent review agent `/root/sar143`. The coordinator requested `gpt-6-astra` with inherited/default effort; the actual runtime model and effort identifiers are not exposed to this reviewer, so the requested configuration is not represented as independently attested runtime identity. The reviewer did not implement this change, delegate review, modify the implementation checkout, write to GitHub, change lifecycle state, or merge. Testing used a private exact-head Git archive export and a separate private environment.

The review followed the supplied requesting-code-review reviewer procedure. It read both changed files in full (1,204 added lines), the accepted design, implementation plan, JIT, refinement and T06 leaf, and the relevant T02–T05, pytest observer and outcome-validation contracts.

## Exact review binding

- Repository and PR: [kburson/aitm #265](https://github.com/kburson/aitm/pull/265), literal base branch `trunk`.
- Base: `0dfbcf0c4b346fe014674aae0775a82f40e3a9b8`.
- Candidate head: `717da4ce2540d4ba52f340cd3fe276fc43ccfb5b`.
- Tested synthetic merge: `31466f9127d4f9ac940bcc93df7ccf468a3b61db`.
- Reviewed source and tested merge tree: `2f5169c7e1129f0cdb089b9d52ffe776de6af782`.
- [CI run 43245371964, attempt 2](https://github.com/kburson/aitm/actions/runs/43245371964/attempts/2).
- [Review admission publication](https://github.com/kburson/aitm/commit/4fdf7aeb1e8a48af76bd447979677c0892ab18bd).

Read-only live GitHub calls independently confirmed the open, non-draft PR, literal base, exact head and synthetic merge. GitHub's Git commit endpoint independently confirmed the merge parents and tree; local Git independently confirmed the candidate tree. The live run endpoint confirmed attempt 2, the exact head, pull_request event, CI workflow and successful completion. All six current jobs were completed/success: python `131287208574`, file-checks `131287209237`, python-base `131287209245`, quality `131287209355`, collect-evidence `131292075891`, aitm-ci `131292208426`. Attempt 1 is retained historical evidence, not the accepted attempt.

The authenticated admission, owner disposition and [trusted verifier pass](https://github.com/kburson/aitm/blob/4fdf7aeb1e8a48af76bd447979677c0892ab18bd/.aitm/stories/001/143/plan/verifier-pass-717da4ce2540.json) agree on these identities, artifact `13957034970`, archive digest `sha256:ab8bdaa8825ce99eff50299778fa85ac9fe2900d100a5e49f2f62fa3cc632bf3` and subject digest `c367d53e544fecc05995d026d87e4d7c49a19769bd4bc7820d04aac0986b4f48`. This SAR checked the verifier result and live job identities; it did not rerun cryptographic attestation verification.

The supplied design, plan and JIT bytes were independently hashed and matched respectively `467f647b560118c51783313118b01854c8cecb4fc4d53083005a00411cdcbc96`, `5da21fa6b30418d58dd1d5cbf18f6b9b022552ed2d5f0b3c05e3331c6b027b63`, and `febd54ed163210198097dd69c825644b489a68e09fbbb3213cfbcadf800316ab`.

## Strengths and source assessment

The two-file scope matches the accepted leaf. [local.py](https://github.com/kburson/aitm/blob/717da4ce2540d4ba52f340cd3fe276fc43ccfb5b/tools/ci/tia/local.py) composes the existing snapshot, classification, graph and selection contracts without modifying hosted authority. Explicit base resolution is protected from option interpretation; fixed-base snapshot identities and raw-path hex accompany advisory output. Captured files, executable modes and contained relative links are verified before use and after collection/execution; new inputs and altered captured content invalidate observations. The separately copied observer is hash checked too.

Candidate inventory is independently established first, with exact snapshot policy/configuration/lock/observer identities and complete nondeselected collection. Baseline setup or collection failure permits only full fallback from that already validated candidate. Selector uncertainty falls back conservatively, while an unusable candidate refuses execution. Exact selected keys, mandatory/new obligations and selection witnesses are retained through the existing T05 contract; full mode uses declared targets.

Execution validates actual return codes, exact runtime collection, phase outcomes, permitted skips and required child labels/PIDs/exits. Results bind to the emitted plan digest. Checkout identity is re-resolved before each profile and after execution, and copy integrity is rechecked; stale observations do not become a pass. Darwin/APFS/native ACL qualification occurs before pytest. Locked private environments, sanitized Python/pytest settings, serial profiles, external observer/fixture paths and controlled nested caches support the intended local runner. The replacement temporary root and regression isolate native fixture ancestors from system temporary-directory churn; this is appropriately bounded to the local fixture problem.

The schema and provenance remain explicitly `local_advisory`. No hosted proof or merge qualification is minted, and #145/#146 qualification holds remain outside this implementation.

## Independent validation

On Darwin, using uv `0.10.6`, `uv sync --no-config --locked --python 3.13.9 --project packages/aitm-usage` with a separate private environment succeeded. The resulting interpreter reported Python `3.13.9`.

From the exact-head archive, ran `python -m pytest -q -p no:cacheprovider tools/ci/tests/test_tia_local.py` with `PYTHONPATH=tools/ci`, bytecode disabled, plugin autoload disabled and an explicit private pytest base directory: **12 passed in 44.65 seconds, exit 0, no skips**. These include the actual module command in plan/run modes, dirty snapshot advisory output, real test failure, full fallback/deduplication/children, checkout drift refusal, unavailable capability, missing child failure, invalid base, relative symlink reproduction, copy mutation refusal, nested cache isolation and native temporary-root cleanup.

Ruff lint passed; Ruff format check reported both files already formatted. Exact-range Git whitespace validation passed. The implementation checkout remained clean during read-only inspection.

Separately reviewed the immutable [native advisory receipt](https://github.com/kburson/aitm/blob/8b8d15e9ea9b7150b108484b42b141e590641c46/.aitm/stories/001/143/plan/native-advisory-717da4ce2540.json): exact candidate, full mode, 1,298 selected/executed/passed, exit 0, with 196 helper and 1,102 product/CLI obligations and both required child labels. Also inspected the published 159-case related validation. Those broader runs are coordinator evidence, not claimed as this reviewer's reruns.

## Issues and recommendations

Critical: none. Important: none. Minor: none requiring action. No source changes requested.

## Declined to judge

- Hosted TIA qualification and promotion of local outcomes into merge authority: explicitly deferred by the accepted phase boundary to later qualification work; existing hosted #103 controls remain required.
- General hostile-code sandboxing and cross-platform execution: this leaf runs the user's captured local Python tests on the qualified Darwin/APFS route; unsupported capabilities refuse, and the design does not claim an operating-system sandbox.

## Assessment

**ACCEPTED.** The implementation satisfies the accepted local advisory leaf and preserves conservative fallback/refusal and separate hosted authority. The independent exact-head focused native run and live CI identity checks support this verdict. A base or candidate change requires fresh applicable validation and review binding.
