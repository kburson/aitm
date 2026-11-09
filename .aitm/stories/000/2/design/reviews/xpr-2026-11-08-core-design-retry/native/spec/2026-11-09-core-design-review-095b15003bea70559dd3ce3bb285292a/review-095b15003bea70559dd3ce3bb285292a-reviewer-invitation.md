<!-- ai-peer-review-template version="1" digest="sha256:064952674640611160aff00e947b64de060d4a4cfe7139019eb0f24ee264aa25" -->
<!-- ai-peer-review-invitation data="ewogICJhcnRpZmFjdCI6ICIvVXNlcnMva3BidXJzb24vLmNvZGV4L3dvcmt0cmVlcy9haXRtLWNvcmUteHByLXJldHJ5L3BsYW5uaW5nLy5haXRtL3N0b3JpZXMvMDAwLzIvZGVzaWduL2NvcmUtZGVzaWduLm1kIiwKICAicmVzcG9uc2UiOiAiL1VzZXJzL2twYnVyc29uLy5jb2RleC93b3JrdHJlZXMvYWl0bS1jb3JlLXhwci1yZXRyeS9wbGFubmluZy8uYWl0bS9zdG9yaWVzLzAwMC8yL2Rlc2lnbi9yZXZpZXdzL3hwci0yMDI2LTExLTA4LWNvcmUtZGVzaWduLXJldHJ5L25hdGl2ZS9zcGVjLzIwMjYtMTEtMDktY29yZS1kZXNpZ24tcmV2aWV3LTA5NWIxNTAwM2JlYTcwNTU5ZGQzY2UzYmIyODUyOTJhL3Jldmlldy0wOTViMTUwMDNiZWE3MDU1OWRkM2NlM2JiMjg1MjkyYS1yZXZpZXdlci1yZXNwb25zZS0xLm1kIiwKICAicmV2aWV3X2lkIjogInJldmlldy0wOTViMTUwMDNiZWE3MDU1OWRkM2NlM2JiMjg1MjkyYSIsCiAgInNjaGVtYSI6ICJhaS1wZWVyLXJldmlldy5pbnZpdGF0aW9uLXJvdXRpbmcvdjEiLAogICJ3b3Jrc3BhY2UiOiAiL1VzZXJzL2twYnVyc29uLy5jb2RleC93b3JrdHJlZXMvYWl0bS1jb3JlLXhwci1yZXRyeS9wbGFubmluZy8uc2NyYXRjaC9wZWVyLXJldmlldy9yZXZpZXctMDk1YjE1MDAzYmVhNzA1NTlkZDNjZTNiYjI4NTI5MmEiCn0K" -->

# Reviewer invitation

Review: `review-095b15003bea70559dd3ce3bb285292a`

Mode: `normal`

- Artifact: `/Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.aitm/stories/000/2/design/core-design.md`
- Workspace: `/Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.scratch/peer-review/review-095b15003bea70559dd3ce3bb285292a`
- Response: `/Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-1.md`
- Invitation: `/Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-invitation.md`
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

When the project-local broker is active, yield after each handoff; do not poll or repeat wait calls. Inspect `peer-review broker status --json` for authenticated instance state. After a failure, preserve receipts and run `peer-review broker reconcile /Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.scratch/peer-review/review-095b15003bea70559dd3ce3bb285292a --json` only when the exact recovery evidence calls for it. A broker failure never silently changes the selected reviewer or transport. If the broker is unavailable for an existing manual review, use the bounded `peer-review status /Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.scratch/peer-review/review-095b15003bea70559dd3ce3bb285292a --next` recovery path.

Role: reviewer. Join from a distinct session in the same physical worktree.

Installed join: `peer-review join /Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-invitation.md`

Installed-package join: `npx --no-install ai-peer-review join /Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.aitm/stories/000/2/design/reviews/xpr-2026-11-08-core-design-retry/native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-invitation.md`

Rules of engagement:

- Edit only the exact pending reviewer response shown above.
- Do not edit the reviewed artifact, create commits, or push.
- Query `peer-review help join` instead of guessing command syntax.

Recovery: `peer-review resume /Users/kpburson/.codex/worktrees/aitm-core-xpr-retry/planning/.scratch/peer-review/review-095b15003bea70559dd3ce3bb285292a`
