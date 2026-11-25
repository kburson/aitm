# #445 bounded live pilot

The [sanitized receipt](445-live-portable-effort-pilot.json) records four successful headless turns in a private macOS test project on the installed wheel. Codex 0.171.0-alpha.13 ran two exact turns under the same child. Claude Code 2.1.331 and Grok Build 1.0.92 received bounded handoffs under separate children of the same pilot epic. Existing sign-in and provider permissions remained in effect. The configured Claude route executed its normal startup hooks. The capture caller checked the successful same-session hook preamble before passing the initialized stream to the portable adapter.

| Scope | Effective observations | Observed tokens |
| --- | ---: | ---: |
| Codex-only child | 2 | 50,774 |
| Claude handoff | 1 | 24,469 |
| Grok handoff | 1 | 18,710 |
| Cross-provider epic | 4 | 93,953 |

Each adapter receipt matched independent native terminal counters and exact retained recovery. A deliberately staged later Claude revision remained pending through SQLite reopen. Its predecessor settled the original observation. Five replays left both the database and the frozen canonical export byte-identical. The export retained one clock gap for the Grok turn, which carries a native end time. Verified billing remained unknown.

The accepted corpus used four model turns and zero new model turns for capture, settlement, recovery or replay. A first pilot attempt was stopped after the Claude launcher failed before a numeric result. Its two completed Codex turns are accounted for separately in the story's cost table. A successful second pilot used a prompt separator and verified the native hook preamble.

Capture intervals ran 3.704–9.800 seconds with a 65-second process timeout and a 2 MiB stdout bound. The largest post-capture adapter step was 190.103 ms including the exact native lookup. In-memory recovery took up to 1.701 ms. Staging four inputs took 7.252 ms. Reopen and readback, settlement, rendering, and five replay checks each took 3.051 ms or less. For the same bounded workload, the initial regression budget is 250 ms per exact adapter check including lookup, 5 ms per in-memory recovery, and 10 ms for each measured SQLite or render phase. These are local repeat targets from one sample. Capture intervals also contain provider response time.

The test directory used mode 0700 and raw copies used mode 0600. The published evidence contains pseudonymous boundaries, digests, bounded counters and timings. The sanitized report and receipt passed checks against raw session IDs, local paths, prompt canaries, and the project pseudonym key identifier.
