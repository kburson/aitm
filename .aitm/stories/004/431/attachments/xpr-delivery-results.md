# #431 Late usage receipts for headless XPR turns

## Disposition

Claude Code and Grok Build each completed a real two-round AIPR review with independently delivered usage receipts. Their sealed decisions were readable before native usage settled. The author revised each fixture after the first decision while its usage was still pending. The wrapper then delivered each provider's round-two receipt before its round-one receipt, without another reviewer invocation. Replaying the four settled and two partial receipts left the journal byte-for-byte unchanged.

The interrupted cases joined separate AIPR reviews, received a native interrupt and produced partial usage evidence with no sealed decision. The tested Codex macOS AIPR reviewer route remains unqualified because of the review lock found in [#430](https://github.com/kburson/aitm/issues/430). This spike used Codex as the interactive author and orchestrator. [#434](https://github.com/kburson/aitm/issues/434) covers the reviewer lock.

## How the receipts were delivered

On November 24, 2026, the fixtures used AIPR 0.4.1 in broker-owned manual transport and no-commit test mode. Claude Code 2.1.331 used the AIPR launcher and its explicit resume. Grok Build 1.0.92 used the generated invitation, native streaming JSON and explicit native resume. The Grok compatibility hook import was disabled for these disposable processes, as qualified in #430. Both used existing signed-in account routes. AIPR labeled Claude’s reviewer identity runtime and Grok’s declared. The adapter independently checked each native session against its AIPR reviewer fingerprint. The signed-in Codex Desktop CLI build was 0.171.0-alpha.13.

1. The caller enrolled the story, run, reviewer phase, attempt, review, round and provider before launching. Enrollment requested native usage capture outside the model loop. The Grok handoff also stated that its caller would capture usage.
2. A bounded process adapter observed the successful submit tool result, verified the AIPR decision event and response digest, and recorded the decision as readable with usage pending. The first-round author handoff used that decision before receipts were delivered.
3. The adapter captured native completion and verified it by exact retained readback. Claude's request IDs matched one prompt root and the retained counters reconciled with its per-result usage. Grok's terminal request and session, signature-keyed usage frames, and exact retained turn matched the usage tuple. The two rounds on each route retained one verified reviewer session and distinct native turns.
4. A separate one-shot consumer delivered the normalized packets to a disposable journal after the native processes exited. The completed review decisions preceded the terminal records in all four native streams. Deliberate staging held the receipts about 152–178 seconds after their decisions became readable. That interval includes the test hold and is not a provider settlement-latency measurement. A second readback reproduced the same native evidence and no reviewer was called again for settlement or replay.

The [sanitized machine receipt](xpr-delivery-receipt.json) records the bindings, decision and terminal ordering, observed/delivered times, exact counters and coverage. The experiment carried a companion receipt alongside the existing XPR result. It added no production AIPR fields, hooks, or persistent service.

## Story usage by role

| Role and provider | Scope | Observed tokens | Monetary evidence |
| --- | --- | ---: | --- |
| Reviewer, Claude | Two completed XPR rounds | 477,168 | $0.2240784 native list-price equivalent |
| Reviewer, Grok | Two completed XPR rounds | 416,774 | 2,046,419,200 native USD ticks |
| Reviewer, Claude | Separate interrupted attempt | 103,367 partial | $0.1142720 native list-price equivalent for observed usage |
| Reviewer, Grok | Separate interrupted attempt | 114,066 partial | Settled total and cost ticks unavailable |
| Orchestrator, Codex | Active interactive #431 turn at the receipt checkpoint | 5,384,476 partial | No verified billed charge or API-equivalent estimate |

Completed reviewer subtotal across the two routes was **893,942 observed tokens**. Separate interrupted reviewer subtotal was **217,433 observed tokens with incomplete coverage**. These are token counts from the observed categories. USD equivalents and Grok native ticks retain their distinct provenance and are not combined into a billed-dollar total.

The orchestrator line was captured from an exact native rollout `token_usage_record.turn_token_usage` in the active Codex turn that accepted #431. It includes coordination and related spike bookkeeping up to the native checkpoint, which preceded receipt delivery and replay. It excludes earlier native turns in the long-lived chat and does not estimate usage after the checkpoint. A read after turn completion would be needed for a final orchestrator receipt. There was no Codex reviewer charge or reviewer receipt to infer.

## Failure and replay controls

- Claude's interrupted case matched its terminal per-result usage to exact retained request records. Grok's interrupted case retained the uniquely identified usage frames but provided no numeric terminal total or retained completed usage row. Both attempts preserved a pending AIPR review state with no sealed decision. Their usage was delivered separately from the completed reviews.
- Exact replay of every settled and partial receipt after reopening the journal was a no-op. The receipt includes before-and-after journal digests and refusal codes for changed decisions and wrong-review routing. A separate assignment control refused the old native turn when presented as a new attempt. The control did not relaunch either interrupted reviewer.
- Each single-provider projection passed using the same envelope and journal rules. That check is a data-path control, not a separately executed same-provider peer review. A fixture also rejected counting a child under an inclusive aggregate and again as direct usage. Live nested-provider coverage and concurrent journal writers were outside this spike.
- Provider billing, subscription credit debits and remote-host behavior were outside the observed coverage. All four disposable brokers reported offline after the probes.

## Handoff to #433

Keep the durable review output and usage receipt addressed to the same immutable assignment. Result status and usage status move independently. Allow an out-of-order receipt to complete its original attempt, reject conflicting replays, and track coverage when incomplete. Extend the same binding across different children, resumed orchestrators, parallel workers and detached work in #433. Codex headless reviewer qualification stays a distinct concern for #434.
