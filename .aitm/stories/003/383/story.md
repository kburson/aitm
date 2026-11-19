---
schema: "aitm.story/v0"
id: 383
title: "Implement an affected-test probe for the index, HEAD, and PR trees"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/383"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T14:06:37Z"
updated: "2026-11-19T15:03:10Z"
last-branch: "trunk"
estimate: {"agent-hours": null, "size": null}
priority: "P2"
origin: ".aitm/stories/003/371/plan/2026-11-19-371-portable-python-tia-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-19-383-advisory-probe.md", "plan/reviews/2026-11-19-383-independent-source-review.md", "plan/2026-11-19-383-qualification.md", "plan/2026-11-19-383-qualification.json", "plan/trusted-pr-384.json"], "attachments": []}
expansions: []
trips: []
---

# Implement an affected-test probe for the index, HEAD, and PR trees

[GitHub issue #383](https://github.com/kburson/aitm/issues/383) · [Parent #370](../370/story.md) · [Accepted #371 finding](../371/plan/2026-11-19-371-portable-python-tia-findings.md).

Implement one read-only affected-test probe in Python for exact staged index, HEAD, and pull-request snapshots. Use Ubuntu as the reference and macOS as the same-source portability cross-check.

## Scope

- Resolve an explicit branch divergence point. Read index blobs and modes without including unstaged or untracked changes. Read a HEAD tree without consulting the index or working tree. Bind the PR base, head, and tested tree distinctly and refuse incorrect or ambiguous authority.
- Reuse the existing snapshot, Python file graph, and selection/inventory validation. Report exact input identities, platform-scoped pytest IDs, path-to-test witnesses and uncertainty. File-level evidence can cover an imported function through its owning module. Require additional evidence before narrowing within a module.
- Return the full applicable inventory when a safe narrow assignment cannot be established. Report unavailable when the exact input or required inventory is missing. Keep the probe advisory.

## Acceptance

1. Show a controlled direct and transitive source change. The selected tests and exact full Ubuntu control both catch a seeded regression. Preserve the compared endpoint, inventory, witnesses, and outcomes.
2. Show that index mode excludes unstaged and untracked edits, HEAD excludes local changes, and incorrect PR tree or parent identity is refused. Exercise renamed or deleted inputs across both graph sides.
3. Show an unresolved dependency that selects full, and missing inventory that refuses selection. Repeat with the same CPython source on macOS and explain platform-specific test inventory.
4. Deliver a reviewed probe receipt. Keep the hosted path map, workflow, merge authority, and #355 pinned advisory command in their existing roles. Hosted integration has its own later decision.

[Accepted #371 finding](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/371/plan/2026-11-19-371-portable-python-tia-findings.md) · [Parent #370](https://github.com/kburson/aitm/issues/370).

[Delivery sign-off](retro/2026-11-19-383-delivery.md) · [Merge PR #384](https://github.com/kburson/aitm/pull/384).
