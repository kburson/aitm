<!-- ai-peer-review-template version="1" digest="sha256:064952674640611160aff00e947b64de060d4a4cfe7139019eb0f24ee264aa25" -->
<!-- ai-peer-review-invitation data="ewogICJhcnRpZmFjdCI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLTgzLXVzYWdlLWxhdW5jaC1oZWFsdGgtcmV2aWV3L3RydW5rLy5haXRtL3N0b3JpZXMvMDAwLzgzL3BsYW4vdXNhZ2UtY2FwdHVyZS1sYXVuY2gtaGVhbHRoLXJlcGxhbi5tZCIsCiAgInJlc3BvbnNlIjogIi9Vc2Vycy9rcGJ1cnNvbi8uY29kZXgvd29ya3RyZWVzL2FpdG0tODMtdXNhZ2UtbGF1bmNoLWhlYWx0aC1yZXZpZXcvdHJ1bmsvLmFpdG0vc3Rvcmllcy8wMDAvODMvcGxhbi9yZXZpZXdzL3hwci0yMDI2LTExLTA5LXVzYWdlLWNhcHR1cmUtbGF1bmNoLWhlYWx0aC1yZXBsYW4vbmF0aXZlL3BsYW4vMjAyNi0xMS0wOS11c2FnZS1jYXB0dXJlLWxhdW5jaC1oZWFsdGgtcmVwbGFuLXJldmlldy02NjYyYjM2YmQ0Y2JlMmUzYTdmYmVjYzNmYjdkYzMzMC9yZXZpZXctNjY2MmIzNmJkNGNiZTJlM2E3ZmJlY2MzZmI3ZGMzMzAtcmV2aWV3ZXItcmVzcG9uc2UtMS5tZCIsCiAgInJldmlld19pZCI6ICJyZXZpZXctNjY2MmIzNmJkNGNiZTJlM2E3ZmJlY2MzZmI3ZGMzMzAiLAogICJzY2hlbWEiOiAiYWktcGVlci1yZXZpZXcuaW52aXRhdGlvbi1yb3V0aW5nL3YxIiwKICAid29ya3NwYWNlIjogIi9Vc2Vycy9rcGJ1cnNvbi8uY29kZXgvd29ya3RyZWVzL2FpdG0tODMtdXNhZ2UtbGF1bmNoLWhlYWx0aC1yZXZpZXcvdHJ1bmsvLnNjcmF0Y2gvcGVlci1yZXZpZXcvcmV2aWV3LTY2NjJiMzZiZDRjYmUyZTNhN2ZiZWNjM2ZiN2RjMzMwIgp9Cg" -->

# Reviewer invitation

Review: `review-6662b36bd4cbe2e3a7fbecc3fb7dc330`

Mode: `normal`

- Artifact: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/usage-capture-launch-health-replan.md`
- Workspace: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330`
- Response: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-response-1.md`
- Invitation: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-invitation.md`
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

When the project-local broker is active, yield after each handoff; do not poll or repeat wait calls. Inspect `peer-review broker status --json` for authenticated instance state. After a failure, preserve receipts and run `peer-review broker reconcile /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330 --json` only when the exact recovery evidence calls for it. A broker failure never silently changes the selected reviewer or transport. If the broker is unavailable for an existing manual review, use the bounded `peer-review status /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330 --next` recovery path.

Role: reviewer. Join from a distinct session in the same physical worktree.

Installed join: `peer-review join /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-invitation.md`

Installed-package join: `npx --no-install ai-peer-review join /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-invitation.md`

Rules of engagement:

- Edit only the exact pending reviewer response shown above.
- Do not edit the reviewed artifact, create commits, or push.
- Query `peer-review help join` instead of guessing command syntax.

Recovery: `peer-review resume /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330`
