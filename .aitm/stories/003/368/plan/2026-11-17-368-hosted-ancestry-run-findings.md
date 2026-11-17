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
same physical path. Worker metadata, full mode, owner and ACL classes matched the outside-sandbox local readback. Listing, home-directory and canary metadata,
ACL and the synthetic canary data denials produced eight EPERM records. Thirteen harness unit tests passed. This was an ordinary-account
synthetic check. The separate-UID hosted controls remain to be verified. [Local reproduction](../attachments/2026-11-17-368-ancestry-local-reproduction.json)

## Exact attempted run and stop condition

The submitted workflow head was `f5f1cf8f48804c364375042ba32426a3125b9749` and tree `4c9cc4a50b74a552a8c8c33eb2aa6821839486cf`. GitHub created run `44085388689/1` at
`2026-11-17T12:40:43Z`, with job `134046345090` requesting `macos-26`. Plan acceptance was `2026-11-17T12:31:32Z`
and the exact product dispatch deadline was `2026-11-17T12:52:24Z`. The recorded status at expiry was `queued`, with no assigned runner
and no executed steps. The cancellation is confirmed at `2026-11-17T12:52:42Z`. There was no controller dispatch-decision timestamp because
the job never reached the gate. The earlier hosted baseline still shows seven passes and 23 failures. The separate offline guest result remains
part of the story. [Previous paired results](2026-11-16-368-hosted-qualification-findings.md)

The 2.152-hour prior preflight upper bound plus the 0.348-hour window exhausted the original 2.5-hour cumulative
admission/preflight stop. At HOLD on `2026-11-17T12:52:42Z`, the conservative charge against the
packet and overall limits was 3.128 hours, leaving 0.622 hours under the 3.75-hour packet limit
and 2.872 under the six-hour overall limit. The accepted code and packet are retained. Another live attempt needs the
owner's explicit authorization of a new admission budget or an approved revision to the stop, followed by a fresh reviewed
packet with a new product dispatch deadline. Keep #368 open and #355 blocked.
Protected local execution and resistance to unreviewed candidate code remain unqualified.
[Exact execution packet](2026-11-17-368-hosted-ancestry-execution-packet.md) · [Machine receipt](../attachments/2026-11-17-368-hosted-ancestry-run-receipt.json) at SHA-256
`a3378e20a4d25de4f40755d99620689711d4bac470ea3a0cad264ef2441bc6fb`.

The five authenticated GitHub API responses are bound by individual SHA-256 hashes, capture times and selected readback fields. [API evidence](../attachments/2026-11-17-368-hosted-ancestry-api-readback.json) at SHA-256 `5ffe99d4c4d44b47a7c77f114ea642a9f01a2a971d9e226952037b6b94b10ff5`. The raw responses are held in the executor’s private cache.
