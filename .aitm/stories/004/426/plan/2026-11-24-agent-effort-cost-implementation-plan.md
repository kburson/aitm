# Agent effort and cost management implementation plan

**Status.** Proposed delivery plan, November 24, 2026. [#426 master plan and spike index](cost-management-master-plan.md) supplies the research basis. [#100's reviewed plan and amendments](../../../001/100/story.md) still govern its existing work.

**Goal.** Give engineers a reliable per-story and per-epic view of agent effort, observed usage, and cost evidence across their existing harnesses. Record which attempts contributed, how the data was attributed, and where coverage is missing.

**Architecture.** Short-lived capture adapters feed a portable, project-scoped receipt store. AITM owns assignment, reconciliation, pricing, and reporting. Review authority remains with AIPR. Use the existing Python 3.13 package and a separate portable entry point so this path can run without importing the host monitor stack. Start with standard-library subprocess, JSON, datetime, decimal, pathlib, and SQLite APIs.

## #100 delivery audit

The November 24 readback compared the [live child set](https://github.com/kburson/aitm/issues/100), open dependency edges, accepted planning records and trunk at [45db935a](https://github.com/kburson/aitm/commit/45db935ac73911b95320a3e38d19f177cedd4fd2). **#100 is open in Dev. 32 of 42 direct children are closed.** Its issue body contains an earlier point-in-time inventory. The live graph and later amendments govern current status.

### Completed and reusable

| Delivered area | Evidence | Reuse in the proposed path |
| --- | --- | --- |
| Baseline collector and research | #83 delivered the original local usage collector. #101 and #102 closed the Grok and Linux research. #100's design and implementation plan passed SAR, SPR and XPR. #103 closed the CI prerequisite. | Preserve historical observations and rate-card provenance. Carry forward source qualification lessons. |
| Storage and provider foundations | #111–#116 and #134 are closed. The delivered work covers host path hardening, atomic operations, project persistence, adapters and fixtures, registration and epochs, and the Linux Codex CLI carrier. | Reuse pure data types, field normalization, sanitized fixtures and identity rules. The host storage and admission implementation stays with the existing monitor. |
| Assignment, publication and recovery | #117, #118, #119, #122, #182 and #194 are closed. They cover scope and handoff, journal and claim order, project writes and ACK, the publication fence, and installed scope compatibility. #119 merged in PR #318. | Preserve the claim that evidence, assignment and publication each need their own stable identity. Use receipt tests for crash, conflict, replay, and earlier snapshots. |
| Scope qualification and scheduling | #120, #199, #201–#203, #209, #210, #300, #303, #304 and #310 are closed. These cover wake scheduling, proof and disposition, fail-closed admission, controlled source authority and journal-only candidates. #269 and #282 are closed research inputs. | Carry forward deny-by-default, exact source and gap reporting. Use existing provider and review proof to check a matching observation only within its authority. |
| Coordinator prerequisites | #325, #326, #329–#331 and #335 are closed. Trunk includes the watch and selected-source inventory, Grok capture and guarded delivery, new-stream enrollment, and Grok marker proof. | Retain these artifacts for #100 and mine their recorded fixtures. The proposed capture path uses explicit assignment and bounded reads. |

Representative delivery evidence includes [project delivery PR #318](https://github.com/kburson/aitm/pull/318), [source exclusion PR #308](https://github.com/kburson/aitm/pull/308), [guarded Grok delivery PR #333](https://github.com/kburson/aitm/pull/333), and [Grok scope proof PR #336](https://github.com/kburson/aitm/pull/336). Closed component work and code on trunk establish reuse candidates. Integrated service delivery and production activation remain open.

### Still open

| Story | Live status | Work remaining |
| --- | --- | --- |
| #121 | Planning, no open direct blocker | Assemble the delivered prerequisites into the root-watch and coordinator path. Its recovery plan still needs implementation. |
| #123 → #124 | Backlog | Finish fenced reports and a versioned compatible export, including receiver-fixture qualification and reconciliation. Trunk still routes the monitor report command to an unavailable handler. |
| #320 → #125 → #126 | #320 Refine, #125 and #126 Backlog | Finish owned wake hook installation, service lifecycle, backup and adoption, and rollback. #125 also depends on #121 and #124. The November 19 amendment removed LaunchAgent and systemd service registration from first release and retained same-user verification and the cutover receipt. |
| #127 → #128 → #129 | Backlog | Integrated privacy and scale, controlled macOS carrier qualification, and controlled Linux release qualification. #127 waits for #126. |
| #137 → #129 | #137 Refine | Finish Linux Grok carrier proof alongside #128 as a live prerequisite for #129. |

Related open scope includes ordinary Claude monitor qualification in #301 (#135, #295, #298), folded Claude accounting in #297 (#204, #270, #296), and live Core Cost receiver qualification in #230 after #51, #123 and #124. The [qualified-release re-acceptance](../../../001/100/plan/2026-11-14-100-qualified-cost-acceptance-r2.md) limits #100's first-release live monitor scope to qualified Codex and Grok sources and records Claude as unavailable. The [portable service amendment](../../../001/100/plan/2026-11-19-100-portable-service-amendment.md) still calls for host-specific process verification. The [current epic](../../../001/100/story.md) retains its dependency edge to Core #2 and separate production cutover authority.

## What #426 changed

| Research evidence | Design consequence |
| --- | --- |
| [#427–#428 interactive and exact delayed recovery](cost-management-master-plan.md#investigation-results) covered configured local sessions on all three harnesses. Arbitrary attachment to an existing chat and remote history remain unqualified. | Support explicit opt-in for configured chats and named exact recovery. Keep unknown scope visible. |
| [#432 self-report](../../432/attachments/self-report-results.md) recovered prior turns, with about 34–35% additional tokens for a dedicated reporting turn in short trials. [#429 headless](../../429/attachments/headless-results.md) captured all three providers with structured completion and exact lookups. | Prefer capture outside the model loop. Make self-report a deliberate fallback. Treat capture capability as provider, version, and surface dependent. |
| [#430](../../430/attachments/xpr-turn-results.md) and [#431](../../431/attachments/xpr-delivery-results.md) tied two sealed rounds on Claude and Grok to exact reviewer turns. Receipts arrived late and out of order, and replay did not change totals. [#434](../../434/attachments/codex-review-lock-results.md) captured usage for both failed Codex attempts while the sealed reviewer route remained blocked on the tested macOS setup. | Preserve outcome, usage coverage and sealed authority separately. Read AIPR decisions through its existing authority and accept a separate usage companion. |
| [#433 epic trails](../../433/attachments/epic-trail-results.md) reconciled 443,354 assigned tokens, 75.776 seconds of summed agent engagement, and 57.186 seconds of working wall time. It covered marked sequential work, parallel and nested workers, a fresh-agent handoff and later attribution. | Keep explicit assignment boundaries and disjoint usage coverage. Count engagement by agent and take the union for working wall time. Actual overnight and cross-machine restart operation still need qualification. |

Provider outputs also differed on resumed cumulative counters, cache accounting, reasoning, cost indicators, and cancellation. Signed-in tests verified usage and some pricing indicators, with no actual per-story subscription charge evidence. Keep measured units, provider-reported price or credit indicators, API-equivalent estimates, and verified billed amounts as separate measures. Never imply a subscription's incremental charge from an API rate or an empty observation.

## Delivery decision

**Recommend an explicit, session-scoped path as the first release.** It covers assigned story runs, epic trails, and supported reviewer receipts with the provider harnesses engineers already use. It also works for a team that chooses one provider, since it can enable only that adapter.

| Option | Benefits and cost |
| --- | --- |
| Finish #100's monitor first | Retains the approved always-on discovery and parked-session workflow. Requires the ten open direct children, remaining qualification and separate cutover. Its OS-specific process and watch dependencies do not fit the portable capture boundary. |
| Deliver session-scoped capture with an explicit compatibility boundary | Gives useful story and agent coverage before always-on discovery and integrated cutover. Engineers or orchestration enroll each run or configured chat. Missed enrollment is visible as a gap. |
| Rewrite both at once | Could unify future capture and supervision, but would couple the first release to legacy takeover, host discovery, and AIPR lifecycle changes. Carry these as separate decisions. |

Keep this proposal beside #100's accepted plan until the owner decides whether to retain, defer, or replace its continuous-service scope. If the decision changes #100, re-accept the scope and reconcile live dependencies, particularly #2, #123, #124 and #230. Preserve the approved receiver contract, writer guard, cutover requirements and known coverage until that decision. The stand-alone pilot reads only approved artifacts and uses isolated state. It needs no production monitor takeover.

## Implementation contract

- **Portability.** Add `aitm_usage.effort` and an `aitm-effort` Python console entry point in the existing package. Use one code path for Linux, macOS and eventual Windows. Project-built binaries, compiled extensions, OS-specific capture code, kernel queries, POSIX shell scripts, native watch APIs, and service managers stay outside this path. Provider binaries stay external. Exercise Windows import and fixture tests early and publish live Windows support only after qualification.
- **Identity and custody.** Persist an immutable enrollment before capture with project, epic or story (or unattached), run, attempt, role, optional parent attempt, and review binding. Bind the observation to a verified harness/version/surface, exact native session and turn or request, and typed source proof. Include provider accounting scope in identity when native IDs are scoped. Establish the project and operation authority from the trusted caller and provider source. A reported ID or a digest alone supplies no authority. Keep raw transcripts private and retain sanitized provenance.
- **Receipt and reconciliation.** Version strict canonical JSON. Store evidence revision, coverage, terminal outcome, time basis, measured categories, price provenance and observed/recorded times. Keep stable observation identity distinct from attempt identity and payload digest. An identical replay is a no-op. A conflicting binding or unordered incompatible evidence enters reconciliation. A proven late completion updates the effective observation without appending the same usage to totals. An older partial arriving after completion stays superseded if the lineage is verified. A fresh execution gets a new attempt even when the prompt matches. Preserve unknown and zero as distinct values.
- **Time and attribution.** Attribute late receipts using the original enrollment, even after the session changes stories. Allow one explicit, authorized link for unattached work. Keep mixed turns with no internal witness unassigned. Union overlapping verified engaged intervals per agent/session and sum across agents. Union comparable wall-clock intervals across agents for working wall time. Show first-to-last workflow elapsed separately. Keep idle and owner waits outside engagement, and never union incomparable clocks or silently fill missing intervals. Keep nested disjoint usage separate from inclusive parent totals.
- **Storage and visibility.** Start with local user-controlled, per-project SQLite state and short transactions. The runtime owns privacy and local access through a configured private state directory. Shared or untrusted state and remote multiwriter operation are outside the initial trust model. Use transaction constraints and test concurrent local writes. Store a separate measurement snapshot version. Keep #83 and #100 exports byte-stable and use approved exports as read-only compatibility inputs. Do not import the existing `ledger.py`, `scopes.py`, `export.py` or `cli.py` into the portable entry point. They take host-specific dependencies. Reuse pure types and pricing when contract tests show equivalent semantics, and reuse the existing `relationships` logic after import and compatibility checks.
- **Small tools.** Provide explicit CLI operations for enrollment, capture/recovery, ingest, attribution, report and export. Accept only configured provider capabilities and authorized evidence inputs. Optional MCP wiring should expose the same typed operations and authority checks. Capturing usage carries no shell, backlog, git, DB administrative or review authority.

## Build slices and acceptance

Split the following into bounded leaf stories after scope approval. Keep each leaf within the repository's engagement limit and review it against exact-head evidence. File paths below are relative to `packages/aitm-usage`; place regression tests in its existing test layout. Test the first three providers against the sanitized #426 receipts on every relevant adapter change.

### 1. Receipt and store foundation

Files: `src/aitm_usage/effort/{__init__,receipts,store}.py`, `tests/test_effort_store.py`, and sanitized input fixtures.

- [ ] Define `Enrollment`, `UsageReceipt`, and `EffortStore.enroll`, `EffortStore.ingest`, and `EffortStore.snapshot`. Return typed statuses for inserted, replayed, pending, refined and conflicted. Fix the schema, unique keys, and validation errors in fixtures before writing adapters.
- [ ] Prove restart and parallel-writer replay, conflict isolation across attempts and projects, partial-after-full ordering, and transaction rollback across the observation and snapshot update. Assert fixture data never includes transcripts, keys or host paths. Run `uv run --project packages/aitm-usage pytest packages/aitm-usage/tests/test_effort_store.py`.

### 2. Headless capture and exact recovery

Files: `src/aitm_usage/effort/capture.py`, `src/aitm_usage/effort/adapters/{codex,claude,grok}.py`, and provider-focused capture tests.

- [ ] Give adapters one contract for `observe(event)` and `recover(exact_ref)`. Keep subprocess selection, bounded streams, timeout and terminal status in the caller. Use argument vectors and a minimal launch environment. Preserve provider sign-in and default sandbox. Exercise a fixture where the subprocess exits successfully after a cancellation and another where a failure still yields usage.
- [ ] In separate provider leaves, qualify Codex resume deltas only against a trusted baseline and exact rollout, Claude final request and per-result data with cache buckets, and Grok exact session/turn identity with separate ticks. Preserve partial counts, observed outcome and unknown settlement. Treat malformed data, unexpected build and wrong turn as typed gaps. Bound reads to the assigned run. Compare all counters to #429 receipts and reuse #83/#100 parser fixtures where applicable.
- [ ] Add `recover` for explicitly selected retained sessions and configured interactive completion hooks where supported. Prove live capture and later recovery resolve to one observation. A failed lookup leaves a coverage gap. Measure capture with no extra model turns in the normal path.

### 3. Boundaries, handoffs and rollup

Files: `src/aitm_usage/effort/{assignments,rollup}.py` and `tests/test_effort_trail.py`.

- [ ] Implement scope start/end and detach/attach markers bound to exact native identity, and `EffortStore.attribute` with one authorized compatible link per unattached observation. Prove an overnight-style trail with multiple completed children, a late worker receipt after the parent changes stories, fresh-agent handoff, and a mixed turn with no safe split.
- [ ] Implement `rollup(snapshot, target)` with per-role and per-provider counts, disjoint nested coverage, separate engagement/union/elapsed measures, and explicit clock and pricing gaps. Reconcile to the published #433 fixture. Reject arbitrary receipt reassignment or cross-project queries. Prove a nested inclusive aggregate with unknown split keeps coverage without duplicating tokens or monetary indicators.

### 4. Reports and compatibility

Files: `src/aitm_usage/effort/{cli,report,export}.py`, package entry point, `tests/test_effort_report.py`, and README.

- [ ] Add story, epic and unattached drilldown with role, provider, attempts, outcomes, coverage and rate basis. Provide structured output and human-readable totals. Show measured, estimated and billed values independently. For absent price or settlement print unknown. Render fixed-snapshot exports deterministically.
- [ ] Define a read-only compatibility adapter for approved legacy snapshots after verifying the fixed export contract. Retain original identity and sequence. Prove a known imported row and the corresponding new observation reconcile or remain separate with explicit overlap. Block aggregate claims when coverage cannot be partitioned. Keep receiver writes for #124/#230 or a separately accepted integration.

### 5. AIPR companion receipts

Files: `src/aitm_usage/effort/review_receipts.py` and `tests/test_effort_review_receipts.py`.

- [ ] Accept linkage to existing sealed decision evidence using review, round, attempt, reviewer identity and artifact/response digests. Treat decision and usage as independent observations. A late receipt can settle against the existing decision without a model call. Verify against the #431 Claude and Grok fixtures. Reject mismatched identities and preserve failed Codex attempts with measurable usage and no decision.
- [ ] Reproduce two rounds, delayed/reversed receipt order, interruption, and replay through the unchanged qualified AIPR routes during pilot. Carry a narrow join/submit operation and same-owner process checks into a later AIPR design review. Full Codex sealed-review coverage requires its own supported sandbox proof.

### 6. Release qualification and bounded pilot

Files: release matrix, portable test targets, and pilot evidence under the implementation leaves.

- [ ] Verify package import and installation on Linux and macOS without the monitor CLI, a daemon, compiled project code or OS-specific access. Run the effort fixture suite on Windows to catch path, encoding and process assumptions. Keep fixture compatibility distinct from live provider support.
- [ ] Run a consented test project with one same-provider story and one cross-provider epic trail. Freeze a snapshot, compare manual exact observations to report totals and exercise restart while receipts are pending. Record workload size, capture duration, retry count, any extra model turns, and privacy/coverage readback. The first run sets a measured overhead budget for subsequent changes.
- [ ] Qualify each shipped provider/host/version capability. Gate release on zero duplicate observations in the declared corpus, exact known rollup parity, explicit unknowns, private raw evidence, and provider-supported routes with sandbox authority preserved. Report partial interactive, billing and Codex sealed-review availability beside the release matrix. Schedule Windows live qualification as a follow-on once provider surfaces are available.

The first release can be evaluated before any provider billing comparison, AIPR rewrite, change to #100's production state, or always-on service adoption. Use bounded, authorized billing evidence later to qualify lag, conversion and currency; keep the source and basis attached to any billed amount.
