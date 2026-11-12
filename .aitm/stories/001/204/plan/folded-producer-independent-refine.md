# #204 independent native producer Refine

Claude Opus 5.5 high, isolated local CLI. Literal trunk `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`. Review packet SHA-256 `46daf44887dc92ef48939873ff269d98aa6703a02b09b357bed739aa4acbd3dc`.

[10:27:38]
HOLD

The evidence does not meet the M08b5 positive producer contract. I agree with keeping #204 in Refine and #119 gated. All three subgates fail on their own, not because one failure drags the others down.

## Per-gate assessment

**1. Exact keyed child membership: FAIL**
- `exact_child_keys_referenced_by_aggregate_metadata: 0` and `aggregate_fields_that_name_membership_or_inclusion: []` in both runs.
- The 3 distinct child request and row keys exist only on the observer's side, in the private sidecar. No producer aggregate names them.
- `tool_agent_id_matches_child_sidecar: true` links the tool call to the child's transcript by agent ID. It does not attest which usage rows belong to the child.
- **The narrative leaves out a gap.** In the foreground run, `native_child_links_to_outer_tool` is **0**; it was 1 in the background run. So the synchronous run's child sidecar has no native link back to the outer tool. The only binding is an agent ID string match. The prose ("The tool's agent ID matched one private child sidecar") is accurate but should say this outright.

**2. Terminal closed accounting set: FAIL**
- `native_task_completion_statuses: ["completed"]`, `background: false` and outer `status: completed` show the Agent call's lifecycle ended. A finished lifecycle is not a closed membership record: nothing lists the members, so nothing is closed.
- `totalToolUseCount`, `totalTokens` and the 1:1 count of usage rows are counts. The contract explicitly excludes counts.

**3. Explicit inclusion in the aggregate: FAIL**
- The outer `usage`, terminal `usage`/`modelUsage` and cost-state `totalCostUSD` are totals with no record of what was summed. Concluding that the child is included from matching sums or from Claude Code's documented cost behaviour is exactly the inferred fold the contract excludes.

## What each artifact proves

| Artifact | Proves | Does not prove |
|---|---|---|
| Linked receipt (tool 18 → result 22) | The parent's Agent call got a terminal result in the same durable transcript | Which accounting rows that result covers |
| Child sidecar | One child transcript with one usage row and 3 keys exists, and its agent ID matches | That the producer counted that row, or that no other rows exist (no native back-link in the foreground run) |
| Task completion | A non-background task reached `completed` | A closed set, or anything about inclusion |
| Outer result, terminal and cost-state totals | Totals exist per model and per session | Membership or inclusion; equal numbers are excluded |
| Ordinary adapter | It recognizes the source and has a cursor | Nothing about the fold. Zero observations and zero diagnostics from a transcript that has usage-bearing parent rows is unexplained (see findings) |

## JIT qualification

The selected fields do not support a qualified JIT. The native prerequisite stays held, and `OVERLAP_UNVERIFIED` and the earlier frontier stay as they are. The `report()` path shown (a PARTIAL aggregate plus an `OVERLAP_UNVERIFIED` gap) is the correct behaviour to keep.

## Native fields left unchecked that could qualify

1. **Terminal `subagent_stats`**, which the receipt records only as `type: dict`, without its keys.
   - Record its key shape, sanitized.
   - It qualifies only if it is keyed by agent ID or tool-use ID, lists the child's request or message IDs, and those match the sidecar row keys exactly, with none missing or extra.
   - It also needs a terminal status on each entry and a field stating it is included in `modelUsage`/`totalCostUSD`.
   - Per-agent totals alone fail: they give agent-level keys, not a closed set of rows.
2. **Outer-result `usage.iterations`.**
   - Record whether it is null, empty or a list, and the keys of its entries.
   - It qualifies only if each entry carries a request or message ID equal to a child row key, and the entry set exactly equals the sidecar's rows.
   - The producer must also define `usage` as the sum over `iterations`; that has to come from the producer's own definition, not from checking that the numbers add up.
   - Combined with foreground `completed`, this would cover all three gates, but only for the outer result treated as the covering aggregate. Inclusion in the session terminal would still be unproven.

The `harness*` fields (`harnessSectionHash`, `harnessNoteCount`, `harnessTailCount`) look like prompt and harness bookkeeping, not accounting. Low priority.

## Findings to fix in the Refine record (none overturns the HOLD)

1. State the foreground `native_child_links_to_outer_tool: 0` explicitly, and say that the child binding rests only on the agent ID match.
2. Name the failing proof gate precisely ("membership, closure and inclusion all unattested"), as M08b5 requires, instead of just "native producer gate".
3. Make the receipt reproducible. It should record the foreground setting it used (name, and a digest of its value), a digest of the pinned CLI binary (not just `"2.1.318"`), and digests of the prompt and settings. Both runs show the same Agent arguments, so the foreground behaviour came from configuration, and the receipt does not capture that configuration.
4. Explain why the ordinary adapter published 0 observations with no diagnostics: an intentional scope filter on the synthetic folder, or a silent miss? This isn't part of the fold gate, but an unexplained drop with no diagnostics should not stay unexamined.
5. Define what `distinct_child_request_and_row_keys: 3` counts. It looks like request ID, message ID and row ID for one row, but the receipt doesn't say.

None of this authorizes JIT, Develop, a provider switch, a change to the parent gate, or anything for Epic #2, C01 or production cutover.
