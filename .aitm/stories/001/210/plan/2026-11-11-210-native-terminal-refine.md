# #210 Refine checkpoint for native terminal settlement

**HOLD.** #209 closed after verified delivery as literal trunk `71aa5c880fc6a1db1cf676dfc663373f02ef7b16`. Its tree is `b4a757f106b89086a24d0e909bc259d7b5b93c88`. #210 is the next Epic #100 child at Project Rank 228.2 and directly gates #204 and #119.

The [disposable probe](../attachments/test_210_native_terminal.py) used the admitted Codex Desktop fixture, chronological append-only native rows, and the public `ScopeState.read_source` API. All three controls preserved the existing journal cursor and held scope. A separate earlier committed read witnessed positive usage before each terminal. The pilot initially expected the proof-only EOF read itself to project the earlier usage. The corrected probe checks the independent prior committed read and records the empty EOF projection as observed.

| Native control | Eligible terminal | Current provider cursor | Diagnostic | Positive usage after terminal |
| --- | --- | --- | --- | --- |
| Proof-only EOF | Yes | Absent | `boundary-unverified` | Absent |
| Counterless completion | Yes | Present | `coverage-gap` | Absent |
| Separate later usage | Yes | Present | None | Present |

The [qualification receipt](native-terminal-qualification.json) records original span `[46,53)`, terminal 61 and the genuine later observation at 63. The first two controls fail qualification. The later observation tests a distinct case and does not qualify a no-later-usage terminal. The current parser attaches the receipt to a follow-up turn. A counterless close leaves the existing coverage-gap rule active, and same-total displays do not establish a newly accounted turn. The journal also requires the disposition receipt to be independently settled.

The [independent Refine](2026-11-11-210-native-terminal-refine-review.md) held. Its suggested later-usage positive release would change the accepted carrier contract and is outside this checkpoint. A bounded follow-up must first establish an authoritative native closure signal under the accepted split, then earn its own required independent acceptance. #210, #204 and #119 remain open. Project Estimate and Size await accepted Refine and JIT. The [Actual evidence](../attachments/timing/refine-actual-readback-input.json) records partial coordinator engagement through this attempt.

## Native closure signal follow-up

The installed Codex Desktop CLI is `0.167.0-alpha.3.2`, the admitted version. Its generated App Server schema exposes turn completion status and timing, and a separate turn-keyed token usage notification with last and cumulative counts. Neither schema declares finalized accounting for a counterless closed turn. [Official Codex App Server event documentation](https://learn.chatgpt.com/docs/app-server#turn-events)

A sanitized sample of this one desktop chat confirmed completion rows with timing and last-message fields, one interruption with lifecycle and reason fields, and repeated cumulative usage snapshots. Only field names and counts were retained. The sample characterizes the observed shape and does not establish that every native turn produces identical evidence. [Schema and native evidence](native-closure-followup.json)

The [public-reader probe](../attachments/test_210_native_closure_fields.py) tested four chronological variants on the literal base. A completion with native timing fields left `coverage-gap`. Interruption left `coverage-gap` and `boundary-unverified`, with no cursor. Repeating the earlier genuine cumulative counter before timed completion still left `coverage-gap`. The clean control had genuine usage after the eligible receipt. All four preserved the existing journal cursor and held scope. The provider cursor present in two negative cases does not satisfy the journal's clean coverage gate.

Refine remains held pending a native signal that attests final usage for the exact receipt and fixed stream without later activity. #210, #204 and #119 remain open. [Cumulative partial Actual evidence](../attachments/timing/native-closure-actual-readback-input.json)
