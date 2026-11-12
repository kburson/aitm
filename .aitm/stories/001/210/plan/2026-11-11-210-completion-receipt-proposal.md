# #210 proposal to qualify a receipt at native turn completion

**Proposed acceptance change.** The current Refine HOLD and #204 and #119 dependencies remain in force.

The append-only [public-reader probe](../attachments/test_210_same_turn_receipt.py) read three fixed prefixes of the existing disposition sequence. Through accounted command output and through completion of the command turn, the public reader exposed neither the disposition receipt nor a cursor. The receipt first appeared at ordinal 61 after the follow-up turn context. The new turn remained boundary-unverified. The probe first expected a function-call output and was corrected to match the fixture's actual custom-tool output. A sanitized sample of one admitted Desktop chat had 10 completed tool-bearing turns with a native usage record after the last tool output. This sample characterizes the observed ordering and does not establish a universal guarantee. [Receipt placement evidence](native-receipt-placement.json)

## Acceptance change for review

A fresh authorized disposition would bind the recognized command and queued output to the native completion of that same command turn. Reconcile that turn's accounting before taking its completion as the terminal anchor. A normally accounted provider request after the tool output and before that completion could precede the new terminal. The current accepted proposal uses the earlier next-turn receipt. Moving the anchor changes which activity counts as later usage and needs owner approval and independent acceptance.

Preserve the exact earlier owned hold and span, the typed current grant and request digest, the unique command/output link, same source/session/stream/turn and checkout, and a fixed physical prefix. Before accepting a positive, use the public reader with a genuine Desktop disposition command and complete same-turn accounting, prove clean native coverage through the completion, and prove absence of usage after the new terminal at that exact frontier. A generic completion row supplies no usage finality by itself.

Existing #203 and #209 next-turn proofs keep their current meanings. Old proposals cannot be moved forward or turned into current settlement authority. Require a fresh verified command and terminal before any release under the proposed route. Abort, unresolved or missing accounting, stale or copied evidence, foreign source, changed route or hold, and positive usage after the proposed terminal all stay held and replayable.

After native qualification, retain #210's existing owner/rival re-proof, one atomic JournalChange, cursor and effective view consistency, first ownership, and crash and restart controls. #204 and #119 stay gated through verified #210 delivery. Epic #2, C01, and production cutover remain outside scope.
