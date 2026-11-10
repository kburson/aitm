---
schema: "aitm.story/v0"
id: 112
title: "[M02] Atomic filesystem operations"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/112"
parent: 100
children: []
blocking: [113]
blocked-by: [111]
created: "2026-11-10T13:57:49Z"
updated: "2026-11-10T14:40:17+00:00"
last-branch: "planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/jit.md", "plan/jit-review.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M02", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "1cb81c44265b11f433754cac28acfa72c278fcb0fa278333cca962926e164056"}
---

# [M02] Atomic filesystem operations

[GitHub issue #112](https://github.com/kburson/aitm/issues/112) · [Parent #100](../100/story.md) · [Accepted plan leaf M02](../100/plan/multi-project-usage-monitor-implementation-plan.md#m02-atomic-publication-and-restore-operations)

**Required predecessors** [M01 #111](../111/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M02. Atomic publication and restore operations

**Files** Extend `S/host_fs.py` and add `T/test_host_fs_publication.py`. Move native call sites in `S/scopes.py`, `S/service.py`, `S/export.py`, `S/backup.py` and `S/install.py` onto it.

**Contract** `publish_noreplace(src_dir: int, src: str, dst_dir: int, dst: str) -> bool` and `exchange_entries(src_dir: int, src: str, dst_dir: int, dst: str) -> None`. Keep exclusive file and directory publication, collision replay, atomic restore exchange and parent directory fsync. Probe `RENAME_EXCHANGE` separately because #102 exercised `RENAME_NOREPLACE` only.

- [ ] Write `test_existing_destination_survives_noreplace`, `test_directory_exchange_and_durability` and `test_unsupported_primitive_fails_without_replacement`. Assert EEXIST preserves both inode identities and a refused exchange leaves the original store intact.
- [ ] Run red. Wire native Darwin and Linux operations through checked ctypes bindings. Run green with `test_scopes.py`, `test_export.py` and `test_install.py`, including real supported filesystem runs. Commit M02.

[Reviewed design, estimate, plan and exact pickup](plan/jit.md) · [Independent review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md).
