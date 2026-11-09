# Live Codex Desktop marker diagnostic

On 2026-11-09T22:12:46.040016+00:00, the installed collector from [PR #97](https://github.com/kburson/aitm/pull/97) was exercised in isolated #96 state with real Codex Desktop 0.167.0-alpha.3.2 records. The actual tool source had 287 bytes. The exact canonical wrapper had 286. The extra byte was one final ASCII line feed, repeated by an independent single-line tool call. The native tool output matched the original queued command.

| Isolated observation | Result |
| --- | --- |
| Original command with source withheld | Pending, zero held sources |
| Original exact native source prefix delivered | Pending, one held source, zero admitted usage rows |
| Native measured records after the linked result | 9 |
| Exact installed marker parser | Rejected the native wrapper |

The initial capture helper did not retain its pre-poll timestamp. This evidence supports diagnosis only. The original native prefix and inbox/status evidence remain private. The temporary operator link was removed and production state and its LaunchAgent were absent. No Claude workload followed. [Scoped repair amendment](../../83/plan/usage-capture-desktop-marker-replan.md).
