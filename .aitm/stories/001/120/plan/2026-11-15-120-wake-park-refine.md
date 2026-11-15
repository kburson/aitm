# #120 Private wake ingress and parked-session scheduling

The accepted M10 owns the private wake ingress, fair monotonic scheduler, explicit park and approved native hook senders and installers. Prerequisites are #115 and #119. #121 owns the process that drives the scheduler, host watchers and native reconciliation. Use the pinned provider contracts accepted under Epic #100 and qualify any new native interaction in isolated provider homes.

## Scheduling and recovery

- A same-account private socket accepts a bounded wake hint. Require the native peer UID before parsing, reject duplicate or unexpected fields, and resolve only an approved source locator through the existing registry and adapter. Treat sender timestamps and raw provider session or turn hints as advisory. Persist only authenticated, keyed service references and the minimum allowlisted disposition needed for deduplicated scheduling. A nonexistent, wrong-account, stale or unapproved source creates no work.
- Active, Settling and Parked are scheduling states. A stop or explicit park schedules final catch-up and cannot retire a newer generation. Independent known appends reopen parked work. A pending final scan that fails retains eligibility and progress; no scheduling event mutates a delivery cursor or the active workflow scope. Caller-supplied monotonic time drives bounded backoff. After reboot derive new monotonic schedules from durable facts and reconcile missing wake events.
- Emit bounded work in fair order across eligible streams and project contexts. One result at its M09 destination limit postpones that stream. Other due streams still receive their quota. The coordinator owns acknowledgment of consumed work and root-watch fallback. Specify the handoff so a crash between dequeue and scan cannot erase a pending wake.

## Hook carrier and explicit park

- Use Codex user-local plugin, Claude Code user-local settings and Grok Build user-local hook configuration, each with an isolated provider home and the pinned approved provider tuple. Installers preserve untouched settings and other owners' hooks even on a refused install. Their owned descriptors invoke one stable launcher. Do not embed checkout, transcript, state or socket paths. The launcher resolves approved private settings and returns promptly when the monitor is absent or refuses the wake.
- An ordinary wake sends no scope command. Any Grok prompt-scoped proposal follows M05 and M07 evidence and admission, then native completion verification. Explicit park supplies only the keyed session reference and cannot approve a provider, acquire quota, assign a project or authorize a scope transition. Live Claude capture and cost policy remain governed by the separate coverage work. Hook wake qualification is separate from cost qualification.

## Refine acceptance

Verify final catch-up and late reopen, stale stop preservation of a concurrent turn, duplicate or lost hook recovery, fairness under one full destination, path and peer refusal, and absence of raw paths after receipt retirement. Exercise each approved installer twice in isolated native configuration, preserve foreign entries and tracked repository files, and demonstrate a refused or missing socket cannot stall the provider. At JIT specify exact APIs, state tables, crash points, input budgets, test names and installer ownership and rollback boundaries.

M10's four-hour implementation cap includes all three adapters. Keyed hint structures and the approved locator path should reuse the current registry, private-file and adapter primitives. Review the estimate against the actual pinned installer inputs. If one extra native carrier needs a separate artifact or exceeds the cap, return the narrowest proposed ownership split for independent acceptance with the scheduler first.

## Native installer evidence to confirm at JIT

- Codex's package interface supports bundled lifecycle hooks. Hook trust remains a separate native authorization even after a plugin is installed. Stage only the owned package through the pinned provider's supported installer. Verify exact activation in the isolated target surface under the release rehearsal story. The local CLI help for 0.169.0-alpha.11.1 advertises plugin installation. Treat that as current authoring evidence and pin the target carrier separately. [Codex plugin package](https://developers.openai.com/plugins/build/plugins)
- Claude Code reads the user settings hook entry independently of project settings. Preserve its separately managed and project trust decisions, and use only a nonblocking wake hook type and event that the pinned binary actually loads. [Claude Code settings](https://code.claude.com/docs/en/settings) and [hook reference](https://code.claude.com/docs/en/hooks)
- Grok Build reads personal hook JSON under its user hook directory. Preserve its native project trust store. The wake path may consume only the bounded fields needed to schedule. The prompt-specific marker path still needs the already qualified M05 carrier and M07 admission. [Grok Build hook configuration](https://docs.x.ai/build/features/hooks)
