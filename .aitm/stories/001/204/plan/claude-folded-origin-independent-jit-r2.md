[20:06:32]
HOLD

**Decision.** The capture is real progress. It corrects R1: the scanner does see the checkout, and the failure is in the scope join. It still doesn't close any of the four prior HOLD findings. The carrier's own assertions show that the existing gates cannot issue a child claim or a parent cover route. The packet's own test says that if the plan still needs new authority code to reach a positive, implementation stays held, and that test applies here. Develop is not authorized. Four active hours is not credible either, even setting the authority problem aside.

**Against the prior HOLD**
1. **Shared stream namespace: confirmed, not resolved.**
   - The carrier asserts `epoch.stream_ref == parent_loc.stream_ref == child_loc.stream_ref`.
   - Every authority key is (project, source, `stream_ref`, ordinal). That covers `span_disposition`, `_evidence` / `ClaimEvidence`, `enroll_stream` and `_latest_epoch`. The distinct `locator_ref` and `incarnation_ref` never reach those keys.
   - So a "distinct child epoch / own ordinal namespace" is a new registry and claim shape.
   - On existing code, `enroll_stream` on the child's ref fails with "Native stream is already enrolled". `_evidence` for child ordinal 19 finds no epoch at or below 19 and refuses.
   - The child's ordinals happen to fall below 34. In general, child ordinals of 34 or more would be attributed to the parent's generation-1 epoch.
2. **Cover route: worse than the packet states.**
   - With the uniqueness refusal preserved, the parent's own observations after dispatch cannot be routed. Once the sidecar exists, `_approved_candidate` always sees two matches.
   - The aggregate at row 46 also sits outside `locator.stream_ref`, so `_observation_proofs` drops it.
   - "Preserve the uniqueness refusal" and "issue the parent cover for [44,47)" cannot both hold on existing discovery. The "dedicated private discovery verifier" would be new authority code placed exactly where that gate fires.
3. **Arm before origin: still unmet.** The only witness that the child was absent before dispatch (`children == {}`) is the scratch hook. Neither the writer nor any existing primitive observed the child before its first frame. Step 2's line "a reservation cannot itself admit that origin" concedes this gap.
4. **Prior probes (a) and (b) were not run.** They required the existing scope recognizer and `_observation_proofs`. The carrier read raw `scan` frames instead.

**Flawed assumptions in the carrier proof**
- **Claims taken from the harness, not proven by the writer.**
  - `parent_ordinary_scope_route_verified_before_dispatch` is hardcoded `True`. It rests on a `'routed'` string in the harness's own `live-progress.jsonl`. No ScopeView or `resolve_route` is replayed.
  - "Admitted before dispatch" as a timing claim rests on that same log and on the hook byte counts. Only the ordinal ordering (34 < 44) comes from the writer.
- **Hook and wire output used as evidence.** These all come from scratch hooks or the harness's stream-json stdout (`stream.jsonl`):
  - child absence before dispatch;
  - the inode and sha prefix witnesses;
  - SubagentStart/SubagentStop timing;
  - foreground status (`is_backgrounded`);
  - the task, run and forwarded-row joins.

  A production monitor reading `~/.claude/projects` has neither source. What remains natively (parent tool and result rows, `agentId`, `meta.json`, the child's `promptId` and `sessionId`, `parentUuid=None`) is copyable file content. It does not prove foreground/synchronous execution or an origin after the enrollment boundary.
- **Scan eligibility is not registry eligibility.** `frame.eligibility is ELIGIBLE` comes from `scan(..., cutoff=2020-01-01)`, not from epochs or permissions. The expected `anchor` comes from the harness path `root/'project'`, not from the registered project in `view`.
- **Partial checks reported as full-span results.**
  - Child checkout is checked only on frames {0, 10, 11, 19}, not on every frame of [0,20).
  - Parent checkout is checked only on frames 44 and 46.
  - Parent permission is queried only on [44,47). The plan requires the full native span [37,47).
- **The prefix check may be tautological.** `_capture_position(..., fixed=epoch_cursor)` returning `epoch_cursor` has no negative control, such as a mutated or truncated prefix, to show it can fail.
- **Closure is not proven.**
  - The receipt rests on one final read, with no control for a post-stop append or continuation.
  - The script accepts either 19 or 20 rows at SubagentStop, so that race is left open.
  - No writer-visible closure signal that works without hooks is identified.
- **None of the step-4 refusal controls were run.** This is a single run on a single client version.
- **Undefined witness.** Step 1's "same-process native witness" is not defined. If it means a witness inside the Claude process, it is a hook.
- **Circular "existing" claim route.** Step 3's "existing immutable claim route" depends on step 2's new child epoch, so it is not existing authority. The atomicity claims (`_build_settlement_change`, v4/v5 payloads) cannot be assessed from this packet.

**What the evidence-only spike must prove**
The spike is read-only: no registry or journal writes, no gate changes. Hook and wire output may serve only as a comparison oracle. It cannot release #204 or #119.

1. **Namespace.** Can any existing writer-validated source ref (for example, the nested or aggregate isolation refs via `validate_source_ref`) carry a child or aggregate epoch and claim through unmodified `enroll_stream`, `span_disposition` and `_evidence`, without colliding with the parent's ordinals? This carrier predicts no.
2. **Parent routing after dispatch.** Can any unmodified path route parent rows written after the sidecar appeared (rows 44–46) while the `_approved_candidate` uniqueness refusal stays in place?
3. **Writer-owned origin.** Can the monitor writer, under its lease and without hooks, do both of the following?
   - Observe the authenticated parent prefix while the child file does not yet exist.
   - Then observe the child's first complete frame at ordinal 0 before any metered row, keeping the same inode and incarnation through [0,20).

   Run this repeatedly and report how often the writer misses the window.
4. **Native-only lineage.** Does the hookless, wire-free join uniquely identify the child and classify it as foreground/synchronous without `is_backgrounded`? It must agree with the hook and wire oracle on every run.
5. **Scope through real code.** Run probes (a) and (b) through `_observation_proofs` / `resolve_route`. Check the registered anchor on every frame of [0,20) and [37,47), and check permission over [37,47).
6. **Refusal controls.**
   - copied or renamed sidecar (new inode)
   - foreign checkout
   - project switch
   - scope handoff
   - disable or re-enable inside the child span
   - post-stop append or continuation
   - missing or duplicate result
   - mutated parent prefix (proves the `fixed=` check can fail)
   - earlier split request rows retained
7. **Closure.** Find a writer-visible terminal signal, without hooks, that orders the durability of row 19 against the parent result row.

**Outcome rule.** If check 1 or 2 is negative, the positive needs new authority:
- a child stream namespace;
- a writer-observed origin;
- a route for the parent after dispatch.

That authority must be a separate issue that blocks #119 directly and gets M08b-style schema and admission review. Otherwise a changed parent plan needs independent re-acceptance.

**Disposition until then**
- Keep `OVERLAP_UNVERIFIED` and the earlier frontier; make no journal changes.
- Keep #204 open, with the failing gate "shared stream_ref namespace: no writer-issued child epoch or claim, and no parent cover route after dispatch; child origin witnessed only by a scratch hook".
- Keep #119 blocked.
