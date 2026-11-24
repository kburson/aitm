# #433 Usage and timing across epic trails

## Result

The disposable epic trail reconciled **443,354 assigned tokens and 75.776 seconds of engaged agent time** across 21 distinct native observations. The same work occupied **57.186 seconds of working wall time** across agents. The fixture workflow elapsed **142.028 seconds** from its first assignment marker to its last child closure, including idle and coordination gaps. Parent direct work, child work, same-account controls, and the mixed-turn gaps were tracked separately.

The [sanitized receipt](epic-trail-receipt.json) includes per-session, per-child, per-role and epic rollups plus the native measurement and time basis for each observation.

## Live boundary checks

| Scenario | What the trial demonstrated |
| --- | --- |
| Sequential story reuse | Codex, Claude Code and Grok Build each ran seven turns on one verified native session. Explicit start and end markers bound shared epic work and each of two synthetic children. The controller closed the first child before the next started. It excluded unmarked turns before, between and after assignments. Each provider ran a synthetic A-and-B turn without a verified internal boundary. Its observed usage and time could not be split. Those three turns remained outside every story and epic rollup. |
| Resident process and idle | The sequential CLI tests reused native sessions through explicit resume. A separate Claude native stream-input control completed and closed two children in one continuously open process. All four trails included an observed idle interval of at least two seconds. The controller continued without owner input in the sequential trials. These were bounded overnight-style rehearsals. Actual overnight operation, restart recovery across machines, and continuously resident Codex and Grok processes were outside the tested evidence. |
| Parallel headless workers | Separate Claude and Grok headless worker sessions were both active during the Claude orchestrator's tool wait for the same **2.064 seconds**. The tool wait stayed inside the orchestrator's engaged interval and counted once for that agent. An unrelated Claude session on the same account stayed unassigned. After the orchestrator switched to child B, a worker receipt held by the controller and a later Grok AIPR reviewer receipt both remained on child A. Replaying each left the journal digest unchanged. |
| Nested worker | The first Claude worker attempt could not invoke the requested custom agent on that launch surface. Its observed work remained on child A. A separate retry invoked the built-in general-purpose subagent and completed. Its exact root usage of **10,618 tokens** plus **3,127 nested tokens** reconciled to the native inclusive aggregate of **13,745**. The two disjoint observations went into token totals. The nested agent added **0.385 engaged seconds** during its parent's interval and added no extra working wall time. The inclusive monetary indicator remained a single coverage record. |
| Handoff | The Grok predecessor produced a handoff note in its original worker session and then detached. The fresh Codex successor received the note and returned the recorded ordering key before child B closed. The Grok predecessor contributed **37,422 tokens and 4.792 engaged seconds** over two turns. The Codex successor contributed **17,993 tokens and 2.916 engaged seconds**. The modeled **2.002-second owner wait** between agents added no engaged time. |
| Later attribution | A fresh Grok brainstorming session produced a migration edge case while unassigned. An explicit event later linked its original receipt to child A. Child A and the epic each gained **19,265 tokens and 7.820 engaged seconds** once. Child B stayed unchanged. Replaying the link left the journal unchanged, and a conflicting link to child B was refused. The late-attributed interval was already covered by other assigned work, so neither child A nor epic working wall time increased. |

The parallel fixture exercised one genuine Grok reviewer turn through AIPR 0.4.1 with broker-owned manual transport and no-commit test mode. The trial verified the sealed revisions-requested decision, reviewer fingerprint and response digest against the native usage receipt. Closing the experiment fixture did not convey review approval. Codex was a direct worker and orchestrator control. Its headless AIPR reviewer path remains the [#434](https://github.com/kburson/aitm/issues/434) gap.

## Rollup readback

| Scope | Observed tokens | Engaged time | Working wall time |
| --- | ---: | ---: | ---: |
| Epic direct shared work | 41,312 | 6.634 s | 6.634 s |
| Parallel child A | 254,356 | 48.073 s | 37.083 s |
| Parallel child B | 58,690 | 8.259 s | 8.259 s |
| Eight sequential and resident-process control children | 88,996 | 12.810 s | See per-child receipt |
| **Epic inclusive** | **443,354** | **75.776 s** | **57.186 s** |

| Assigned role | Observed tokens | Engaged time |
| --- | ---: | ---: |
| Orchestrators | 143,270 | 29.381 s |
| Workers, including both handoff participants | 76,525 | 11.898 s |
| Nested worker | 3,127 | 0.385 s |
| Reviewer | 201,167 | 26.292 s |
| Later-attributed research | 19,265 | 7.820 s |

A second view summed by native agent or session and matched the assigned token and engaged-time totals. The verifier counted the union of intervals within one session for engaged time, then summed those session totals across agents. It used the union across all included agents for working wall time. Workflow elapsed uses fixture assignment and close markers and includes gaps. The mixed turns retained **41,655 observed tokens and 4.956 seconds** outside the assigned rollup. The receipt also records nine unmarked control turns and one unrelated account control outside it.

## Measurement boundary

MacOS tests used Codex CLI 0.171.0-alpha.13 with ChatGPT sign-in, Claude Code 2.1.331 with Claude Pro sign-in, and Grok Build 1.0.92 with existing Grok sign-in. The launch routes supplied no separate API key. Codex resumed counters were differenced and reconciled to the exact retained turn. Claude joined stream request IDs to exact retained root or subagent records. Grok matched terminal tokens and ticks to an exact session and returned native ordinal. Published turn references bind the session and its native turn together. The measured values and native model price indicators have separate provenance. Neither billed charges nor credit debits were verified.

Engaged time here is an observed adapter interval with the source stated per record. It uses native start or readiness to terminal where observed, stream input dispatch for the resident Claude control, and adapter launch enrollment for the Grok XPR interval. Nested timing uses that agent's retained user and assistant timestamps. Excluded idle and modeled owner wait are independently recorded. These are bounded fixture measurements and do not establish that every harness exposes identical timing events. The adapters were session-owned and exited with their work. The disposable AIPR broker was observed offline after the probe.

For a later decision under #426, carry forward immutable assignment markers, exact native turn identity, an auditable late-attribution link, and the separate session-effort and wall-time measures. Preserve observable work with an unknown or ambiguous scope until a verified link is available.
