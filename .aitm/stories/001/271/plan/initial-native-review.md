[22:37:07]
# HOLD

The core mechanics hold up. The HOLD is for one material overclaim: the memo says the run had isolated settings and used no hooks, and the inputs don't support that.

## What holds

- **Subprocess wait:** this is a real wait on the same process. The launcher reads results from the pipe it created, closes stdin, reads stdout to EOF, then waits and asserts exit code 0. The verifier confirms the last line in the stream log is a success result. A timeout fails the run.
- **Early origin witness:** this holds. The child directory is empty before the prompt. The watcher, running under the lease, records file identity, size, row count and hash once rows begin with a user row and contain no assistant row. After exit, the launcher re-checks file identity and the prefix hash. The verifier re-hashes the prefix, re-counts the rows and confirms none is an assistant row. Ten rows matches the first assistant row at ordinal 10.
- **Closure guard:** this holds. After exit the directory contains exactly the transcript and its metadata file. The parent's pre-prompt bytes and capture cursor are unchanged, and the registry still equals its armed snapshot with one epoch. The verifier checks byte lengths and SHA-256 again, both before and after the controls.
- **Request linkage:** this holds.
  - Start and stop share task, run and tool IDs, and the task is foreground.
  - There is exactly one parent Agent call and one tool result. The tool ID matches the metadata and the child file name.
  - The prompt, call and result appear in order.
  - Assistant rows match the forwarded assistant rows by ID, one-to-one.
  - Exactly two request groups exist. The second is the last row (ordinal 19), with stop reason `end_turn`, and its usage equals the reported usage. The earlier group is rows 10–11.
  - The epoch (34) comes before the prompt span start (37).
- **Negative controls:** all seven refuse, and the memo correctly says they change only the verifier's inputs.

## Material overclaim

**"Isolated settings", "no production or child lifecycle hooks", and "a structured scratch startup signal satisfied the existing scanner recognizer"** aren't supported by the exact inputs.
- `settings.json`, `agent.json`, `mcp.json` and `prompt.txt` weren't provided.
- The run uses the real `~/.claude`, which is where the transcripts are written. It passes `--settings` but nothing that limits which settings sources load.
- Only `CLAUDECODE` and `CLAUDE_CODE_ENTRYPOINT` are removed from the environment.

As I understand Claude Code's flags, `--settings` adds settings rather than replacing them, so user-level hooks and plugins could have run. I can't confirm what `--restricted` does in 2.1.318. Nothing in this slice proves the run was isolated, and the "controlled process" qualification depends on it.

## Minor wording problems

1. **"Already approved empty child directory":** the launcher created that directory and approved it itself, under the same lease, moments earlier. Say so, so readers don't take it as proof of an outside approval step.
2. **"Missing terminal usage" control:** `refuses()` accepts any assertion failure without checking which one fired. Truncating `child[:-1]` actually fails at the assistant-ID match, not at a usage check. Name the controls by what they refuse, not by an assumed reason.
3. **The four file-set controls only show that changed hashes fail.** "Modified parent prefix" is caught by the whole-file hash, not by comparing against the armed prefix hash. The live launcher guards (witness, file identity, registry) have no negative controls at all.
4. **`child_prefix_seen_before_metering`:** the stronger claim ("before metering") is only safe as "before any assistant row was written." The first request may already have been sent; if so, its request row would be in the early 10 rows.
5. **Unchecked progress log:** the verifier never reads the log entry that records whether the parent was admitted or the scope check refused. A scope refusal after the epoch was set would still produce a receipt. The memo doesn't claim admission, so this is a gap, not an overclaim.

## To clear the HOLD

Either:
1. provide the settings, agent and MCP files plus proof of which settings sources were loaded and which hooks were active; or
2. remove "isolated settings", "no … hooks" and the startup-signal claim from the memo.

Then fix the wording in items 1–4.
