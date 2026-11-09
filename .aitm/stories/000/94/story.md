---
schema: "aitm.story/v0"
id: 94
title: "[Usage U09] LaunchAgent install, upgrade and restore"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/94"
parent: 83
children: []
blocking: [95]
blocked-by: [93]
created: "2026-11-09T14:42:22Z"
updated: "2026-11-09T21:18:05+00:00"
last-branch: "codex/aitm-usage-u09-launch-health"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md", "plan/launch-health-recovery-jit.md", "plan/launch-health-recovery-pickup-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U09", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "2c8ee0355ced2b1edfdc1148b3c3e8d6cf95c0f161787552c5966a0465fb09a3"}
---

# [Usage U09] LaunchAgent install, upgrade and restore

[GitHub issue](https://github.com/kburson/aitm/issues/94) · [Parent #83](../83/story.md) · Review

**Required predecessors** [#93](../93/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{install,backup,cli}.py`, `tests/test_install.py`.

**Contract** `install_agent(project: Registration, executable: Path, launchctl: LaunchControl) -> InstallReceipt`, `backup(ledger: Ledger, destination: Path) -> BackupReceipt`, and `restore(source: Path, destination: Path, expected: LedgerIdentity) -> RestoreReceipt`. Plan and apply explicit install, stop and upgrade actions. Build the dedicated environment under `versions/<version>-<wheel-digest>/` from a verified wheel and a pinned absolute Python 3.13+ interpreter. Create the venv first and install the exact wheel without runtime dependency resolution. Keep the prior environment beside it through successful upgrade and receipt verification. Prune only inactive, explicitly selected versions with a retained recovery wheel and backup. Set RunAtLoad and KeepAlive. Set plist ProgramArguments to `[<absolute-aitm-usage>, "--project", <absolute-state-dir>, "service", "run"]`. Upgrade backs up state before activation and restores the previous compatible service registration on failure. Restore only into a stopped target under the same writer lock and replace state atomically after validation. Validate absolute paths, ownership and installed version. Use the SQLite backup API and capture the associated private pseudonym key in the same protected backup bundle. Verify project/key identity before restore. Preserve ledger and key when stopping or uninstalling.

- [ ] Write `test_owned_launchagent_and_recoverable_upgrade` with a fake launchctl and temporary state. Check correct plist paths, RunAtLoad, KeepAlive and 15-second polling, idempotent install, failure before activation and failure of the new launch leaving the prior service recoverable, stop and uninstall preserving data, wrong-key and wrong-project restore refusal, and stable pseudonyms and same-cutoff export parity after a supported restore with the backed-up key. Use two side-by-side wheel environments to verify rollback restores the previous plist path after a failed new launch. Scan the protected backup bundle bytes except the known secret key for canaries. V1 supports same-schema version changes and refuses other schema versions before mutation.
- [ ] Run `test_install.py` to show failure, implement installation and backup operations, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Launch health producer amendment under review](../83/plan/usage-capture-launch-health-replan.md). The #94 source candidate is preserved pending exact process-attribution proof.

[Reviewed launch health recovery pickup](plan/launch-health-recovery-jit.md) · [Independent acceptance](plan/launch-health-recovery-pickup-review.md). The rejected original candidate remains preserved.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.
