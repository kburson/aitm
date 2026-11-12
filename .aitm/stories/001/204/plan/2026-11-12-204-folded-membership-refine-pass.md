# #204 independent Refine PASS for exact Claude child membership

Literal trunk `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`. #203 and #210 are Closed Completed. #204 remains a direct prerequisite of #119.

The pinned Claude Code macOS 2.1.318 foreground Agent selected the final metered child assistant response for `toolUseResult.usage`. The synthetic child made two distinct provider requests. Each joins its own durable row, forwarded assistant event, client request reference, server request ID, message ID and row UUID to the same outer tool, foreground task and completed run. The final `end_turn` response at child row 17 supplied the usage. The earlier `tool_use` response at child row 10 stayed outside the aggregate and requires independent accounting. The entire normalized usage shape matched the outer result as corroboration.

The executable hash and source ranges bind the proof to the foreground runner. It retains child history before filtering forwarded events, selects the last assistant response with `isUnmetered` other than true, overlays the checked usage onto native defaults, and passes the result through the completed tool payload. Null output tokens normalize to zero. Refuse missing selected responses, error or recovered history, unexplained injected entries, ambiguity, mismatched shapes, and unsupported native builds. The second synthetic run used a structured startup hook in its scratch project. It proved the same membership and exercised the existing startup recognizer. Neither run established native writer scope custody or a foldable child claim.

Independent Refine recovery passed on Claude Opus 5.5 high. Review input SHA-256 `e88a91d7172b842cf91f0dc86ffd055f1c4b4118231487aa905c42aa1b6556d9`. The first Refine HOLD remains the historical disposition for the earlier capture. Raw synthetic transcripts and binary excerpts are retained privately.

- [Native membership receipt](claude-foreground-membership.json)
- [Supplemental producer ranges](claude-foreground-producer-supplement.json)
- [Independent Refine verdict](claude-foreground-independent-refine-r2.md)
- [Structured startup capture](claude-foreground-structured-start-membership.json)
- [Registry preflight](claude-foreground-writer-preflight.json)
- [Child subroot preflight](claude-foreground-child-subroot-preflight.json)
