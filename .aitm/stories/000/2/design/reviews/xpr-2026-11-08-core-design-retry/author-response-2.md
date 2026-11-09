---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "author"
round: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "63c7e85d66153db6dc03e5aa41fc8d8191845632"
artifact_digest: "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6-astra"
  effort: "xhigh"
author_session: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T06:13:39.559Z"
submitted_at: "2026-11-09T06:18:53.686Z"
start_basis: "prior-submit"
start_source: "reviewer-response-2.md"
finding_ids: []
answered_finding_ids: ["R2-F001", "R2-F002"]
patch: "patch-002.diff"
native_source: "native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-author-response-2.md"
native_source_digest: "sha256:bf7423adb219ee80e95ab44a4f02f9a4fda67459a94a649558cbb2e49362f866"
---

Mode: `normal`

## Summary

Addressed both required round-2 findings and all three optional suggestions. The revision makes verification assurance a declared policy choice with a usable captured-export route, defines preparation and cache handling, and explicitly classifies the identity-issuing backlog provider/namespace as an anchor.

## Finding dispositions

- **R2-F001 — accepted.** The design now defines captured-export and contained assurance separately. Both run a private copied source/input export; captured-export proves isolation from other worktree writers and reports its limits for arbitrary command self-mutation, undeclared reads and network. Contained adds the capability-probed OS process-tree restrictions. A committed policy explicitly selects the permitted level; the example selects captured-export, so OS containment is not a universal closure prerequisite. No silent downgrade is allowed. The receipt and acceptance tests carry the actual assurance, and the general verification paragraph no longer promises a stronger guarantee than the selected lane provides.

  Added aitm test prepare, test prepare --offline, the separate prepare_network policy, lock-hash-verified cache reuse, stale-environment rejection and exact preparation-unavailable guidance. The default execution records environment selection, no-sync/offline uv behavior, bytecode suppression and writable pytest cache redirection. The core-only nominal fixture uses explicitly policy-accepted captured-export, while separate platform fixtures prove contained behavior and its unavailable path.
- **R2-F002 — accepted.** Backlog identity issuer and repository/numbering namespace are anchor/routing fields requiring verified init --reconfigure. That adoption must retain existing issued IDs/provider references. Non-identity provider settings, including githost, are tip-effective; changing githost cannot redirect the independently anchored store remote/ref.

Optional suggestions:
- **O1 — accepted.** Moved bootstrap recovery after the init sequence and removed the unexplained direct fetch from another initializing clone. That clone's verifying rerun publishes the retained objects; other clones report bootstrap-pending, or an explicit reconfiguration replaces an irretrievable unissued proposal through the normal anchored default-branch path.
- **O2 — accepted.** Recorded PYTHONDONTWRITEBYTECODE and pytest cache_dir redirection into writable output storage for the default command transformation.
- **O3 — accepted.** Init/doctor report the chosen lane's readiness, the deprecated macOS sandbox-exec dependency and specific unavailable Linux namespace/mount/profile capabilities. This is diagnosis; no command changes global host security settings.

## Changes made

Replaced the single mandatory containment lane with a policy-governed assurance table, rewrote the shared verification contract to match the actual promise, added preparation to the CLI and config example, expanded the test-receipt assurance metadata, and aligned the acceptance matrix. The original policy split now includes providers and preserves numbering continuity.

Captured-export does not claim that chmod by arbitrary same-user test code is impossible or that before/after hashes prove no transient self-edit. Those are explicitly outside that assurance. The core still refuses an observed contract violation or a receipt too weak for current policy. Original-checkout edits cannot change the separately copied run inputs. This provides a truthful weaker-assurance route rather than relabeling a failed containment probe.

No owner-open limit, review-depth choice, expansion interpretation or hosted-audit choice changed. No implementation was performed.

## Declined changes and rationale

None. Both required findings and all optional suggestions are resolved in the revised text. The platform-specific facts are not used to claim any implementation test has passed.

## Verification

- Re-read the full round-2 response and checked both findings against the affected configuration, guard, preparation, CLI and acceptance sections.
- Checked the installed macOS sandbox-exec manual, which explicitly marks it deprecated.
- Checked the primary [pytest cache_dir documentation](https://docs.pytest.org/en/stable/reference/reference.html#confval-cache_dir), plus the already cited uv environment and lock/sync documentation, for the default command's stated controls.
- Checked FUR/response whitespace, frontmatter and relative links; searched for stale mandatory-containment wording, the old preparation network key and provider-classification omissions.
- Only the FUR and this pending native author-response body are revised. Protected native frontmatter and previous responses are retained. Native submit owns the revision commit.
- Round 3 must again review the full current FUR, including assurance limits and the complete acceptance matrix. Runtime acceptance remains future implementation work.
