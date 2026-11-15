[20:23:38]
# REFINE_300: HOLD

**Basis:** I reviewed only the evidence you supplied: the Refine text, the R2 amendment excerpt, the NA-1 graph JSON, the baseline test output and the four code excerpts. I did not recompute the artifact SHA. The M09, M12–M15 and NA-1 milestone prose was not supplied, so I could check downstream responsibilities only against the R2 summary sentences. This is not a JIT approval and does not authorize any code.

## What holds up

- **Graph and board.** The JSON agrees with R2:
  - #300's only incoming edge is #210, and its outgoing edges are {119, 129}.
  - #119's final prerequisites are {118, 199, 201, 202, 203, 209, 210, 300}.
  - #129's final prerequisites are {128, 134, 137, 300}.
  - #100 keeps incoming {101, 102} and outgoing {2}.
  - #297's children are unchanged at {204, 270, 296}.
  - #135, #295 and #298 now sit under the sibling epic.
  - The open first-release set is {119–129, 134, 137, 300}.
  - On the Project item, Estimate, Size and Start are all null.
  - The supplied JSON does not show: the edges #295←{210, 298}, #298→{295}, #204→{296} and #119→{120, 122, 296}; #135 having no outgoing edges; or #301 having no parent and no edges. I'm accepting those on your statement that activation was verified.
- **The proposed seams are the right ones:**
  - `Registry._approved_candidate` is the correct place for the gate on retained roots. It runs after the pinned-root identity check and the host, surface and provider check, and before any usage read.
  - In `_reserve`, the final check that `final_view` and `final_registry` are unchanged runs inside the write transaction. That makes it a correct atomic place to recheck the decision.
  - The `_enable_paired` lazy upgrade is a working template for the migration.
- **Downstream roles match R2.** M09 builds the journal-only candidate with no ACK, M11 handles scheduling, M12 fences visibility, and M13/M14 surface the result. Nothing is moved into #300.
- **Baseline.** "3 passed" shows current behavior only. The Refine says so correctly.

## Blocking findings

1. **The runtime profile default and activation authority are not decided.** Today `Registry(root)` and the journal constructors take no profile.
   - If the default becomes closed, every existing Claude-heavy test from #199–#210 needs a profile passed in. That rewrite is not in the estimate.
   - If the default stays legacy or open, the system fails open by default. The first-release "closed" entry points do not exist yet, because #121 and #125 are still open.
   - The Refine also says neither what authenticates the "isolated candidate proof" (constructor kwarg? object bound to the root identity? persisted profile identity?) nor what stops a caller from building the same proof outside tests.
   - Leaving all this to JIT leaves both the property under review and the largest sizing variable unsettled.
2. **No seam reads the build or executable identity.**
   - `_approved_candidate` checks only the platform, machine, `native._native_surface` and `native.provider`.
   - `client_version` and `format_version` are taken as declared at `_approve`, which does no native discovery.
   - Executable identity is not in the transcripts. Verifying it would need host binary inspection, which is the Refine's own trigger to stop for a "product loader subsystem."
   - So "unreviewed build" and "falsely declared adapter tuple" cannot be tested as real native checks. The Refine must either name an existing source for each tuple field, or limit this leaf to authenticated proof inputs and assign real binary verification to #128/#129.
3. **Approval-time behavior conflicts with the coverage key.**
   - The coverage record is keyed by "approved installation/epoch", but the Refine also gates new approvals. If a new Claude `approve_source` is refused, it has no key and no coverage record. If it is registered but excluded at capture, the Refine must say so.
   - It also doesn't say whether re-approving an existing Claude source idempotently (the `existing == approved` return) counts as "new" or "retained".
   - Any decision field persisted in `ApprovedSource` changes `existing != approved` equality and the registry encoding. That would need a registry migration nobody has scoped. Deriving the decision at runtime avoids this.
4. **The source and recheck point for policy changes are not defined.**
   - "Private config narrows captured policy" implies a new persisted artifact. That means a new pinned file with its own format and custody, which is not scoped.
   - Batches are tied to their journal instance (`self._batches[id(prepared)]`). So the "stale prepare" test only means something if policy can change within one instance, and `_reserve` would have to re-read that source inside the transaction.
   - The `current == read.progress` retry branch in `_reserve` must also refuse a source that is now excluded. No test names it.
5. **The sequence and schema migration details are missing:**
   - `_tip(connection)` must cover the new coverage table. Otherwise a coverage event and the next claim (`sequence = _tip + 1`) can get the same sequence number.
   - Existing `JournalChange` readers that assume only disposition or settlement exist must either filter out the new variant or handle it.
   - v6 must be a strict superset of v5. `_enable_paired` upgrades only when the version is 4, so an upgrade from v4 to v6 that skips `_PAIRED_SCHEMA` permanently disables paired settlement.
   - Strict identity validation must accept v6 and still reject v7 and later.
   - `prepare` currently uses only a read transaction. The Refine must name where the refusal-time write happens and confirm it commits before the refusal is raised.
   - The Refine must say whether `coverage_changes` on a v4 or v5 store returns empty without upgrading it.
6. **The estimate leaves no margin.** At 4.0h it equals the cap.
   - The 1.2h test budget covers about 15 named sub-cases across three contract tests, plus negatives for v4→v6, v5→v6, older upgrades, strict schema and copied/stale/forged sources.
   - Existing test churn from finding 1 is not included, and neither is host parametrization. `_approved_candidate` checks the real `platform.system()`, so the qualified Codex surface differs between a macOS dev host (Desktop) and hosted Linux (CLI), and the excluded macOS Codex CLI case needs host simulation.
   - With findings 1–5 open, a single combined story under the four agent-hour cap isn't credible.

## Non-blocking items for JIT

- Freeze a canonical byte encoding for `JournalCoverage`, so M09 can validate "exact journal change bytes."
- If extent is always unknown in this leaf, either drop the half-open range from the v6 layout or test it. Don't ship an untested range.
- Define who may read `coverage_changes(after_sequence)`, and its sanitization guarantees, given that it has no source or project filter.
- Confirm that the name `coverage` doesn't collide with the existing coverage projection from #209.
- Show that `ProviderAdapter().discover` does not parse Claude payload. If it does, gate on the approved provider before discovery as well.
- Writing v6 makes the store unreadable to pre-#300 binaries. That rollback effect needs a note for #126.
- The "reviewer's mode-level applicability condition" cited for NA-1 is not in the supplied evidence, so I could not verify it.

## To get a PASS, pick one

1. **Re-Refine as a combined story.** Resolve findings 1–5 in the text: profile default and call-site strategy, activation authority, the source of each tuple field, approval semantics, the policy-change source and the v6/`_tip` plan. Re-estimate with the existing test churn counted and keep visible margin under 4.0h.
2. **Propose an independently accepted split.** Both parts would block #119 and #129.
   - **300a, closed qualification profile and read/reserve gate:** the policy module, the default and activation decision, gates at approval, capture and reserve, the stale-prepare and retry branch, the healthy Codex stream and threading profiles through existing tests. About 2–2.5h.
   - **300b, durable coverage record (depends on 300a):** the v6 superset migration, `_tip`, `coverage_changes`, keyed idempotent writes at refusal and the migration and forged-input negatives. About 2–2.5h.

Either option needs its exact JIT before Develop.
