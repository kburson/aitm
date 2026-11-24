---
schema: "aitm.story/v0"
id: 434
title: "[Spike] Qualify the Codex headless AIPR review-lock path"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/434"
parent: 426
children: []
blocking: []
blocked-by: [431]
created: "2026-11-24T20:29:15Z"
updated: "2026-11-24T20:29:15Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Qualify the Codex headless AIPR review-lock path

[GitHub issue #434](https://github.com/kburson/aitm/issues/434)

Research parent: #426. Follow-up to the reproducible Codex refusal in #430 and the coverage gap in #431.

## Question

Can a real Codex headless AIPR reviewer join and submit under a supported macOS permission configuration while preserving AIPR's lock ownership and process-incarnation checks? If the macOS path remains unsupported, which exact boundary must change and which native route, if any, works with equivalent authority?

## Experiment

- Reproduce the refusal with the installed AIPR and Codex versions on a disposable two-round XPR. Trace the denied boot/process identity query used by the review lock. Compare against a bounded host-side positive control. Retain the actual sandbox policy, provider authentication mode and runtime versions.
- Test documented, least-privilege routes that preserve the native Codex reviewer session and the AIPR trust boundary. Compare a scoped host/broker operation or another supported native host when available. Keep permission and platform changes visible. Do not synthesize boot identity, borrow a participant's identity, disable the sandbox, or change production AIPR in the spike.
- If a path passes admission, exercise two sealed decisions in one native reviewer session, an interrupted attempt, and replay. Correlate every result to its exact native turn and usage. Check whether new and stale lock owners are distinguished and that an ambiguous launch or lock outcome stays visible.
- If no path passes, document the precise blocker, any verified supported control, the smallest candidate change, and the missing proof. Keep the lightweight native Codex comparator separate from AIPR review authority.

Deliver a sanitized provider/host matrix and evidence-backed recommendation for #426. This spike does not change #100.
