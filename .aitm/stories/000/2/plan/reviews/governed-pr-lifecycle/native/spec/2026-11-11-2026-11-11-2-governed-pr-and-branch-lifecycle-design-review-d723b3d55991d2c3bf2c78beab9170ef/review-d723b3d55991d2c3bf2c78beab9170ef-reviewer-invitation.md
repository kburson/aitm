<!-- ai-peer-review-template version="1" digest="sha256:064952674640611160aff00e947b64de060d4a4cfe7139019eb0f24ee264aa25" -->
<!-- ai-peer-review-invitation data="ewogICJhcnRpZmFjdCI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLTE1OC1ldmlkZW5jZS90cnVuay8uYWl0bS9zdG9yaWVzLzAwMC8yL2Rlc2lnbi8yMDI2LTExLTExLTItZ292ZXJuZWQtcHItYW5kLWJyYW5jaC1saWZlY3ljbGUtZGVzaWduLm1kIiwKICAicmVzcG9uc2UiOiAiL1VzZXJzL2twYnVyc29uLy5jb2RleC93b3JrdHJlZXMvYWl0bS0xNTgtZXZpZGVuY2UvdHJ1bmsvLmFpdG0vc3Rvcmllcy8wMDAvMi9wbGFuL3Jldmlld3MvZ292ZXJuZWQtcHItbGlmZWN5Y2xlL25hdGl2ZS9zcGVjLzIwMjYtMTEtMTEtMjAyNi0xMS0xMS0yLWdvdmVybmVkLXByLWFuZC1icmFuY2gtbGlmZWN5Y2xlLWRlc2lnbi1yZXZpZXctZDcyM2IzZDU1OTkxZDJjM2JmMmM3OGJlYWI5MTcwZWYvcmV2aWV3LWQ3MjNiM2Q1NTk5MWQyYzNiZjJjNzhiZWFiOTE3MGVmLXJldmlld2VyLXJlc3BvbnNlLTEubWQiLAogICJyZXZpZXdfaWQiOiAicmV2aWV3LWQ3MjNiM2Q1NTk5MWQyYzNiZjJjNzhiZWFiOTE3MGVmIiwKICAic2NoZW1hIjogImFpLXBlZXItcmV2aWV3Lmludml0YXRpb24tcm91dGluZy92MSIsCiAgIndvcmtzcGFjZSI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLTE1OC1ldmlkZW5jZS90cnVuay8uc2NyYXRjaC9wZWVyLXJldmlldy9yZXZpZXctZDcyM2IzZDU1OTkxZDJjM2JmMmM3OGJlYWI5MTcwZWYiCn0K" -->

# Reviewer invitation

Review: `review-d723b3d55991d2c3bf2c78beab9170ef`

Mode: `normal`

- Artifact: `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md`
- Workspace: `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.scratch/peer-review/review-d723b3d55991d2c3bf2c78beab9170ef`
- Response: `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-response-1.md`
- Invitation: `/Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-invitation.md`
- Reviewer: `claude-opus-5-5` (`claude-opus-5-5`), effort: `high`
- Runtime: XPR, project-local broker

## Communication policy (v1)

Keep all peer-review chat messages terse. Put complete review analysis, findings, dispositions, revised prose, rationale, decisions, and verification evidence in the generated durable review documents.

Chat may contain only:

- a short operational status;
- a pointer to the relevant durable document;
- the exact next action; or
- a concise blocker requiring human action.

Read the relevant durable reviewer or author response document; do not rely on a chat summary. Do not paste findings, dispositions, revised prose, verification output, or other durable document content into chat unless the human explicitly requests it.

“Terse chat” does not mean terse review evidence. Durable reviewer and author response documents remain complete, self-contained, and authoritative.

## Project-local broker and recovery

Phased sessions remain event-authoritative. After a non-final acceptance, the registered author finalizes and advances the exact next artifact; resume only from the generated reviewer response and never infer or skip a phase from chat.

When the project-local broker is active, yield after each handoff; do not poll or repeat wait calls. Inspect `peer-review broker status --json` for authenticated instance state. After a failure, preserve receipts and run `peer-review broker reconcile /Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.scratch/peer-review/review-d723b3d55991d2c3bf2c78beab9170ef --json` only when the exact recovery evidence calls for it. A broker failure never silently changes the selected reviewer or transport. If the broker is unavailable for an existing manual review, use the bounded `peer-review status /Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.scratch/peer-review/review-d723b3d55991d2c3bf2c78beab9170ef --next` recovery path.

Role: reviewer. Join from a distinct session in the same physical worktree.

Installed join: `peer-review join /Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-invitation.md`

Installed-package join: `npx --no-install ai-peer-review join /Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.aitm/stories/000/2/plan/reviews/governed-pr-lifecycle/native/spec/2026-11-11-2026-11-11-2-governed-pr-and-branch-lifecycle-design-review-d723b3d55991d2c3bf2c78beab9170ef/review-d723b3d55991d2c3bf2c78beab9170ef-reviewer-invitation.md`

Rules of engagement:

- Edit only the exact pending reviewer response shown above.
- Do not edit the reviewed artifact, create commits, or push.
- Query `peer-review help join` instead of guessing command syntax.

Recovery: `peer-review resume /Users/kpburson/.codex/worktrees/aitm-158-evidence/trunk/.scratch/peer-review/review-d723b3d55991d2c3bf2c78beab9170ef`
