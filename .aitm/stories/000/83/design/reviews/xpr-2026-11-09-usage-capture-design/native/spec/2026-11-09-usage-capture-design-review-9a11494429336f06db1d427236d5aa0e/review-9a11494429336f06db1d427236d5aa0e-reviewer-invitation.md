<!-- ai-peer-review-template version="1" digest="sha256:064952674640611160aff00e947b64de060d4a4cfe7139019eb0f24ee264aa25" -->
<!-- ai-peer-review-invitation data="ewogICJhcnRpZmFjdCI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLTgzLXVzYWdlLXJldmlldy9wbGFubmluZy8uYWl0bS9zdG9yaWVzLzAwMC84My9kZXNpZ24vdXNhZ2UtY2FwdHVyZS1kZXNpZ24ubWQiLAogICJyZXNwb25zZSI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLTgzLXVzYWdlLXJldmlldy9wbGFubmluZy8uYWl0bS9zdG9yaWVzLzAwMC84My9kZXNpZ24vcmV2aWV3cy94cHItMjAyNi0xMS0wOS11c2FnZS1jYXB0dXJlLWRlc2lnbi9uYXRpdmUvc3BlYy8yMDI2LTExLTA5LXVzYWdlLWNhcHR1cmUtZGVzaWduLXJldmlldy05YTExNDk0NDI5MzM2ZjA2ZGIxZDQyNzIzNmQ1YWEwZS9yZXZpZXctOWExMTQ5NDQyOTMzNmYwNmRiMWQ0MjcyMzZkNWFhMGUtcmV2aWV3ZXItcmVzcG9uc2UtMS5tZCIsCiAgInJldmlld19pZCI6ICJyZXZpZXctOWExMTQ5NDQyOTMzNmYwNmRiMWQ0MjcyMzZkNWFhMGUiLAogICJzY2hlbWEiOiAiYWktcGVlci1yZXZpZXcuaW52aXRhdGlvbi1yb3V0aW5nL3YxIiwKICAid29ya3NwYWNlIjogIi9Vc2Vycy9rcGJ1cnNvbi8uY29kZXgvd29ya3RyZWVzL2FpdG0tODMtdXNhZ2UtcmV2aWV3L3BsYW5uaW5nLy5zY3JhdGNoL3BlZXItcmV2aWV3L3Jldmlldy05YTExNDk0NDI5MzM2ZjA2ZGIxZDQyNzIzNmQ1YWEwZSIKfQo" -->

# Reviewer invitation

Review: `review-9a11494429336f06db1d427236d5aa0e`

Mode: `normal`

- Artifact: `/Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.aitm/stories/000/83/design/usage-capture-design.md`
- Workspace: `/Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.scratch/peer-review/review-9a11494429336f06db1d427236d5aa0e`
- Response: `/Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-response-1.md`
- Invitation: `/Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-invitation.md`
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

When the project-local broker is active, yield after each handoff; do not poll or repeat wait calls. Inspect `peer-review broker status --json` for authenticated instance state. After a failure, preserve receipts and run `peer-review broker reconcile /Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.scratch/peer-review/review-9a11494429336f06db1d427236d5aa0e --json` only when the exact recovery evidence calls for it. A broker failure never silently changes the selected reviewer or transport. If the broker is unavailable for an existing manual review, use the bounded `peer-review status /Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.scratch/peer-review/review-9a11494429336f06db1d427236d5aa0e --next` recovery path.

Role: reviewer. Join from a distinct session in the same physical worktree.

Installed join: `peer-review join /Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-invitation.md`

Installed-package join: `npx --no-install ai-peer-review join /Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.aitm/stories/000/83/design/reviews/xpr-2026-11-09-usage-capture-design/native/spec/2026-11-09-usage-capture-design-review-9a11494429336f06db1d427236d5aa0e/review-9a11494429336f06db1d427236d5aa0e-reviewer-invitation.md`

Rules of engagement:

- Edit only the exact pending reviewer response shown above.
- Do not edit the reviewed artifact, create commits, or push.
- Query `peer-review help join` instead of guessing command syntax.

Recovery: `peer-review resume /Users/kpburson/.codex/worktrees/aitm-83-usage-review/planning/.scratch/peer-review/review-9a11494429336f06db1d427236d5aa0e`
