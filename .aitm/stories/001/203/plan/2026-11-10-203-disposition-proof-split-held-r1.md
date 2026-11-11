# #203 M08b4 Refine and bounded split

Epic #100, literal product target trunk. #202 is Closed Completed and Done after verified PR #207. The current detached source baseline is merge `1282538954dc5a7e7f7b27da4e3ab096892e3add`, tree `906680801e3f6d0a121248fe20fb4c80397478aa`. Project 24 Rank 228. This artifact requests independent acceptance of a split only. Each resulting leaf has a separate exact JIT before Develop.

The clean detached literal baseline passed 996 product and CLI tests and 182 helpers, Ruff, and raw 10,461/11,407 product and 778/821 helper lines. A separate private native-parser preflight passed. It verified the original bytes through the fixed cursor, preserved hold `[18,19)`, admitted the distinct terminal at ordinal 29 with no later usage, and observed the legacy disposition gate refuse. This establishes the parser seam and the actual boundary failure.

## Why split

The accepted #199 M08b4 split calls for a writer-verified scope and coverage disposition, its separate native terminal receipt, exact half-open overlap, an atomic local JournalChange, and explicit authority for both affected replay frontiers. It also requires old v1 scope resolutions to remain historical absent fresh exact authority. These are distinct implementation and validation risks.

`ScopeState.verify_boundary` can authenticate a current terminal native command receipt. The command recognizer accepts monitor scope dispose and #118 demonstrates a receipt at EOF with no later usage. However, `ScopeState.dispose` requires the new receipt ordinal to fall inside the original already-fixed hold span. `test_verified_disposition_only_releases_its_covered_hold` explicitly refuses the later receipt and its positive case replaces the held suffix to reuse the ordinal. `_Resolution` retains only the command ID, digest and resulting original hold. It contains neither the terminal target nor the original fixed physical witness. Keep this legacy method and its original test behavior. A new journal proof must join a real later receipt to a separately authenticated older span without rewriting the transcript.

`RoutingJournal._boundaries_settled` already refuses an otherwise unknown disposition receipt. `RoutingJournal._claim` and `_reserve_revision` keep ownership and content disputes as separate durable evidence. A single owner's current ProofHold cannot settle a journal dispute involving two independent carriers. Current policy does not define a joint receipt. The paired frontier leaf must prove both actual sides and its resulting disposition under fresh current authority, with first ownership retained. Any missing authority keeps the affected frontier replayable.

The Claude monitor quota diagnostic has no authenticated reader with a durable exact replay obligation in this chain. Keep every quota-only, identical generic, and mixed diagnostic unsettled. Grok snapshot contradiction coverage remains held because no Grok source is currently admitted for project scope and routing. The source order and the #204 positive folded proof gate stay in force.

## Proposed slices

| Story | Rank | Requires | Directly gates | Bounded deliverable |
| --- | ---: | --- | --- | --- |
| #203 M08b4a | 228 | #202 | M08b4b and #119 | Verified append-only native scope disposition evidence and exact old/new scope storage, 3.75 agent-hours before its own JIT estimate. |
| M08b4b new | 228.1 | #203 | M08b4c and #119 | Exact RoutingJournal.record_disposition contract, strict v4 compatibility, one local JournalChange, scope/coverage projection, active half-open overlap for existing and late claims, atomic receipt and idempotent historical replay, at most 4 hours after its own JIT. |
| M08b4c new | 228.2 | M08b4b | #204 and #119 | Exact current paired owner/rival disposition and cursor settlement, real no-later-usage terminal and restart fixtures, retained unsupported coverage and proof, at most 4 hours after its own JIT or a further independently accepted bounded split. |

All three directly block #119 and remain direct children of #100. Preserve the original #203 → #204 edge as an additional dependency and add M08b4c → #204. Preserve #204's own direct #119 gate. Read back the complete native parent, project Rank and dependency graph before Develop or closing #203. The split leaves the accepted milestone order and closure conditions intact. It carries the complete accepted M08b4 requirement through the three leaves. Any unsupported member keeps its story and the direct #119 prerequisite open.

## Scope proof for #203's later exact JIT

Use the existing admitted local Codex Desktop or Claude native parser and fixed batch. First record a real owned hold, append a separately linked monitor scope dispose command and terminal receipt, and demonstrate the earlier immutable prefix, distinct later ordinal and lack of later usage. Use synthetic fixture data in the normal parser. Show the current legacy path remains HELD on this input. New proof issuance will have a separate ScopeState entry point that binds the exact present operator authority, command digest, original hold and source/session/stream, original half-open span, terminal command/receipt/digest/physical position, and current fixed batch under the same writer. The terminal ordinal is at or after the old span end. A current owned hold can propose GAP, or propose RESOLVED only with the same prior route throughout the target, intact checkout/authority, and an unexpired eligible hold. This proposal is evidence for later journal adjudication. ScopeState routing, hold state, journals and cursors remain unchanged in M08b4a.

Retain a closed typed proof of the original fixed physical prefix and native hold receipt for newly authenticated holds, with a separate closed typed record of the disposition's terminal receipt and target span. Use the existing private ScopeState publication fence and exact format-specific codecs. Select the next version only when writing new proof, preserve the exact legacy codec and legacy records, and fail closed on wrong, mixed or unknown formats. A v1 resolution alone supplies no v2 target authority. A fresh operator and exact current source must reprove any replay before a new ephemeral same-writer proof issues. Freeze exact persistent types and schema, original/terminal join, retry and old-reader test in the later JIT.

Require current physical and capture rechecks before and after publication, exact idempotent same-command replay, conflicting command reuse refusal, stale/foreign/copy/wrong scope/disabled-capture controls, and a normally appended EOF positive. Keep terminal location and target span distinct. Keys remain hints. Subsequent journal work owns effective claim/receipt settlement and separately proves late overlap, journal atomicity and both replay frontiers.

## Required rechecks

Independent review must confirm that the split covers every accepted M08b4 deliverable, that proof issuance itself cannot release an old hold or route, that the terminal and target can be joined using an actual append-only native fixture, and that the native graph preserves #119 and #204 order. Before any source changes, accept an exact #203 JIT with closed persistent shapes, executable positive and negative controls and a measured checkpoint under four hours. Epic #2, C01 and production cutover remain outside Epic #100 delivery.
