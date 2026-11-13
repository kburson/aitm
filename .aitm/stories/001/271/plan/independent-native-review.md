[22:38:30]
# PASS

The material overclaim from the first HOLD is fixed. The four wording items are fixed in the memo prose. What remains is minor and doesn't block.

## HOLD items cleared

- **Isolation claim.** The memo now says only what the evidence shows.
  - **`--restricted`:** the pinned help text says this flag makes Claude Code ignore user, project and local settings files. Managed settings and `--settings` still load.
  - **Pipe evidence:** the pipe shows one SessionStart hook that ran and succeeded, no MCP servers, no non-built-in plugins, and only the Task and Read tools.
  - **Scratch settings:** `settings.json` defines exactly one SessionStart hook with the `startup` matcher. That matches the single hook the pipe reported.
  - **Managed policy:** the memo states plainly that the capture doesn't prove managed policy was absent, and the evidence summary records `managed_policy_absence_verified: false`.
  - **Removed:** the "isolated settings", "no hooks" and "scanner recognizer" claims are gone.
- **Config files.** `agent.json`, `mcp.json` (empty) and `prompt.txt` are now provided. They match what the run did: the parent and child replies are correct, there's one Read call, and there are two request groups.
- **Item 1 (directory approval).** The memo now says the launcher created the directory, approved it and enabled it through the inbox itself.
- **Item 2 (control names).** The memo now names the controls by what they refuse ("a truncated child record set", "a recorded error").
- **Item 3 (control coverage).** The memo no longer claims the parent check compares against the armed prefix, and it doesn't claim negative controls for the live launcher guards.
- **Item 4 (before metering).** The memo now says "ten complete child rows before an assistant row".
- **Item 5 (progress log).** The memo doesn't claim admission. "Established the parent epoch at ordinal 34" is supported by the registry view.

## Minor issues (don't block)

1. **Receipt keys.** The receipt JSON still uses the old names `child_prefix_seen_before_metering`, `missing_terminal` and `recovered_or_error_completion`, and the memo doesn't adopt them. Rename them in the next verifier revision.
2. **Unhashed inputs.** The settings, agent, MCP and prompt files have no recorded hashes. The hook and plugin summary has no script showing how it was produced. Both can be checked against the hashed `stream.jsonl` and the observed behaviour, but a future receipt should hash them directly.
3. **Hook events.** "No other hook events" is a statement about what the pipe reported. It doesn't show that no other hooks ran. The memo's wording stays within that limit.

This PASS covers one controlled process and its closure trace, for admission design review only. It grants no authority over ownership, child epochs or restart scope.
