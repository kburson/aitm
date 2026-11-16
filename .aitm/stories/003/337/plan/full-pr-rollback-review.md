# Independent review of #337 full PR validation and disposable rollback

Verdict: ACCEPTED

I accept the production measurement and disposable rollback evidence at protected planning commit `9911fe7f4d5adc2ee603b7886c037a4334da00ed`. #337 is Rank 160 under #133 and follows the delivered #323 prerequisite. Acceptance covers the existing full PR path and one rollback in `kburson/aitm-rollback-337` under copied production trunk rules plus the proposed app-bound checks. Production #103 retains its authority. [Issue #337](https://github.com/kburson/aitm/issues/337) · [Exact packet](https://github.com/kburson/aitm/tree/9911fe7f4d5adc2ee603b7886c037a4334da00ed/.aitm/stories/003/337/plan)

## Evidence identity

I retrieved the protected planning revision, verified the remote manifest bytes, checked all eight entries against the manifest and extracted both archives. The archived production replay reproduced both JSON outputs byte for byte and the rollback replay verified all four retained lab signatures. I also independently verified the simulated operator's ED25519 acknowledgment. [Manifest](SHA256SUMS) · [Reproduction](reproduction.md)

| Artifact | SHA-256 |
| --- | --- |
| `SHA256SUMS` | `9aca19e231d14b5f1639f3ff4d4bd8a0c20cfbb59057f1b0f6ce4b28f1f71312` |
| `2026-11-15-337-full-pr-and-rollback-plan.md` | `ccdca1f606d6142b472769eee74adc96a29b1926d1bbdab89fc34a45bf341a80` |
| `2026-11-15-337-full-pr-and-rollback-results.md` | `f421d55f3e41d9072e455d133cc3fc6a9152271cfb995735066724f2a841dcef` |
| `qualification-summary.json` | `e0f55e98527beec901bf5289e0a507bd9fe719bef0c80d60c0546f056bd57f2c` |
| `production-evidence.zip` | `76a7ce2567bd6f1923406aa7a93e0beb6e6b3d02678937d473c8654fa954a81d` |
| `rollback-evidence.zip` | `84b074162b51a8dd83c5f52220655be32ef6f7e71d79403f680c3617e699b306` |
| `restore-review.md` | `43598a40041dade842aecc6fdade0356f3407e2c37f0ac61536413a7e78f3d92` |

## Production PR path

I reconciled the cutoff window against the native PR and CI listings and recalculated principal clocks directly from the raw job and PR records. The eight same-repository PRs opened after #319 and merged into `trunk` by the cutoff, covering 20 run IDs and 23 attempts. The immutable verification replay passed for all eight final candidates and cryptographically verified 15 signed artifacts. The final-attempt-start to signed-job p95 was 8m 36s. First provider registration through final exact signed evidence was 22m 01s p50 and 45m 55s p95, with all eight at or beyond 15 minutes. First registration through both historical verification and recorded exact review was 52m 17s p95 across seven, and open to merge was 54m 48s p95 across eight. [Production readout](production-readout.md)

The readout preserves retries, earlier heads, the distinction between provider registration and an unrecorded trigger clock, and review recording time versus review execution. Four cancelled attempts rely on unique branch and time-window association. #324 has the verified final signed artifact and lacks historical pre-merge verifier and review timestamps in the retained evidence. The final cohort ran 1,367–1,487 candidate tests. The 3,000-test workload remains a separate modeled comparison. This measurement exceeds the latency target.

## Disposable rollback

I checked the tested source, actor and target identities, rule evaluations and exact signatures. The original selected-only PR #1 passed authenticated `pilot-evidence` for the single Markdown fixture, with zero canonical runs. The ordinary job token passed the applicable check rule and was refused solely by the active hold in native suite `5136279926`. After the switch, `5136289087` reported all six full checks missing for the old pilot. Red PR #3 failed `file-checks` and `collect-evidence`, with `aitm-ci` skipped. Its unchanged verifier held, and native suite `5136386588` reported two failing required checks. The operator's direct push was denied in `5136384394`. [Pilot run](https://github.com/kburson/aitm-rollback-337/actions/runs/43776122187) · [Red run](https://github.com/kburson/aitm-rollback-337/actions/runs/43776314804)

The ordinary actor's denied merge attempt on the first fully green restore passed native full checks and failed the separate update hold in suite `5136383866`. GitHub then exposed a new synthetic merge SHA with the same ordered parents and tree. I independently reproduced the premerge verifier's refusal of the earlier SHA-bound signature. The refreshed restore changed only the disposable mode from `pilot` to `full-only` against the lab base. I independently reran the unchanged verifier for refreshed head `d43d94a7dcf0ab1932092ee135ea142b9b21ef18` against `0cc6c0c9fabe47efb36972d6aa0af0ec56f6bd15`, tested `37d2c271233584fe98c97ca7b8a646f28f4b4f5b`, tree `6dcdc52b7dd0e582b0a5e555ea45af44dda65fa1`, and signed the exact premerge disposition. GitHub's suite `5136523549` records the designated operator bypassing only the update hold and passing the ordinary rules and all six required checks. Landed trunk `b848e1612870d143472c54a9a3ab2b7eb806ac23` has the accepted tree and ordered parents. [Restore premerge review](restore-review.md) · [Exact restore run](https://github.com/kburson/aitm-rollback-337/actions/runs/43777508613)

The previous ordinary #4 exact green separately passed my independent live verifier on the old base. After the restore moved trunk, the unchanged verifier held and native suite `5136532518` refused the superseded evidence. The older pilot also failed the unchanged verifier on the restored target. I independently verified all six canonical jobs and signed fresh evidence for #4 head `7a74a51ab3e4b81fa0ed29ccfe40acf203195ff6` on the landed base. I applied the delivered push observer to the lab provider identity and independently authenticated the current trunk artifact, four applicable push jobs and 1,487 passing-policy tests while the hold was still active. [Old ordinary run](https://github.com/kburson/aitm-rollback-337/actions/runs/43776372089) · [Fresh ordinary run](https://github.com/kburson/aitm-rollback-337/actions/runs/43778385315) · [Exact push run](https://github.com/kburson/aitm-rollback-337/actions/runs/43778309249)

The simulated operator acknowledgment binds the independently reverified fresh PR and push receipts. Its signature verified and its timestamp preceded the native change disabling only hold `27339262`. Live rules and archived before-and-after records agree that the normal PR, deletion and non-fast-forward rules and the six required GitHub Actions contexts remain active. Ordinary PR #4 stayed open with all six required checks green. GitHub's aggregate `unstable` state includes the intentionally failing optional pilot check. Only the reviewed restore merged. [Native rollback archive](rollback-evidence.zip)

Production `trunk` and its canonical gate inputs, active canonical workflow and effective rules matched the starting snapshots. The native app-bound contexts enforce check outcomes in the lab. The unchanged trusted verifier remains mandatory for authentic exact-candidate evidence. The selector is a disposable fixture and the acknowledgment uses a simulation key. Production publisher and credential isolation, schedule qualification and explicit owner approval for any exact cutover remain separate requirements under #294. [Readiness decision](https://github.com/kburson/aitm/blob/6d2a29fdfcef865c6769bfefe1cc07ddc628302f/.aitm/stories/002/294/plan/2026-11-15-294-cutover-and-rollback-plan.md)

Signed by the independent Codex reviewer `/root/review337`.
