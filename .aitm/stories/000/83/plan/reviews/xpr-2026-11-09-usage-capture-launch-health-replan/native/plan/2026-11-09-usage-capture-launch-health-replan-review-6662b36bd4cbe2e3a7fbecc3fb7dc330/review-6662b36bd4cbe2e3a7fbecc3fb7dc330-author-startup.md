<!-- ai-peer-review-template version="1" digest="sha256:7555c0e7388bb1e33e4ec68e9f0387d9c25cf16764c1fe2139f718efee4456aa" -->

# Author startup

Review: `review-6662b36bd4cbe2e3a7fbecc3fb7dc330`

Mode: `normal`

- Artifact: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/usage-capture-launch-health-replan.md`
- Workspace: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330`
- Response: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-response-1.md`
- Reviewer invitation: `/Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.aitm/stories/000/83/plan/reviews/xpr-2026-11-09-usage-capture-launch-health-replan/native/plan/2026-11-09-usage-capture-launch-health-replan-review-6662b36bd4cbe2e3a7fbecc3fb7dc330/review-6662b36bd4cbe2e3a7fbecc3fb7dc330-reviewer-invitation.md`
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

Phased sessions remain event-authoritative. After a non-final acceptance, finalize the current artifact and follow the single `peer-review advance <workspace> <artifact>` action emitted by `status --next`; never infer or skip a phase from chat.

When the project-local broker is active, yield after each handoff; do not poll or repeat wait calls. Inspect `peer-review broker status --json` for authenticated instance state. After a failure, preserve receipts and run `peer-review broker reconcile /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330 --json` only when the exact recovery evidence calls for it. A broker failure never silently changes the selected reviewer or transport. If the broker is unavailable for an existing manual review, use the bounded `peer-review status /Users/kpburson/.codex/worktrees/aitm-83-usage-launch-health-review/trunk/.scratch/peer-review/review-6662b36bd4cbe2e3a7fbecc3fb7dc330 --next` recovery path.

Installed help: `peer-review status --help`

Installed-package help: `npx --no-install ai-peer-review status --help`
