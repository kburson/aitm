# Preserved blocked native SPR attempt

This is provenance for a separate unsuccessful native attempt, not a reviewer response or acceptance. The owner explicitly authorized the following manual SPR after the native join remained blocked: “Use the same manual SPR process as story 01 for the core design, with Astra-6/ExtraHigh as author and GPT-6.1 Sol/high as reviewer. Preserve the blocked native attempt, publish the results, and stop before XPR.”

## Native attempt

- Review ID: `review-17297d5a4b119945bd8a26971509b636`.
- Tool: `@kburson/ai-peer-review` 0.4.1; SPR, project-local broker, manual invitation transport, normal commit mode, authority assurance unavailable.
- Artifact/base: `.aitm/stories/000/2/design/core-design.md` at planning `73210b6da93942f06a0d6616cf5df02eaf64180c`.
- Raw input SHA-256: `d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9`.
- Selected author/reviewer: `gpt-6-astra` / `xhigh` and `gpt-6.1-sol` / `high`.
- Last verified state before the manual review: `awaiting-reviewer`, reviewer `unclaimed`, protocol event revision 1. No submitted reviewer response, artifact revision, native acceptance or finalization.

The collaboration-session join failed `APR_CODEX_HOOK_INVALID` because the hook observed the parent without the child runtime evidence. A genuine separate Codex CLI reviewer then encountered `APR_INTERNAL` (`uv_uptime` denied by its sandbox). Normal command escalation was rejected by automatic approval, which treated the trusted hook's automatically inserted identity fields as a manual identity override. The reviewer supplied only the literal sealed join command. Read-only checks confirmed its genuine session and the hook-generated fields. The same-session retry was rejected again after the owner explicitly authorized that trusted-hook join. No checks or identities were bypassed.

## Retention and separation

The original worktree `/Users/kpburson/.codex/worktrees/aitm-architecture-spr/planning` and branch `review/2-core-design-spr` retain the original native output, setup, hook records and private runtime/retry evidence. The local recovery handoff is `.scratch/core-spr-cli/recovery-handoff.md`. A local before/after digest inventory verifies the native files remain unchanged during this manual cycle. Private scratch, tokens, provider handles and setup files are excluded from planning publication.

This manual review runs in a different worktree and collateral folder from that attempt. Its outcome does not change the native attempt's state or claim native tool acceptance, abandonment, supersession or repair. No native join or submission is used for the manual review. The blocked worktree is retained when the manual worktree is cleaned up.

## Public native-original fingerprints

These files remain at their original location under the retained worktree; they are not part of the manual review's round sequence. A pending template is not a submitted review.

| Original basename | SHA-256 |
| --- | --- |
| review-17297d5a4b119945bd8a26971509b636-author-startup.md | sha256:17ee4ab372af4bb29c0a39bb913e641f670f70e1d9a31e91d6b421e23d519e40 |
| review-17297d5a4b119945bd8a26971509b636-reviewer-invitation.md | sha256:9c6a2487dc2b2bfbc64afc308d062e90ded02e1d6323f62fb4a03a7927241d4d |
