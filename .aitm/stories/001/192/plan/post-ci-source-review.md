# #192 independent post-CI source review

**Verdict** PASS. No material source findings remain for the exact candidate. Signed by Codex, independent source reviewer, on 2026-11-11 UTC.

## Candidate and signed evidence

- Repository `kburson/aitm`, PR #221 targeting `trunk`. [Pull request](https://github.com/kburson/aitm/pull/221)
- Base `aa7dff45156919bcbe34d0489335949259bc584a`, head `96d9788f36f6be71315a5014bc2e9412fae6692c`, tree `75c3e40316fc49821a0f174565d6d26fe0bdc2cd`, and tested merge `52a26ceb751fcdd0ea35b53a90167522ad863024`.
- The signed verifier reported PASS for run `42963929800` attempt `1`, artifact `13830860547`, and subject digest `80270fefcaa43c1076d16b4d590c11c45c3869bd90f42057e3af20a5bf4ff44f`. The six verified jobs are `aitm-ci`, `collect-evidence`, `file-checks`, `python`, `python-base`, and `quality`. The local head and tree match the record. The tested merge identity comes from the signed record. The two previous hosted attempts have no authority for this verdict. [Hosted evidence run](https://github.com/kburson/aitm/actions/runs/42963929800/attempts/1)
- The clean candidate diff adds only `tools/story_dashboard/dashboard.html`, `tools/story_dashboard/render.py`, and `tools/story_dashboard/tests/test_render.py`. The three files match reviewed correction `ce2a18a5f5579bae7ef0776a2a498ee62576972c` byte-for-byte. The base is an ancestor of the candidate and `git diff --check` passed.

## Source and verification

- The earlier private payload and drilldown findings are resolved. The complete nested v1 field allowlist rejects unrecognized keys before embedding. Typed evidence and detail validation rejects malformed objects before browser rendering. Coverage, source links, and display scope follow the A05 contract. The renderer preserves valid pinned journal and receipt links, makes rejected destinations inert, handles output aliases, escapes snapshot text, and limits inline assets with hashed CSP.
- Independently reran all 61 dashboard tests on the exact head, including the five renderer tests. All passed. The exact-byte candidate evidence records Ruff, whitespace, and Node syntax checks.
- Independently regenerated the real and adversarial HTML in memory and matched the retained browser inputs byte-for-byte. Their SHA-256 digests are `1da066aaff343b8ae4c04cec74a1f291765e607d8117045b4590080ac552bdd2` and `bd53b835d2f243ea0119533af688795048aec67f4a7ec92247daeb6ee7f2bb0a`, respectively. Four retained Chrome observations across 390 and 1280 CSS pixels report zero automatic web requests, all three filters and functioning drilldowns. The historical fixture preserves #111 Actual of 36m 26.725s and implementation elapsed of 12m 54s with Unknown all-phase elapsed and Cost. The adversarial fixture preserves safe literal text, independent usage and timing watermarks, and exact priced Cost.

This is a signed off-platform source review. Native GitHub review is absent.
