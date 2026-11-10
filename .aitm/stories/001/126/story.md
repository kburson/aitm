---
schema: "aitm.story/v0"
id: 126
title: "[M16] Backup, legacy adoption and rollback"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/126"
parent: 100
children: []
blocking: [127]
blocked-by: [122, 124, 125]
created: "2026-11-10T13:58:13Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M16", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "e78b684bee548b914ff2cb62bc1d688f03f9be55e01103d9e4b802ea9ee64166"}
---

# [M16] Backup, legacy adoption and rollback

[GitHub issue #126](https://github.com/kburson/aitm/issues/126) · [Parent #100](../100/story.md) · [Accepted plan leaf M16](../100/plan/multi-project-usage-monitor-implementation-plan.md#m16-coordinated-backup-legacy-adoption-and-rollback)

**Required predecessors** [M12 #122](../122/story.md), [M14 #124](../124/story.md), [M15 #125](../125/story.md).

Apply the accepted plan’s [legacy command surface after adoption](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#legacy-command-surface-after-adoption).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M16. Coordinated backup, legacy adoption and rollback

**Files** Extend `S/backup.py`, `S/monitor_recovery.py`, `S/install.py` and `S/cli.py`. Add `T/test_monitor_cutover.py`.

**Contract** `capture_monitor_backup(store: MonitorStore, destination: Path) -> MonitorBackupReceipt` and `adopt_legacy(request: LegacyAdoption, receipt: MonitorBackupReceipt) -> LegacyBaseline`. Back up the journal, keys and ledger vector with pending routes. Verify the separate current recovery tail. Adopt the existing UUID, key, cutoff and ledger sequence under the original writer guard. Fence new projects behind proven enrollment baselines and reconcile provider activity during stop exactly once. `CutoverController.activate(request: ApprovedCutover, qualification: TargetQualification) -> ActivationReceipt` owns the ordered sequence. Confirm exact runtime and target qualification, verify independent recovery currentness, capture and verify the legacy backup, stop legacy collection, acquire the original guard, confirm the final checkpoint and frozen export, then verify the rollback bundle matches that stopped checkpoint. If the legacy writer advanced after backup, capture and verify a matching replacement bundle under the guard or refuse before schema migration. Record and transfer exact pending legacy commands and freeze ingress, then adopt the schema under the guard and verify the replacement in write-disabled readiness mode. Install production hooks only within the authorized cutover. Rollback removes exact owned hook entries and preserves foreign changes. If an owned entry cannot be safely removed, prove it inert under legacy service and record it. Enable writes only after the authorized cutover receipt binds those results. Before enabling writes, persist the adopted project ledger identities, head sequences and journal checkpoint as the rollback fence. Recovery checks the guarded durable project and journal state against that fence. A project commit beyond the fence is a write even if ACK or a separate marker was interrupted. Restore and restart legacy only when the absence of new durable usage writes and publication is proven. If a write exists or absence cannot be verified, preserve the state and require proven compatible rollback or forward recovery. A portable restore needs independently authenticated current-tail evidence outside the restored material.

- [ ] Write `test_cutover_first_report_and_fixed_export_parity`, `test_copied_pre_cutover_archive_cannot_reach_other_project`, `test_older_backup_before_handoff_and_accepted_export_holds_or_reconciles`, and `test_reversible_prewrite_failure_and_postwrite_forward_recovery`. Add `test_legacy_write_between_backup_and_stop_survives_cutover_failure` and `test_first_project_commit_without_ack_prevents_legacy_restore`. Add `test_pending_legacy_commands_apply_once_and_native_mark_remains_live`, `test_post_cutover_revision_updates_legacy_row_once`, `test_codex_counter_epoch_continues_across_cutover` and `test_legacy_restore_leaves_owned_hooks_removed_or_inert`. Verify frozen export bytes after each continuity case. Ambiguous lineage, mixed generations, missing independent tail and unverifiable post-fence state fail closed.
- [ ] Run red. Implement dry-run validation, staged restore and adoption checks. Rehearse on copied representative #83 state, including rollback before new writes and recovery of pending routes. Run green with `test_monitor_recovery_fence.py`, `test_install.py` and `test_export.py`. Commit M16.
