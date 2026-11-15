[13:49:00]
REFINE_320: HOLD

**Confirmed**
- **#120 dependency:** #120 is closed and Done, and #320 is listed as its dependent. `HookSender` exists at `sources/hooks.py:136`, so reusing the generic sender is grounded.
- **Graph:** the graph matches the amendment. #320 is blocked only by #120 and blocks #125, #121 gains no installer edge, and #115/#117 are closed and reachable through #119/#118.
- **Scope:** the scope narrowing to the release addition is correct. It covers Codex and Grok candidate installers only, with no live Claude hook, no positive Claude wake, #83 and foreign entries preserved, no production install and no cutover.
- **Rehearsal ownership:** #125 owns the installed rehearsal and #128/#129 own release qualification. Using a constrained disposable home for descriptor parsing and synthetic producer runs fits that split.
- **Grok producer authority:** the producer is bound to the #115 carrier and #117 receipt/owner authority. A wake creates no marker or usage, and durable completion stays separate from the coordinator wake acknowledgment.
- **Estimate:** 2.5 h, Size M is plausible once Claude is removed, and the four-hour cap is viable. #120's 0.0715 actual is partial coverage and provides no calibration signal.

**Actual additional file**
1. **`monitor_control.py`:** monitor subcommand registration lives at `monitor_control.py:775`, in `configure_monitor_commands(monitor_subparsers)`. It is not in `cli.py`, so `monitor hooks install` most likely needs that function edited.
   - Either add `monitor_control.py`, limited to registering the `hooks` subparser, to the edit map.
   - Or prove at this exact commit that `cli.py` can attach `hooks` without touching it.
   - This is small and still inside 2.5 h, but the map is wrong as written.

**Unproved prerequisites**
2. **Stable launcher:** only `HookSender` is evidenced in `sources/hooks.py`. The #120 stable launcher entry and the private launcher settings authority have no cited symbol. Descriptors free of checkout, state and socket paths depend on these, so name the exact launcher entry point, such as a console script or shim, and the settings resolver.
3. **Codex carrier record:** Grok has #115, but no recorded Codex carrier or candidate tuple is cited. This covers the Codex version, pinned lifecycle event, plugin manifest schema and marketplace or enable mechanism. The tuples must come from an already-accepted record, not from #128/#129, which sit downstream of #320 through #125. Name the record.
4. **Grok hook path:** the "approved private Grok user hook directory" is not named. Neither is the record that approves it.
5. **Native trust:** the story does not state that installation writes no trust or approval state. Installation should only stage the plugin and the Grok hook file, and enablement must stay a provider-native user action. Make this explicit so "preserve native review/trust" cannot be read as pre-approving the plugin.

**Story defects to correct**
6. **Installer count:** the summary still says "three native installer descriptors", which contradicts the two-provider body. Change it to two.
7. **Excluded providers:** `--provider claude` and any other excluded provider must be refused with no file written. Excluded-provider wake input must grant no scope and must be rejected without retaining origin data, as the M10 addition requires.
8. **Duplicate events:** the amendment's case of duplicate native producer events reaching the same keyed scheduler path is missing from the test list.
9. **Budget proof:** the amendment's "provider can finish within its accepted budget" proof is downgraded without saying so. State that it is an execution of the installed command line against an absent or refusing monitor, timed against #120's 30 ms sender budget. State that live provider execution is deferred to #125.
10. **Leaf gates:** list the gates explicitly: JIT, locked/signed Test, independent source review, verified delivery and native Close. "Preserve all gates" is not enough.

**Disposition**
Revise the map and text for items 1 and 6–10, and cite evidence for items 2–5. Then re-run Refine. If the Codex record (item 3) does not exist, #320 needs a new prerequisite edge before Develop.
