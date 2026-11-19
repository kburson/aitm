---
schema: "aitm.story/v0"
id: 375
title: "Refuse an extra file grant without a macOS ACL"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/375"
parent: 372
children: []
blocking: []
blocked-by: [377]
created: "2026-11-18T23:38:27Z"
updated: "2026-11-19T04:20:33Z"
last-branch: "trunk"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Refuse an extra file grant without a macOS ACL

[GitHub issue #375](https://github.com/kburson/aitm/issues/375) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 520. Priority P2. Size S. Estimate 3 agent-hours.

#377 has moved the required Python jobs to Linux. This pull request runs on that suite.

`host_fs.check_private_acl` does all of the following.

- An absent ACL is success. On Darwin the text is `!#acl 1\n`. On Linux `system.posix_acl_access` is absent, and on a directory `system.posix_acl_default` is absent.
- A grant is a refusal, reported as `Unsafe private ACL`. A present Linux ACL xattr is a grant. Any Darwin ACE is a grant except the one ancestor ACE below.
- An ancestor that carries only the stock macOS home deny-delete ACE still passes. The accepted text is `!#acl 1\n` followed by `group:ABCDEFAB-CDEF-ABCD-EFAB-CDEF0000000C:everyone:12:deny:delete`. That ACE is allowed on ancestors only. The same ACE on the private file is a refusal. Any other ACE on an ancestor is a refusal.
- An inconclusive read is a refusal. A missing ACL reader, a failed `acl_get_link_np`, `acl_get_fd_np`, or `getxattr`, or ACL text that cannot be classified stays a refusal: `Private ACL validation is unavailable`, `Unable to validate private ACL`, or `Unable to classify private ACL`.
- The control directory stays `~/Library/Application Support/aitm-usage-control` on Darwin and `~/.local/state/aitm-usage-control` on Linux.

The required suite does not run `chmod +a`. Deleting the `native-acl` capability from `tools/ci/tia/suites.json` belongs to #376.

