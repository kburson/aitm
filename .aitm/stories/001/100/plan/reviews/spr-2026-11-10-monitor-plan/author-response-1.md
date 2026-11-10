# Author response to SPR round 1

Revised plan SHA-256 `1f2bd6312b236ca2358333b8f3c97ce6d7132bddbe5dd2d800968be23be2c90e`. All five blocking findings were accepted.

1. **Schema and cutover.** M03 now owns dual-format ledger, backup and installer validation. M15 provides write-disabled rehearsal. M16 owns qualified production activation, final legacy checkpoint, writer transfer, first-write fence and recovery.
2. **Disputes and snapshots.** M07 owns native-order proof. M08 records durable dispositions, M09 builds both journal-only and ACK-backed publication candidates, and M13 reopens the durable fenced view across processes. M14 covers export after a post-ACK dispute. Folded replacement is one publication change.
3. **Receiver recovery.** M12 durably resolves exact intents from verified receiver evidence. M14 owns the operator routes, immutable acceptance history and reconciliation. Verified absence permits only exact retry. Unknown or conflicting evidence remains held.
4. **Operational paths.** M06, M07 and M10 now name every operator or producer path. M11 exercises queued and final outcomes through the coordinator and verifies native proof before applying a scope command.
5. **Native evidence.** M04 and M05 require controlled native carrier evidence before enabling a surface. An unavailable carrier gets a named dependent slice and blocks affected qualification. M18 and M19 require two distinctly scoped Grok turns and a separate hookless eligible turn.

The ownership table now includes the shared CLI and control paths, counters and qualification files. The revised checks preserve acceptance at planning scope.
