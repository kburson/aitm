[14:56:01]
PASS

This PASS covers only the native evidence and producer predicate offered to Refine. It doesn't cover scope custody, ownership, journal integration or release of #119.

**Producer gate: met by a pinned code path, not by arithmetic**
- The selector is literal native code: `e.findLast(Ae => Ae.type==="assistant" && Ae.isUnmetered!==true)`. It picks one operand. The result's `usage` is built from that one entry's `message.usage` through `sX`. Nothing in the result builder sums `usage` across child entries. The `be` message-ID set and `totalTokens`/`totalToolUseCount` are separate fields and don't feed `usage`.
- The capture tells the members apart:
  - Both child rows are genuine provider requests. Each has its own server `requestId`, a `requestRef` joined to the native API request, and matching `message.id` and row UUID.
  - The selected row (ordinal 17, `end_turn`) matches the parent's usage exactly. The excluded row (ordinal 10, `tool_use`) does not.
  - So the result equals one member, not the sum. Equality is used only to check consistency with the code, not to infer membership.
- None of the excluded inference sources is relied on: no emitted relation, sums, call counts or session totals.
- The receipt is versioned (`aitm.claude-foreground-coverage-research/v1`) and sanitized: synthetic prompt, one trusted Read, no production journal writes. The binary, agent definition, captures and source ranges are pinned by SHA-256.

**Exact child membership: met (a set of one)**
- The covered set is {last metered assistant entry in the completed foreground child history}, keyed by the outer tool-use ID plus the selected row's message ID, row UUID and request IDs.
- The earlier child is outside the covered set, both by the code and by the observation, so it must stay independently accounted. This fits M08b5's "exact keyed child set" without changing the parent plan.

**Closure: met for the selected operand**
- `de.push(O)` runs before the `if(!y)return` forwarding check. So the history doesn't depend on whether forwarding is on, and the probe's forwarding mode doesn't change what gets selected.
- `wgn(Zt,…)` runs after the foreground loop ends, on `Zt=de` in the clean path. The selection is taken from a closed local array.
- The capture fits this order: task start 25 and task end 35 carry the same task, run and tool IDs, then the outer result arrives at 36, matching durable row 23.

**Producer inclusion: met**
- The chain is `wgn` → `g6r(w=e)`. The handoff changes only `content`, `harnessNoteCount` and `harnessSectionHash`, so `usage` passes through unchanged into the `status:"completed"` result.

**Corrections the checked rule must carry (fail-closed; they tighten the rule, they don't block the gate)**
1. **The value isn't exactly the message's usage.** It is `{...ih, ...sX(u)}`: native defaults overlaid by the message usage, with a `null` `output_tokens` turned into `0`. If there is no selected entry, the result is just the `ih` defaults, a fabricated-looking zero usage. The rule should state this exact form, pin `ih`, and refuse when no entry is selected or the key sets differ. The current wording "passes exactly its message usage" is slightly wrong.
2. **Error recovery is indistinguishable in the result.** When `it` is set, `h6r` rebuilds the history and the result still says `status:"completed"`. The receipt should record the observed proof that this was the clean path: no system `api_error` events or `agent_api_retry` progress, no cutoff note, and the selected entry is the final history entry. Without that, refuse.
3. **Injected entries aren't in the refusal list.** `Yt.hasNews()` → `Dhe(de,h)` can put items into the history that didn't come from the provider stream. Add a refusal: if any non-provider history entry can't be ruled out, refuse. The `_e.moved` early return is already covered by the background refusal.
4. **Where `isUnmetered` gets set is untraced.** For this capture, the native request joins show both rows were metered. In general, the rule must refuse unless the flag's state can be determined from the pinned artifacts.
5. **Split rows sharing one `message.id`** (several content blocks from one response) must be keyed by request or message ID, or refused as duplicate ambiguity. The proposal already lists that refusal.
6. **The last step isn't visible in the excerpts.** The `foreground_close` excerpt is cut off at `prompt:X,..`, so neither the `usage` assignment in the returned `data` nor the step that turns `data` into the durable `toolUseResult` can be read here. The pinned range has to cover the assignment, or the rule must add the tool-result persistence range. Until then, this one step rests on the observed full equality (stream result to durable row 23).

**Remaining JIT work, not a missing producer gate**
- A supported pre-M09 path to acquire and bind the native artifacts to the live writer.
- The original eligible owner and source span.
- The scan fence under current scope rules.
- Atomically reserving the covering claim plus the exact withdrawal intent for the singleton child.
- Preserving older v5 data and all ordinary readers.
- Controls for missing, foreign, extra and ineligible children.
- `scope_authority_checked:false` is correct and must not be read as custody.

**What would have made this HOLD**
- A selector that summed or iterated over children.
- A history built after forwarding filters.
- A selected operand that matched the excluded row or both rows.
- A result only reachable through the error-recovery path.

None of these applies.
