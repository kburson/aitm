<!-- ai-peer-review-template version="1" digest="sha256:064952674640611160aff00e947b64de060d4a4cfe7139019eb0f24ee264aa25" -->
<!-- ai-peer-review-invitation data="ewogICJhcnRpZmFjdCI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLWNvcmUtcGxhbi1mdWxsZmlsZS9wbGFubmluZy8uYWl0bS9zdG9yaWVzLzAwMC8yL3BsYW4vY29yZS1pbXBsZW1lbnRhdGlvbi1wbGFuLm1kIiwKICAicmVzcG9uc2UiOiAiL1VzZXJzL2twYnVyc29uLy5jb2RleC93b3JrdHJlZXMvYWl0bS1jb3JlLXBsYW4tZnVsbGZpbGUvcGxhbm5pbmcvLmFpdG0vc3Rvcmllcy8wMDAvMi9wbGFuL3Jldmlld3MveHByLTIwMjYtMTEtMDktY29yZS1wbGFuLWZ1bGxmaWxlL25hdGl2ZS9wbGFuLzIwMjYtMTEtMDktY29yZS1pbXBsZW1lbnRhdGlvbi1wbGFuLXJldmlldy0wOWU0MjQ2YmZhNGNhYTVmZWZmMTU5MmRlOWYyMjQ5Yy9yZXZpZXctMDllNDI0NmJmYTRjYWE1ZmVmZjE1OTJkZTlmMjI0OWMtcmV2aWV3ZXItcmVzcG9uc2UtMS5tZCIsCiAgInJldmlld19pZCI6ICJyZXZpZXctMDllNDI0NmJmYTRjYWE1ZmVmZjE1OTJkZTlmMjI0OWMiLAogICJzY2hlbWEiOiAiYWktcGVlci1yZXZpZXcuaW52aXRhdGlvbi1yb3V0aW5nL3YxIiwKICAid29ya3NwYWNlIjogIi9Vc2Vycy9rcGJ1cnNvbi8uY29kZXgvd29ya3RyZWVzL2FpdG0tY29yZS1wbGFuLWZ1bGxmaWxlL3BsYW5uaW5nLy5zY3JhdGNoL3BlZXItcmV2aWV3L3Jldmlldy0wOWU0MjQ2YmZhNGNhYTVmZWZmMTU5MmRlOWYyMjQ5YyIKfQo" -->

# Reviewer invitation

Review: `review-09e4246bfa4caa5feff1592de9f2249c`

Mode: `normal`

- Artifact: `/Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.aitm/stories/000/2/plan/core-implementation-plan.md`
- Workspace: `/Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.scratch/peer-review/review-09e4246bfa4caa5feff1592de9f2249c`
- Response: `/Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-response-1.md`
- Invitation: `/Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-invitation.md`
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

When the project-local broker is active, yield after each handoff; do not poll or repeat wait calls. Inspect `peer-review broker status --json` for authenticated instance state. After a failure, preserve receipts and run `peer-review broker reconcile /Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.scratch/peer-review/review-09e4246bfa4caa5feff1592de9f2249c --json` only when the exact recovery evidence calls for it. A broker failure never silently changes the selected reviewer or transport. If the broker is unavailable for an existing manual review, use the bounded `peer-review status /Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.scratch/peer-review/review-09e4246bfa4caa5feff1592de9f2249c --next` recovery path.

Role: reviewer. Join from a distinct session in the same physical worktree.

Installed join: `peer-review join /Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-invitation.md`

Installed-package join: `npx --no-install ai-peer-review join /Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-invitation.md`

Rules of engagement:

- Edit only the exact pending reviewer response shown above.
- Do not edit the reviewed artifact, create commits, or push.
- Query `peer-review help join` instead of guessing command syntax.

Recovery: `peer-review resume /Users/kpburson/.codex/worktrees/aitm-core-plan-fullfile/planning/.scratch/peer-review/review-09e4246bfa4caa5feff1592de9f2249c`
