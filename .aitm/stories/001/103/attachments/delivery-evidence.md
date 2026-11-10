# #103 delivery evidence · November 10, 2026

- [#104](../../104/retro/2026-11-10-ci-bootstrap.md) delivered the ordinary PR workflow, isolated attestation and exact-merge readback. Hosted ShellCheck supplied a real failure and the corrected run passed. Moving only the disposable target invalidated the old evidence. A fresh run verified the refreshed base and closed #104.
- [#105](../../105/retro/2026-11-10-ci-verifier.md) delivered the read-only verifier and genuine signed fixture tests. The delivered copy held the live incomplete proof and then agreed with the independent manual check. The one-file proof PR closed unmerged and its temporary refs were removed.
- [#106](../../106/plan/delivery-checklist.md) added locked Markdown, YAML and strict JSON checks to the same workflow. Ruff and actionlint still cover Python and workflow semantics. A native Markdown failure held the aggregate with the earlier lanes green and skipped signing. The corrected PR is verified below.

The repository currently has no product TypeScript. The file check reports that applicability explicitly. The full Python suite runs serially on Darwin APFS. Both scopes use unrounded raw line counts with a 90% floor, and the two normal CLI and service child processes supply their own coverage. The suite records inventory, per-test durations, cache state and run timing for later scheduling decisions.

## Exact final candidate

The delivered verifier and independent manual check agreed on the tested merge `65253157183d5b0f42a0b024c3c12788fd87fbae`, tree `549de417f614d7ef9f91fa6020bc1c732847bdd4`, the six job results, archive identity, signed subject SHA-256 `0478e39308f4ec53c1d7655d39af7e0729aa3627da2284ea9d08682c362c38bb` and the two coverage scopes. An independent reviewer also replayed the gate using the raw evidence. The ordinary PR merge delivered this tree to trunk at `9cc3b7b9912245e2ffcfa8b24ffbfa4e32523cc6`. [Passing PR attempt](https://github.com/kburson/aitm/actions/runs/42829600040/attempts/1) · [Source review](../../106/plan/post-ci-source-review.md) · [Trunk verification](https://github.com/kburson/aitm/actions/runs/42830542706)

The local product repeat passed 531 tests and the helper suite passed 182. The signed hosted result measured 6,285/6,910 (90.96%) product lines and 778/821 (94.76%) helper lines. The installed-wheel smoke and both normally exiting child-process measurements passed. Earlier one-off failures in two unchanged local service tests remain recorded with their passing reruns. [#105 evidence](../../105/plan/delivery-checklist.md) · [#106 evidence](../../106/plan/delivery-checklist.md)

GitHub had no required CI status checks at closeout. The planning checklist defers mandatory CI use to a separate design after the build works locally and in GitHub Actions. [Manual checklist](../../../../manual-delivery-checklist.md)

## Runner measurements

GitHub job start and finish times sum to 48.5 macOS runner-minutes and 8.8 Linux runner-minutes across 13 named epic runs. These sums include diagnostics, failures and superseded proofs and exclude skipped jobs. They are observed runner time. GitHub billed spend is Unknown.

| Attempt | Result | macOS seconds | Linux seconds |
| --- | --- | ---: | ---: |
| [42749926303](https://github.com/kburson/aitm/actions/runs/42749926303) | success | 4 | 0 |
| [42756762134](https://github.com/kburson/aitm/actions/runs/42756762134) | success | 0 | 13 |
| [42819416038](https://github.com/kburson/aitm/actions/runs/42819416038) | failure | 278 | 26 |
| [42819951099](https://github.com/kburson/aitm/actions/runs/42819951099) | success | 302 | 43 |
| [42821017488](https://github.com/kburson/aitm/actions/runs/42821017488) | success | 152 | 40 |
| [42821068153](https://github.com/kburson/aitm/actions/runs/42821068153) | success | 291 | 39 |
| [42821747864](https://github.com/kburson/aitm/actions/runs/42821747864) | success | 283 | 51 |
| [42824974182](https://github.com/kburson/aitm/actions/runs/42824974182) | success | 300 | 43 |
| [42825839166](https://github.com/kburson/aitm/actions/runs/42825839166) | success | 173 | 32 |
| [42825896772](https://github.com/kburson/aitm/actions/runs/42825896772) | success | 313 | 64 |
| [42828814252](https://github.com/kburson/aitm/actions/runs/42828814252) | failure | 309 | 42 |
| [42829600040](https://github.com/kburson/aitm/actions/runs/42829600040) | success | 287 | 94 |
| [42830542706](https://github.com/kburson/aitm/actions/runs/42830542706) | success | 220 | 39 |

The signed cold #104 proof recorded 4 seconds of setup, 102 seconds of tests, 122 hosted seconds and a 3-second queue. The final warm #106 PR recorded 4 seconds of setup, 147 seconds of tests, 171 hosted seconds and a 4-second queue. These observations cover different runs and support later scheduling analysis.

## Agent measurement

The production collector was running, but the epic and child rollups had zero attributed observations. The installed launcher cleared the Codex chat identity before the marker command could authenticate it. Agent engagement, API-equivalent dollars, actual provider spend and subscription-limit effects are Unknown for this delivery.
