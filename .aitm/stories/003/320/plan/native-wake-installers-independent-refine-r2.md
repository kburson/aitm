[14:03:11]
REFINE_320: HOLD

The blocking issue is that the Codex hook mechanism was proven on the excluded surface. The rest of the revision closes the prior holds.

**Prior holds: resolved**
- **1. `monitor_control.py`:** resolved. The `cli.py` excerpt shows `monitor = groups.add_parser("monitor").add_subparsers(required=True)`, then `configure_monitor_commands(monitor)`, then `monitor.add_parser("report")`. A sibling `monitor.add_parser("hooks")` fits there without touching `monitor_control.py`. JIT must confirm `configure_monitor_commands` does not already register `hooks`, because Python 3.13 argparse raises on a duplicate subparser name.
- **2. Launcher and settings:** resolved. The launcher is `sources.hooks.main()`, which reads stdin and passes the frame to `HookSender().notify`. The console entry is `aitm-usage = aitm_usage.cli:main`. `HookSender.__init__` calling `default_monitor_root()` is shown. The rest of the root chain is shown only as symbols existing at `84b936d1`, not as call edges. That is low risk, and JIT should confirm it.
- **4. Grok path:** resolved at the literal version. The probe binary SHA-256 `197c66a6…5b2a` equals #115's executable hash. `~/.grok/hooks/*.json` is reported as source `user` with event `user_prompt_submit`. Note that #115 itself proved a project hook, so the personal placement rests on the probe, which the plan states honestly.
- **5. Native trust:** resolved for both providers. The plan has no config, trust or approval writes and no auto-enable. Grok workspace trust stays a native decision.
- **6–10:** resolved.
  - The installer count is now two.
  - Claude and other providers are refused with zero writes or scope.
  - Duplicate events go through the same scheduler key path.
  - The budget proof is restated as a 30 ms socket phase against an absent or refusing monitor, with live provider execution deferred to #125.
  - All six leaf gates are listed.

**Prior hold 3 (Codex carrier record): not resolved, now a contradiction**
- **Surface mismatch:** the probe used the official npm Darwin executable, which is the Codex CLI distribution. #114 line 30 states that Mac Codex CLI is excluded even in a shared root. It also states that "same client version alone does not carry the Desktop proof over to the CLI." That reasoning applies in both directions. The matching version string `0.167.0-alpha.3.2` therefore does not carry the plugin, marketplace or Stop-hook mechanism to Codex Desktop.
- **Version vs mechanism:** #114 pins the Desktop version and usage format, not the hook mechanism. The mechanism is the very thing #320 builds on.
- **Fix options:**
  1. Re-run the no-model probe against the executable bundled with Codex Desktop 0.167.0-alpha.3.2, recording the bundle and executable hash.
  2. Show the bundled executable is byte-identical to the npm integrity `sha512-Tdql…sah0A==` artifact, and get #114's owner to accept that carry-over explicitly.

**New implementation dependencies to settle before JIT**
1. **Codex marketplace path:** the per-user marketplace or catalog location is not named. "Preserve foreign catalog entries" implies writing into a shared, provider-read file. The plan's own rule is that any external path returns to Refine. Name the exact file and state whether registering the marketplace requires a config edit or a native command. A config edit is forbidden, so a native command would be the user's action.
2. **Shared-root CLI firing:** Desktop and CLI share the root, so a staged Codex plugin is also discoverable by the excluded CLI. State how a CLI-originated Stop wake is handled: refused, or harmless because a wake grants no scope. Add a test for it.
3. **Package source and file count:** say where the plugin manifest and package contents come from. If they are generated in `sources/hooks.py`, the three-file map holds. If they are packaged data files, the map is wrong.
4. **#194 custody:** confirm #194 is closed at the base. If it is open, it is a missing edge.
5. **Base commit:** the source evidence is at `84b936d1`, which is neither this branch head (`4df14d9e`) nor shown to be trunk. Pin the Develop base, or have JIT re-cite at that base.
6. **Console resolution:** "Executable resolution under each isolated provider invocation" is the plan's JIT gate, not a hold. The choice is bare `aitm-usage` on PATH versus an absolute installed-console path. Either is acceptable only if it needs no checkout path and no extra grant. Otherwise it returns to Refine, as the plan says.
7. **Entry-to-exit timing:** the plan measures it but sets no threshold. State that it is recorded only and that the provider-timeout gate belongs to #125.

**Gate ownership**
- **Rehearsal gates (#125):** trusted live provider execution, the provider hook timeout budget, and real user install, enable and trust flows.
- **Release gates (#128/#129):** qualification only. Nothing in #320 may rely on them.
- **Pre-Develop (this Refine):** Codex hold 3 and items 1–5.

**Disposition**
- **Authorization:** JIT is not authorized.
- **Grok half:** it is Refine-clean as written.
- **Codex half:** it needs either Desktop-surface mechanism proof or an accepted hash-identity carry-over.
- **Next step:** after the Codex record exists and items 1–5 are written into the plan, re-run Refine.
- **Missing Codex record:** if no such record can be produced, add a prerequisite edge before Develop.
