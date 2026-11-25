---
schema: "aitm.story/v0"
id: 457
title: "Capture and publish session-owned agent turn receipts"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/457"
parent: 456
children: []
blocking: [458]
blocked-by: []
created: "2026-11-25T16:06:16Z"
updated: "2026-11-25T18:03:41.017Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-25-session-owned-turn-capture.md"], "plan": [], "attachments": ["attachments/timing/457-kickoff-native-engagement-20261125-457.json", "attachments/timing/457-kickoff-native-usage-20261125.json"]}
expansions: []
trips: []
---

# Capture and publish session-owned agent turn receipts

[GitHub #457](https://github.com/kburson/aitm/issues/457)

Implement the session-owned capture path recommended in #455. Reuse #435 enrollment, adapters, storage, and AIPR companion evidence.

## Acceptance

- The live chat agent binds its own and each supervised worker, subagent, SPR or XPR turn when it starts or dispatches. A small caller-owned helper persists private routing state and writes sanitized immutable receipts scoped to the story on `planning`.
- Qualify automatic live capture and exact delayed recovery on the advertised Codex, Claude Code and Grok Build routes. Exercise change of story, resume or compaction, interruption, handoff, out-of-order completion, replay, and pending or unattached work. Keep the Codex sealed-review gap explicit.
- Demonstrate remote publication under existing branch protection. Use one scoped writer for registration, handle concurrent pushes and ambiguous delivery by readback, and refuse conflicting identities. Test cross-project isolation, privacy, and overlap without duplicate usage.
- Measure processing and publication overhead and record any additional model turns. Keep provider transcripts private and AIPR decisions under their existing authority.

Carry the useful narrow checks from #127, #128 and #129 forward. #137 supplies Linux Grok evidence if that route is advertised. [Spike findings](https://github.com/kburson/aitm/blob/f39eb4d681c86f3c9a747d606e95d969e900b43b/.aitm/stories/004/455/attachments/455-findings.md)

## Kickoff

Drafted the [session capture design](design/2026-11-25-session-owned-turn-capture.md). An independent builder check identified three requirements to make explicit: minimum live route coverage, exact native launch binding, and remote writer fallback. The draft includes each. Design acceptance is pending.

## Actual agent engagement

**3m 37.222s observed (0.0603 agent-hours), partial coverage.** Independent agent intervals are summed, including overlap. The kickoff turn was active at the 2026-11-25T18:03:24.882Z cutoff. The builder check had an exact native end. This snapshot will be superseded as work continues. [Timing receipt](attachments/timing/457-kickoff-native-engagement-20261125-457.json).

## Agent activity and cost

| Agent turn | Observed engagement | Cached input tokens | New input tokens | Output tokens | Codex standard API estimate | Grok reported USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex story kickoff (through cutoff) | 3m 13.891s | 1,982,592 | 40,371 | 8,027 | $0.359271 | — |
| Codex independent builder check | 0m 23.331s | 494,336 | 4,151 | 797 | $0.065706 | — |
| **Kickoff subtotal (observed)** | 3m 37.222s | 2,476,928 | 44,522 | 8,824 | $0.424977 | — |

The estimate uses native GPT-6.2 Sol request frames and Standard API rates. Output includes reasoning where already counted by the provider. **Verified billed story cost is unknown.** This kickoff used two Codex agents. [OpenAI model rates](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [Sanitized request evidence](attachments/timing/457-kickoff-native-usage-20261125.json).
