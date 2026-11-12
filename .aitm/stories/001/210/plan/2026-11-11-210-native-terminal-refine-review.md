# #210 independent Refine review

Claude Opus 5.5 high. Literal trunk `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`, tree `b4a757f106b89086a24d0e909bc259d7b5b93c88`. Packet SHA-256 `d08c324578a169275eff45684c076a468c1fb6b2d89913bea78c732dff8b2fbf`.

HOLD

**Decision:** None of the three controls is a genuinely settled no-later-usage native terminal. The evidence agrees with itself (`status: no_settled_no_later_usage_carrier_qualified`). The accepted split says a missing qualified carrier keeps #210 open, along with its direct #119 and #204 gates.

## The five properties, control by control

| Property | `proof_only_eof` | `counterless_completion` | `later_usage` |
|---|---|---|---|
| Terminal receipt eligible (61, at or after span end 53) | yes | yes | yes |
| Provider cursor | **none** | yes | yes |
| No later usage | yes | yes | **no (63)** |
| Clean coverage | **no** (`boundary-unverified`) | **no** (`coverage-gap`) | yes |
| Actual paired settlement | none | none | none |

- **`proof_only_eof`** is the seam the split names and excludes: the boundary is unresolved and there is no cursor. Its empty current projection is correct, because `_read_codex` returns only diagnostics when `batch.cursor is None`. The real positive earlier usage `[3..23]` is properly witnessed by the earlier committed read, as the pilot correction requires.
- **`counterless_completion`** is the generic completion the brief forbids. `turn_end` emits `COVERAGE_GAP` because `turn.seen_counter` is false. Its cursor only marks how far the provider read got; it does not settle anything. `_complete` refuses any batch with diagnostics.
- **`later_usage`** has clean coverage and a cursor, but only because of genuine later usage at 63. It is the required control, not the carrier. Treating its cursor as no-later-usage settlement would be exactly the "unrelated later-usage cursor" the brief forbids.
- **Paired settlement** happens in no control. The journal cursor is unchanged, the hold stays `held`, and no owner/rival source, span or frontier authority is shown for either side.

## Parser and journal checked against the split

The current code matches the accepted split:

- An EOF read keeps `BOUNDARY_UNVERIFIED` and gives no cursor.
- The terminal receipt attaches only to the start of the follow-up turn (`turn_start` through `next_turn_receipt`), so the receipt always opens a turn.
- That turn can only close cleanly if `seen_counter` is set, and only a counter with a changed total sets it:
  - A counter with the same total returns early. This correctly refuses a fabricated zero.
  - A missing baseline, regression or compaction each produce a gap or regression diagnostic.
  - A higher total is, by definition, later usage.
- So under the current parser a clean, no-later-usage carrier cannot exist in this receipt shape. That is a design conclusion, not a fixture gap.
- `_boundaries_settled` still refuses the disposition receipt, because it matches neither an applied event nor a hold `command_id`.
- Legacy `dispose` raises `LedgerError`.
- The fixture's earlier rows keep their order and timestamps are non-decreasing; nothing is backdated.

## Authorized path to resolve the HOLD

The split permits two routes: M08b4c's own independent JIT, or "a further independently accepted bounded split". I recommend the bounded split, so that the parser-semantics risk stays separate from journal settlement:

1. **M08b4c-i (journal settlement, no parser change).**
   - Journal-derived effective hold in the admitted routing ScopeView.
   - One atomic JournalChange.
   - Owner/rival re-proof at adjudication.
   - Crash and re-read idempotence, plus refusal of a mismatched hold or route.
   - The clean `later_usage` carrier is the only positive release.
   - Every no-later-usage terminal stays held and replayable.
   - Gates #119 and #204.
2. **M08b4c-ii (native carrier qualification).**
   - Needs its own exact JIT for any parser change that defines a settled no-later-usage terminal.
   - That change must rest on a closure signal Codex actually produces natively. A counterless `end`, a same-total counter, a zero-delta counter or a backdated counter cannot count.
   - It must keep the `later_usage` and `counterless_completion` negatives.
   - It stays a direct #119 and #204 prerequisite until it is qualified through the public reader.
   - If no such native signal exists, this leaf stays open and no no-later-usage release is ever allowed.

Either route needs the split or JIT accepted, Ranks read back, and the parent, project, #119 and #204 edges rechecked before Develop. Epic #2, C01 and production cutover stay out of scope.
