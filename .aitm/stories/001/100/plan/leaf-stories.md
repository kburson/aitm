# #100 implementation backlog

[Accepted plan](multi-project-usage-monitor-implementation-plan.md) · publication `be326aa06bbf0180969ecadb8df74cf4a37a62c4` · SHA-256 `8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21`.

GitHub readback at `2026-11-10T14:00:46Z` verified 19 open Backlog items, all 19 native parent links to #100 and the same 24 direct dependencies in both directions. The two completed research dependencies remain linked to #100. The [verification receipt](leaf-issue-receipt.json) records exact issue and Project item identities.

| Plan leaf | Story | Required predecessors |
| --- | --- | --- |
| [M01](multi-project-usage-monitor-implementation-plan.md#m01-host-path-security) | [#111 Host path security](../../111/story.md) | None |
| [M02](multi-project-usage-monitor-implementation-plan.md#m02-atomic-publication-and-restore-operations) | [#112 Atomic filesystem operations](../../112/story.md) | [M01 #111](../../111/story.md) |
| [M03](multi-project-usage-monitor-implementation-plan.md#m03-versioned-project-persistence) | [#113 Versioned project persistence](../../113/story.md) | [M02 #112](../../112/story.md) |
| [M04](multi-project-usage-monitor-implementation-plan.md#m04-adapter-contract-and-codex-or-claude-bridge) | [#114 Adapter contract and existing providers](../../114/story.md) | [M03 #113](../../113/story.md) |
| [M05](multi-project-usage-monitor-implementation-plan.md#m05-grok-whole-turn-adapter) | [#115 Grok evidence adapter](../../115/story.md) | [M04 #114](../../114/story.md) |
| [M06](multi-project-usage-monitor-implementation-plan.md#m06-explicit-registrations-and-capture-epochs) | [#116 Registry and capture epochs](../../116/story.md) | [M04 #114](../../114/story.md) |
| [M07](multi-project-usage-monitor-implementation-plan.md#m07-authenticated-scope-handoff-and-proof-holds) | [#117 Native scope and handoff](../../117/story.md) | [M06 #116](../../116/story.md) |
| [M08](multi-project-usage-monitor-implementation-plan.md#m08-single-owner-journal-and-verified-revision-order) | [#118 Service journal and claim order](../../118/story.md) | [M07 #117](../../117/story.md) |
| [M09](multi-project-usage-monitor-implementation-plan.md#m09-guarded-destination-writes-and-ack) | [#119 Project writes and ACK](../../119/story.md) | [M08 #118](../../118/story.md) |
| [M10](multi-project-usage-monitor-implementation-plan.md#m10-private-wake-ingress-and-parked-session-scheduling) | [#120 Wake and park scheduler](../../120/story.md) | [M05 #115](../../115/story.md), [M09 #119](../../119/story.md) |
| [M11](multi-project-usage-monitor-implementation-plan.md#m11-shared-root-watchers-and-coordinator) | [#121 Root watches and coordinator](../../121/story.md) | [M05 #115](../../115/story.md), [M10 #120](../../120/story.md) |
| [M12](multi-project-usage-monitor-implementation-plan.md#m12-independent-recovery-and-publication-fence) | [#122 Recovery and publication fence](../../122/story.md) | [M09 #119](../../119/story.md) |
| [M13](multi-project-usage-monitor-implementation-plan.md#m13-pinned-project-and-story-reports) | [#123 Snapshot reports](../../123/story.md) | [M11 #121](../../121/story.md), [M12 #122](../../122/story.md) |
| [M14](multi-project-usage-monitor-implementation-plan.md#m14-versioned-exports-and-immutable-receiver-compatibility) | [#124 Compatible export and reconciliation](../../124/story.md) | [M13 #123](../../123/story.md) |
| [M15](multi-project-usage-monitor-implementation-plan.md#m15-single-per-user-supervisor-on-macos-and-linux) | [#125 Host service lifecycle](../../125/story.md) | [M11 #121](../../121/story.md), [M14 #124](../../124/story.md) |
| [M16](multi-project-usage-monitor-implementation-plan.md#m16-coordinated-backup-legacy-adoption-and-rollback) | [#126 Backup, legacy adoption and rollback](../../126/story.md) | [M12 #122](../../122/story.md), [M14 #124](../../124/story.md), [M15 #125](../../125/story.md) |
| [M17](multi-project-usage-monitor-implementation-plan.md#m17-cross-project-privacy-saturation-and-scale-proof) | [#127 Privacy and scale integration](../../127/story.md) | [M16 #126](../../126/story.md) |
| [M18](multi-project-usage-monitor-implementation-plan.md#m18-controlled-macos-qualification) | [#128 Native macOS qualification](../../128/story.md) | [M17 #127](../../127/story.md) |
| [M19](multi-project-usage-monitor-implementation-plan.md#m19-controlled-linux-qualification-and-delivery-gate) | [#129 Native Linux qualification](../../129/story.md) | [M18 #128](../../128/story.md) |

The child set follows the exact accepted plan. Individual estimates and leaf-specific gates are recorded at refinement and pickup.

## M04 pickup split

[#134 M04-LC](../../134/story.md) and [#135 M04-LA](../../135/story.md) were added under #100 after the original 19-leaf inventory. Both require #114 and block #129. [Verified split](../../114/plan/linux-carrier-split.json).
