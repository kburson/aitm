# #368 ancestry qualification rerun findings

**HOLD at hosted runner allocation.** The revised policy passed local validation, author review and Opus 5.5/high SAR and XPR.
The full hosted qualification was submitted for execution. GitHub kept it queued with zero steps and no allocated runner
through the reviewed admission deadline. The job was then cancelled with zero product tests and zero exported artifacts.
This attempt supplies scheduling and local-regression evidence. The live hosted boundary and integrated assignment on the
revised policy still require qualification. [GitHub run](https://github.com/kburson/aitm/actions/runs/44085388689/attempts/1)

## Revised worker policy

The branch adds literal metadata access for `/`, `/Users` and `/Users/Shared` for the integrated worker. It retains the admission-root
literal and existing protected paths. The local pinned ledger ancestry check reproduced `LedgerError: Private ledger ancestry is unavailable`
under the previous profile. The revised profile produced the complete six-identity chain for the synthetic target. Python resolved the
same physical path. Worker metadata, full mode, owner and ACL classes matched the outside-sandbox local readback. Listing, child metadata,
ACL and the synthetic canary data denials produced eight EPERM records. Thirteen harness unit tests passed. This was an ordinary-account
synthetic check. The separate-UID hosted controls remain to be verified. [Local reproduction](../attachments/2026-11-17-368-ancestry-local-reproduction.json)

## Exact attempted run and stop condition

The submitted workflow head was `f5f1cf8f48804c364375042ba32426a3125b9749` and tree `4c9cc4a50b74a552a8c8c33eb2aa6821839486cf`. GitHub created run `44085388689/1` at
`2026-11-17T12:40:43Z`, with job `134046345090` requesting `macos-26`. Plan acceptance was `2026-11-17T12:31:32Z`
and the exact admission deadline was `2026-11-17T12:52:24Z`. The recorded status at expiry was `queued`, with no assigned runner
and no executed steps. The cancellation is confirmed at `2026-11-17T12:52:42Z`. There was no controller dispatch-decision timestamp because
the job never reached the gate. The earlier hosted baseline still shows seven passes and 23 failures. The separate offline guest result remains
part of the story. [Previous paired results](2026-11-16-368-hosted-qualification-findings.md)

The plan charges the prior 2.152 preflight-hour upper bound plus the 0.348-hour new admission window. The accepted code and packet are
retained. A new reviewed admission window with a fresh exact packet is required for another live attempt. Keep #368 open and #355 blocked.
Protected local execution and resistance to unreviewed candidate code remain unqualified.
[Exact execution packet](2026-11-17-368-hosted-ancestry-execution-packet.md) · [Machine receipt](../attachments/2026-11-17-368-hosted-ancestry-run-receipt.json) at SHA-256
`a3378e20a4d25de4f40755d99620689711d4bac470ea3a0cad264ef2441bc6fb`.

The executor's authenticated GitHub API responses for expiry, final job and artifact count are retained under `/Users/Shared/aitm368-ancestry.9nEAFE39`.
