---
schema: "aitm.story/v0"
id: 125
title: "[M15] Host service lifecycle"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/125"
parent: 100
children: []
blocking: [126]
blocked-by: [121, 124]
created: "2026-11-10T13:58:11Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M15", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "82fe21e10af9244b8bdb55f85c05dcaa16887e0027f30bd9e4bd4f7da2b79701"}
---

# [M15] Host service lifecycle

[GitHub issue #125](https://github.com/kburson/aitm/issues/125) · [Parent #100](../100/story.md) · [Accepted plan leaf M15](../100/plan/multi-project-usage-monitor-implementation-plan.md#m15-single-per-user-supervisor-on-macos-and-linux)

**Required predecessors** [M11 #121](../121/story.md), [M14 #124](../124/story.md).

Use the completed [Grok #101](https://github.com/kburson/aitm/issues/101) and [Linux #102](https://github.com/kburson/aitm/issues/102) reports as applicable. They are evidence inputs carried by the parent.

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M15. Single per-user supervisor on macOS and Linux

**Files** Create `S/host_service.py` and `T/test_monitor_install.py`. Extend `S/install.py` and `S/cli.py` lifecycle commands. Preserve the original LaunchAgent identity until guarded adoption. M15 permits isolated candidate rehearsal and a write-disabled readiness probe. Test each adopted legacy mutation refusal with no direct write or lifecycle change, including collect-once and restore between monitor transactions. The production activation path refuses without the M16 cutover receipt and exact target qualification.

**Contract** `Supervisor.install(runtime: VerifiedRuntime, state: MonitorState) -> ServiceReceipt` and `Supervisor.verify(expected: ServiceReceipt) -> ServiceHealth`. Register one per-user LaunchAgent or systemd user unit. Verify loaded definition, exact executable and same-user process incarnation plus a fresh matching heartbeat. Enable within the user manager. Report absent manager and operator-controlled lingering separately. Refuse unsupported filesystem and insecure state before activation.

- [ ] Write `test_second_service_and_legacy_writer_refuse_activation`, `test_stale_pid_and_heartbeat_do_not_certify_readiness`, and `test_no_systemd_user_bus_and_unapproved_linger_are_explicit`. Exercise isolated install, stop and restart using controlled manager fixtures.
- [ ] Run red. Implement supervisor selection and exact-runtime evidence. Run green with `test_install.py` and `test_service_process.py`. Commit M15. Real OS proofs occur in M18 and M19.
