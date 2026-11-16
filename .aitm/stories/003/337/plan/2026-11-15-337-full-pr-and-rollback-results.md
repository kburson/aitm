# #337 Full PR path and rollback results

The eight consecutive production PRs spent **22m 01s p50** and **45m 55s p95** from first canonical CI registration to final exact signed evidence. All eight exceeded fifteen minutes. The final successful attempt by itself took **8m 36s p95**. The whole PR took **54m 48s p95** from open to merge. Earlier heads, cancellations, reruns and review clocks are retained separately. Seven PRs retain historical exact verifier and review timestamps. [Production readout](production-readout.md) · [Production provider evidence](production-evidence.zip)

## Disposable rollback

The lab seeded the public protected production tree at `4ba4354f603ad861c897111dcaaf2342fc68da86`, added two rehearsal-only files and copied the native production trunk rule set. Its strictly app-bound required checks are an added lab control. The read-only trusted verifier authenticates exact candidate, all canonical jobs, coverage and signed artifact. An Actions status context by itself supplies no trusted attestation. This rehearsal uses fixed reviewed input paths and a simulated operator, with broader production credential and publisher isolation still to qualify.

| Held and restored behavior | Native evidence |
| --- | --- |
| Old app-authenticated pilot green, with zero canonical PR runs | [PR #1](https://github.com/kburson/aitm-rollback-337/pull/1) and [pilot run](https://github.com/kburson/aitm-rollback-337/actions/runs/43776122187) |
| Ordinary actor blocked while pilot check passed. After the gate switched, selected-only proof failed all six missing full contexts | Rule suites 5136279926 and 5136289087 |
| Intentional malformed JSON failed file checks and collector. Terminal signer skipped and both failing checks blocked merge | [Red run](https://github.com/kburson/aitm-rollback-337/actions/runs/43776314804) and suite 5136386588 |
| Operator direct push refused. Ordinary actor could not merge the fully green restore while the hold was active | Suites 5136384394 and 5136383866 |
| The independently reviewed forward restore changed only the disposable mode to full-only. Full evidence verified in 21m 05s from PR open | [Restore PR](https://github.com/kburson/aitm-rollback-337/pull/2), [pre-merge review](restore-review.md) and native suite 5136523549 |
| Superseded exact full evidence refused after trunk advanced. Fresh ordinary head passed the full verifier on the restored base | Old [canonical run](https://github.com/kburson/aitm-rollback-337/actions/runs/43776372089), suite 5136532518 and [new canonical run](https://github.com/kburson/aitm-rollback-337/actions/runs/43778385315) |
| Restored trunk passed a fresh full push. A separate signed acknowledgment on newly reverified evidence released only the update hold | [Exact push](https://github.com/kburson/aitm-rollback-337/actions/runs/43778309249); retained acknowledgment, native change and rule readback |

Ordinary native PR, deletion and non-fast-forward protections and all six app-bound canonical contexts remained active after release. The independent restore review was scoped to the exact head, tree and verifier receipt before the native merge. The supporting records show the recorded provider check identities, open candidate proof and exact landed parents. The refreshed ordinary PR remained open with all six required check contexts passing.

GitHub reported the ordinary PR mergeable with aggregate state `unstable`. The optional lab-only pilot job deliberately failed for the full-only route and was outside the six required checks. Only the reviewed restore PR merged during the rehearsal.

The first restore attempt passed full CI and independent review. The trusted pre-merge verifier refused it after GitHub regenerated the synthetic merge with the same parents and tree but a different SHA. The lab trunk stayed fixed. An empty synchronization commit preserved the intended tree, triggered fresh full CI and received a new exact disposition. The superseded attestation, rebuilt ref and failed pre-merge receipt are retained. The restore elapsed time above includes the refresh.

The reviewed evidence covers the existing full PR timing and one disposable rollback. The measured production cohort exceeds the latency target, and the experiment supplies no wider executable selection, production schedule cadence or cutover authorization. Production #103 control inputs, canonical workflow state and effective rules matched the starting snapshots. [Native rollback archive](rollback-evidence.zip) · [Machine readback](qualification-summary.json) · [Reproduction](reproduction.md)
