# #272 native buffered prefix findings

The accepted admission plan requires an authenticated live arm of the original Claude child transcript before its first API request. The work used pinned Claude Code macOS 2.1.318 and literal trunk `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`.

Two fresh disposable runs used an approved, enabled child root, a prospectively enrolled parent and the stream-json process carrier. Before dispatch the child directory was empty. A macOS kqueue directory watcher and a tight reader observed the same original child file. In both runs each observer's first complete prefix held rows 0–9. Row 9 was the first native API request record. After process exit the original file identity and exact early prefix matched, and the scratch registry still held only the parent epoch. Neither trial exposed an eligible pre-request prefix to arm.

The pinned producer trace explains this observation. The foreground runner invokes SubagentStart before it queues the initial child transcript. It does not await persistence of that append before starting the query. The request recorder queues its records during query setup before the provider dispatch path. Both kinds of records use the same per-file queue and the local writer can combine them in one append. The default queue drain interval in the pinned build is 100 ms. The pinned ranges and artifact hashes are in the attached receipt. The earlier scratch SubagentStart control saw no child file to arm.

These runs establish that neither observer produced a qualifying arm for this build and workload. A transport pause after the first native request is recorded cannot recover the earlier arm. A qualifying carrier must expose a complete original child prefix and give the live writer an opportunity to arm it before the first request. No child epoch or paired ownership proof was issued. #273 remains blocked on #272, and #204's JIT awaits both original owners. #204 continues to block #119.

[Two live trials and pinned source ranges](native-pre-request-timing.json) · [Earlier lifecycle control](pre-request-arm-controls.json) · [Independently accepted plan](2026-11-12-272-claude-admission-reacceptance-r2.md)
