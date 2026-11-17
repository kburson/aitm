# #368 queue-inclusive hosted qualification findings

**HOLD.** The new admission window worked. The hosted rerun proved the restricted worker's ancestry readbacks, isolation denials,
and the independent observer's ability to account for every assigned outcome. The exact product scope returned 14 passing and
16 failing IDs, so the combined runner, observer and assignment qualification remains open. #355 remains blocked by #368.

## Exact live run

The owner authorized a fresh window in the #368 Codex conversation before the recorded 13:03:02Z opening. Opus 5.5/high accepted
the revised 105-minute packet at 13:10:47Z. GitHub created the run at 13:11:28Z and a macOS runner started the integrated job at
13:11:31Z, three seconds later. The runtime authenticated and the protected controller recorded its UTC dispatch decision at
13:12:46.148321Z, within the 14:48:02Z deadline. The job completed at 13:13:06Z. Conservative cumulative charge was 3.4633 hours
at dispatch and 3.4688 hours at job completion, within both reviewed closeout caps.
[Accepted packet](2026-11-17-368-queue-inclusive-execution-packet.md) ·
[Run 44090243525/1](https://github.com/kburson/aitm/actions/runs/44090243525/attempts/1) ·
[Job 134063181995](https://github.com/kburson/aitm/actions/runs/44090243525/job/134063181995).

The authenticated run used workflow head `56428a6ccc7c525b374f087dc2aa0c06e4cc7eac`, tree
`6f61e6d1a8a103d894c3607751cde3f42ca9abcd`, product baseline `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`,
and runner image `20261112.0504.1` on arm64 macOS 26.7.2 build `25G332`. The only new workflow-source difference was the
deadline. The authenticated artifact `14332020353` matched SHA-256
`ce2195147f73f7f9e807a27691fcc78a3663ad659b0540e3a6fdb1d8371f6a33`. I verified the archive and every receipt-listed member,
then separately parsed the ancestry and early process traces, the assigned IDs, phases and direct child lifecycles.
[Machine receipt](../attachments/2026-11-17-368-queue-inclusive-run-receipt.json) ·
[Screened artifact](https://github.com/kburson/aitm/actions/runs/44090243525/artifacts/14332020353).

## Gate results

| Gate | Live evidence |
| --- | --- |
| Restricted worker | Separate UIDs on APFS. The stat, owner, mode and ACL readbacks matched on all five directories. Physical scratch matched. All eight targeted denials returned EPERM. The baseline isolation controls also passed. |
| Early independent observation | The runner exposed 30 process and 1,116 syscall probes. Fresh fork, exec, exit and reap records and the expected USDT event matched the benign worker and controller wait. |
| Runtime and assignment report | Authenticated runtime restored. Both positive trusted report replays agreed. An extra untracked file produced `unsupported-change` with zero IDs. |
| Calibration and intake | The observer accepted the selected positive with one expected child, observed a genuine failing control, and detected the missing sibling on the stop-on-failure control. The integrated job advanced through intake checks to product dispatch. |
| Exact scoped run | All 30 archived IDs were discovered, collected, dispatched and observed. No IDs were missing, misordered or executed outside the assignment. The trace was clean and the tracer exited 0. All 74 exact direct native child lifecycles matched, including phase, executable and operation. Fourteen passed through teardown; 16 distinct IDs failed a phase. The product driver exited 1. |
| Post-run custody | The controller stopped at product reconciliation before post-run custody. GitHub published screened evidence and reported the qualification as failed. |

The pytest terminal summary reports 21 passing calls, nine failing calls and 15 teardown errors. Eight IDs appear in both
failure categories, seven more passed the call but failed teardown, and one failed only the call. The trusted count includes
every required phase and therefore gives 14 full passes and 16 distinct failures.

## Two failure paths

- **Transcript discovery.** Fifteen IDs failed during transcript locator use, all in teardown and eight also in the test body.
  The pinned locator raised `ValueError` because discovery yielded no matching transcript. `GrokAdapter.discover` uses
  `sources.scan._directory`, which opens each directory from `/` with `O_RDONLY | O_DIRECTORY | O_NOFOLLOW` and
  suppresses filesystem errors in the discovery path. The restricted profile admits metadata on the ancestors and denies their
  data reads. A separate same-UID local sandbox probe on synthetic directories reproduced the relevant distinction. Stat and a
  direct read below the ancestor succeeded while an ancestor directory open with those flags and a listing each returned EPERM.
  This supports ancestry directory-open denial as the explanation. The product run did not capture the precise failing
  directory-open syscall and errno.
- **Native process custody.** The independently observed pytest process was PID 2551 UID 550. Its direct parent PID 2550
  was UID 0. The pinned Darwin `install._process_identity` requires the requested process's UID to equal the caller's
  effective UID, and the custody test calls it on `os.getppid()`. The test therefore received `None` and failed its
  positive assertion. Passing that check would require a different, same-worker-UID parent arrangement.

The unchanged 30-ID module passed all 30 locally outside the qualification sandbox with Python 3.13.9, pytest 9.2.0 and
pluggy 1.7.0, matching the hosted versions. This control establishes the result under ordinary local execution. It does
not establish protected local observation. Resolving the hosted failures would require a layout compatible with descriptor-based
traversal while preserving reviewed listing denials, and a worker launch that provides a same-UID direct parent while preserving
independent observation. Both change the reviewed boundary or launch assumptions. The queue-only packet and this evidence leave
those requirements open. An exact-head repeat would exercise the same two structural conditions.

## Why both experiments were needed

The disposable local guest exercised the intended pre-commit boundary and its protected-path controls. The guest exposed no
usable DTrace process provider, so it ran zero assigned product tests. The #146 hosted runner supplied the missing independent
observer. Its first experiment observed 30 outcomes, with seven passing IDs and 22 of 74 expected native children matched.
The ancestry revision cleared the metadata gate and this live rerun matched all 74 children. It also exposed the remaining
directory-open and parent-UID conflicts under the hosted worker policy.
[Local findings](2026-11-16-368-live-tracing-findings.md) ·
[First hosted findings](2026-11-16-368-hosted-qualification-findings.md) ·
[Prior queue-only HOLD](2026-11-17-368-hosted-ancestry-run-findings.md).

The hosted rerun left scoped execution and post-run custody unqualified. Protected **local** execution and resistance to
unreviewed candidate code also remain unqualified, as do the broader candidate test inventory and impact completeness.
The #368 issue remains open and #355 retains its native blocker.
