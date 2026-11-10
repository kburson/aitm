---
schema: "aitm.story/v0"
id: 111
title: "[M01] Host path security"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/111"
parent: 100
children: []
blocking: [112]
blocked-by: []
created: "2026-11-10T13:57:48Z"
updated: "2026-11-10T14:26:01+00:00"
last-branch: "planning"
estimate: {"agent-hours": 2.5, "size": "S"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/jit.md", "plan/jit-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M01", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "1ca9420de1ab889e868a4bc2a5d392de7355fdbe303d53b54dba5f145a998391"}
---

# [M01] Host path security

[GitHub issue #111](https://github.com/kburson/aitm/issues/111) · [Parent #100](../100/story.md) · [Accepted plan leaf M01](../100/plan/multi-project-usage-monitor-implementation-plan.md#m01-host-path-security)

**Required predecessors** None.

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M01. Host path security

**Files** Create `S/host_fs.py` and `T/test_host_fs_security.py`. Modify private-path validation and per-user guard location in `S/ledger.py`.

**Contract** `check_private_acl(target: Path | int, *, ancestor: bool = False) -> None` and `account_control_root(uid: int) -> Path` in `host_fs`. Keep Darwin ancestry rules and POSIX fd-relative checks. Use checked ctypes where the standard library lacks native ACL bindings. On Linux inspect access and default ACLs separately and use a stable UID-resolved account root independent of environment overrides.

- [ ] Write `test_private_acl_rejects_linux_default_acl_and_unknown_enforcement`, `test_pinned_path_rejects_symlink_and_wrong_owner` and `test_uid_guard_ignores_home_override`. Assert `0700` with a permissive default ACL fails and an unavailable ACL capability refuses state admission.
- [ ] Run the named file to show red. Implement the checked OS boundary and run green with `test_ledger.py`. Exercise real ACL enforcement on the qualified Linux volume. Commit only M01 paths.

[Reviewed design, estimate, plan and exact pickup](plan/jit.md) · [Independent review](plan/jit-review.md).
