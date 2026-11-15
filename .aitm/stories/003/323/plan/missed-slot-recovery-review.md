# #323 independent review of missed-slot recovery

Verdict: ACCEPTED

Signed by OpenAI Codex, independent review agent `/root/missed_slot_review`. This verdict applies to the disposable recovery observation and its exact retained evidence. [Story #323](https://github.com/kburson/aitm/issues/323) · [Protected planning packet](https://github.com/kburson/aitm/tree/3708f730092adcfe59fb0fb5e7646e4a173014f7/.aitm/stories/003/323/plan)

## Exact review subject

| Evidence | SHA-256 |
| --- | --- |
| [Plan at initial protected revision](https://github.com/kburson/aitm/blob/9ca00dccbb71d962e076133820da434440fcfcb3/.aitm/stories/003/323/plan/2026-11-15-323-missed-slot-recovery-plan.md) | `5553df2f8e89870bf01c8e9ec5f908bbe0e5762fca79f9e5f63ecfdfbb16ec90` |
| [Results](2026-11-15-323-missed-slot-recovery-results.md) | `e6add4e08515eba2ea52723bb37437b1d52cb474fe51d6c5cf86ecff41122773` |
| [Manifest](SHA256SUMS) | `50ced6e241cbbd1c6698897e68beb3986fed14e22d8996719e0863bbb60bcb82` |
| [Qualification summary](qualification-summary.json) | `190085afd55313be96d5c2484671805d879f35f5ca6062ce2301277a3fd79b5c` |
| [Retained evidence archive](rehearsal-evidence.zip) | `c9ff03705b8e3566a1ee09fcd0f4400a1bf5daffb5076becb231e6b0fa2f9906` |
| Archive member `records/green/result.json` | `c79ea574bdb3bf3211a0b8d22a354ef10c3be6e342479e60132584ddc9e0299a` |
| Archive member `records/operator-acknowledgment/receipt.json` | `0a0e8983d7c85cb5925f681c93105b218d11024d719db5c3acdc25a4c08aec90` |
| Archive member `records/native-replay/result.json` | `5b122a811d37dc7336b031f857a294773e57d56e0885ccf912ebc015b06be678` |
| Archive member `records/control-results.json` | `81a5ef278656dcf4bf02d093ce4c8da16ab9bdb4caa356c0daab0af65166c6e2` |

I matched the manifest and all 23 listed files to the GitHub Git object identities at `3708f730092adcfe59fb0fb5e7646e4a173014f7`, downloaded the published archive independently and checked all 281 archived records. I reproduced the saved outcome and control results from the manifest-checked recipe and archive in fresh scratch with a detached exact source checkout. The regenerated control result matched byte for byte. [Reproduction](reproduction.md)

## Production observation and signed dispatch

Independent GitHub reads found one production schedule run, `43709222718/1`. It registered at 11:30:14 UTC on 2026-11-15, 7 hours 43 minutes 14 seconds after the 03:47 slot and after the 04:32 registration deadline. Its source was `4cfb41813199f9fa483447a61c65b9ca664fb97e`. The retained earlier #289 read saw zero scheduled registrations after the deadline. I executed the unchanged protected-source reader against GitHub before and after the rehearsal. Both current reads reported `incomplete`, `current_verified=false` and no current artifact. The latest production diagnostic was separately identified as stale workflow dispatch `43671830880/1`. The exact observer refused diagnostic incident eligibility even under an offline hypothetical green. [Production scheduled attempt](https://github.com/kburson/aitm/actions/runs/43709222718/attempts/1) · [Diagnostic attempt](https://github.com/kburson/aitm/actions/runs/43671830880/attempts/1)

The initial lab source pin was abandoned before dispatch when production trunk advanced. I checked the corrected lab merge, native rule reactivation and empty schedule history. GitHub protected lab trunk `27ab953c5d3280999a0c2eb4c75fd2003ca7e76b` and the separate update hold were in place before the predeclared 17:32 UTC slot and 17:34 deadline. The protected workflow deliberately had only a `workflow_dispatch` trigger. The missed-slot record captured empty history after the deadline, then the simulated operator issued signed authorization `bdb23cbf0d19f5bda815edb3db903c03` at 17:34:03.469891 UTC. I fetched the signer bytes from the protected lab commit, verified the ED25519 signature and matched the signed miss hash to the retained record. GitHub's native dispatch response named run `43741833227`, and native reads independently authenticated attempt 1, workflow `419337510`, event `workflow_dispatch`, actor and triggering actor `kburson` (`1082467`), and the exact protected lab ref and SHA. I observed the in-progress run with no conclusion. [Lab configuration and signer](https://github.com/kburson/aitm-missed-slot-323/tree/27ab953c5d3280999a0c2eb4c75fd2003ca7e76b) · [Re-pin PR](https://github.com/kburson/aitm-missed-slot-323/pull/1) · [Recovery attempt](https://github.com/kburson/aitm-missed-slot-323/actions/runs/43741833227/attempts/1)

## Full hosted evidence

I authenticated GitHub Actions check suite `118424235459`, check and job `132896486467`, and the artifact metadata for `14173500281`. The job logged native macOS 26 arm64/APFS and locked Python 3.13.9, uv 0.10.6 and helper GitHub CLI 2.97.0. The executed production subject was protected trunk `9de9dbbec4053b95cfab5e005cd876c667f71e10`, tree `d551e285f8c15c98ec7285bbf43f78c59d345756`. I independently compared all 163 payloads in a separate download to the exact native production Git tree, including all seven subject controls. Native preflight identifies the lab producer ref, workflow SHA, actor, event and exact attempt. The runner log identifies the separately fetched production SHA and tree and shows the normalized SHA and ref that the unchanged production runner requires.

I independently downloaded the 251,751-byte hosted ZIP before the rerun. Its SHA-256 `20c8e17ac2310205b7f46f9d97c1461e5c9455406f65f0e0401c27b4ce3e72a0` matched GitHub's digest, both the retained original download and the separate acknowledgment download. The artifact link, exact job interval, member list, authorization, subject, combined receipt and raw phase files reconciled. The run registered at 17:34:05 UTC. The job started seven seconds later, finished at 17:42:57 UTC, and GitHub recorded the upload at 17:42:48 UTC. [Recovery job](https://github.com/kburson/aitm-missed-slot-323/actions/runs/43741833227/job/132896486467)

My locked local collection on macOS arm64 reproduced the two reference reports byte for byte. Both hosted profile collections, executions and combined receipt matched those exact node IDs in order. Every test had one passing setup, call and teardown. I checked required policy IDs, phase uniqueness, zero skips and deselections, and the distinct subprocess witnesses `service-one-shot` PID 7730 and `cli-help` PID 8100, both exit zero.

| Profile | Ordered IDs and passes | Passing phases |
| --- | ---: | ---: |
| Product | 1,366 | 4,098 |
| Helpers | 545 | 1,635 |

## Hold, acknowledgment and replay

The native hold stayed active with no bypass after I observed the verified green. GitHub rule suite `5132918857` records the earlier pending-period merge refusal for PR #2. After green, rule suite `5132983767` records the same protected-ref refusal at 17:44:30 UTC. Both native rule suites mark only update hold `27321992` as failed and all three normal rules as passed. The probe branch existed and the PR remained open, mergeable and blocked while the hold was active. [Probe PR](https://github.com/kburson/aitm-missed-slot-323/pull/2) · [Pending-period rule suite](https://api.github.com/repos/kburson/aitm-missed-slot-323/rulesets/rule-suites/5132918857) · [Post-green rule suite](https://api.github.com/repos/kburson/aitm-missed-slot-323/rulesets/rule-suites/5132983767)

I independently verified the separate operator acknowledgment signature under the protected rehearsal key. At 17:45:02.180027 UTC it bound run and attempt, the artifact ID and digest, authorization ID, miss hash, hold ID, and exact fresh verification file `930e31e3624f1f62d420481ee6f0c1a45f961512dbea571fe9a7bd82335261f2`. The fresh capture still showed the active hold and the same verified positive subject. GitHub records disabling only hold `27321992` at 17:45:03.788 UTC. My subsequent native read confirmed protected lab trunk stayed on the reviewed SHA and normal ruleset `27321991` stayed active, with PR, deletion and non-fast-forward protections and no bypass. The probe PR reported clean after release and remained unmerged.

The deliberate native rerun started after release at 17:45:06 UTC. I read exact attempt 2 and job `132899623613`, and downloaded its logs directly. Authorization failed with `wrong event or replayed attempt`, full execution was skipped, and GitHub lists no attempt-2 artifact. Attempt 1 remains historical. The run and repository artifact inventories were empty after the rerun, and direct read of the original artifact ID returned HTTP 404. The published archive retains the pre-rerun provider metadata, exact downloaded positive ZIP and both attempts' native logs. [Rejected native attempt](https://github.com/kburson/aitm-missed-slot-323/actions/runs/43741833227/attempts/2)

The retained native pending case was held. I independently replayed the eleven off-host controls against the exact positive snapshot, including accepted-identity red, missing bytes and listing, foreign metadata, corrupt bytes, moved SHA, wrong event, newer candidate, duplicate signed admission, another attempt and premature hold disablement. Each failed closed as recorded. The production schedule absence case and counterfactual green diagnostic were off-host replays. The late schedule and its ineligibility were also verified live.

## Qualification boundary

The evidence qualifies a single isolated missed-window recovery with a simulated operator. The disposable workflow used the exact production source current at admission, dispatch and acknowledgment. Production before and after GitHub reads agreed for protected trunk, the effective ruleset and three workflow identities, and all 17 listed gate and shadow control blobs. #103 continues to govern production validation. Native schedule cadence, production credential separation, atomic enforcement across concurrent provider writes and full production PR integration remain separate qualification items under #133 and #294. Production cutover requires separate explicit owner approval. [#103](https://github.com/kburson/aitm/issues/103) · [#133](https://github.com/kburson/aitm/issues/133) · [#294 decision](https://github.com/kburson/aitm/blob/6d2a29fdfcef865c6769bfefe1cc07ddc628302f/.aitm/stories/002/294/plan/2026-11-15-294-cutover-and-rollback-plan.md)
