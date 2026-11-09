<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-48ae3de9ffa0067249b56573a8a3b1c8"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_commit: "bcacb1378ca2cf268bb194cdf80f4fe21f155b2d"
artifact_blob: "767b7bbf82da157494fc94feb5ebf3092c97ed55"
artifact_digest: "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8"
  identity_source: "runtime"
started_at: "2026-11-09T12:48:50.030Z"
submitted_at: "2026-11-09T12:53:12.820Z"
finding_ids: ["R1-F001","R1-F002","R1-F003"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revisions requested. This is the owner-authorized separate full-file validation (2026-11-09) of `.aitm/stories/000/2/design/core-design.md`, by an Anthropic reviewer (Opus 5.5, effort high), independent of the earlier accepted SAR/SPR/XPR records. I did not use earlier review responses to scope this round; I assessed the current FUR's contracts on their own.

### Fresh full-file reread

- Tool: Read, contiguous chunks of at most 60 lines, in this round, started at line 1 after joining.
- Ranges read: 1–60, 61–120, 121–180, 181–240, 241–300, 301–360, 361–420, 421–480, 481–540, 541–600, 601–658. The last request (offset 601, limit 60) returned lines 601–658 and nothing beyond: EOF.
- Observed line count: 658.
- Native input artifact identity (from the package-generated response header for this turn; I did not recompute it, because shell access was not available in this session): `artifact_digest` `sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d`, `artifact_blob` `767b7bbf82da157494fc94feb5ebf3092c97ed55`, `artifact_commit` `bcacb1378ca2cf268bb194cdf80f4fe21f155b2d`.
- Truncation: none observed. To rule out silent line truncation I ran a Grep for lines of 2,000 or more characters (`^.{2000,}$`) over the FUR; it found 0 matches, so every long line was returned in full. Later Grep searches that printed "[Omitted long matching line]" were confirmation searches only, not part of the reread.

### Context read

`.aitm/README.md`; `.aitm/stories/000/1/draft.md` (owner decisions, including the builder-check answers, installation, planning-branch guarding and review-timing sections); `.aitm/stories/000/1/design/architecture.md` in full (including the reconciliation list on line 226); `.aitm/stories/000/1/plan/master-plan.md` in full; `.aitm/stories/000/2/draft.md`; `.aitm/drafts/2026-11/20261108-1310-peer-review/draft.md`. To find the finding-ID convention only, I opened the first reviewer response of the earlier native core XPR.

### Assessment

The design is coherent and implementable for the great majority of its surface. I checked that it reconciles each item the architecture handed down on its line 226: single-owner persistence through the append API with no event union (FUR 200–217, 235, 298); the versioned canonical authored-content digest and metadata migration (416, 620); M1 review import through the CAS writer (426); authoritative default-branch configuration with bootstrap and freshness (116–134); delivery before Done, with merge, squash, rebase and core-only local evidence (455–459); evidence recovery (463); and the root `README.md` as a bounded migration input rather than a permanent exception (168–170).

It preserves the settled owner decisions: the implementation-only four-hour clock per attempt; one expansion per attempt with no nested allowance; the origin paused and blocked while its expansion runs; no required human gate, with `pivot` the only human-only command; agent sign-off on leaving Review; a fresh allowance and clock after a trip decision and new plan; and the configurable orphan planning branch. It keeps the open questions open: the expansion-completion boundary, the second-trip cap, the review-depth matrix and the hosted every-push audit (132, 422, 501, 657). The addition of `done/unverified` as a fifth labeled value beside the architecture's four dispositions is justified in the text (358) as the advisory historical outcome, and is never treated as delivery. I do not raise it.

Three required gaps remain. Each leaves a lifecycle step or an owner-mandated rule without a contract or without acceptance proof:

1. Nothing assigns or changes a story's `kind`, there is no "split" route out of Refine, and the leaf-size guard's applicability to epics and spikes is unstated (R1-F001).
2. The code/deliverable review evidence that stops the clock and gates Review exit has no defined record schema or independence/assurance policy for core-only operation (R1-F002).
3. The acceptance matrix has no proof for `pivot` (the owner's only human-only path) or for the anchor/issuer fence of `init --reconfigure` (R1-F003).

## Findings

### R1-F001 — Story kind has no source, there is no split route, and the leaf-size guard's scope by kind is undefined

**Severity:** high. **Required.**

**Where:** FUR 284 (`story.md` frontmatter includes `kind (story, epic, defect, spike)`); 243 (`core.story.graduated` data: "from draft, issue ref", with no kind); 255 (`core.expansion.recorded` has kind defect or story); 370 (guard table titled "Core guards for story/defect leaves (kind substitutions follow)"); 376 (Refine exit `estimated / leaf-size`: "leaf estimate ≤ configured four-hour limit"); 387–393 (the kind matrix starts at Plan exit/Develop entry); 409 ("An epic passes design/estimate/plan gates"); 584–591 (CLI). Parent: architecture 116 (Refine leaves when "Estimated; leaf ≤ 4 h or split"); owner, `../../1/draft.md` 51 ("Leaf stories are no larger than 4 agent-hours").

**Problem:**

- **No source for `kind`.** Guards, clocks, Test and Review behavior all branch on kind (the kind matrix and 405–410), yet nothing in the design sets it. `graduate` has no kind input, `core.story.graduated` carries none, `describe` has no kind field, and no event type or command records a kind change. Only expansion children get a kind (defect or story). A builder must invent where an epic or spike comes from, and the fold has no typed fact to compute it from.
- **No split route.** The architecture's Refine exit is "leaf ≤ 4 h *or split*". The FUR mentions neither splitting nor the transaction that turns an oversized story into an epic with children (kind change, child graduation or links, invalidation of its leaf estimate and design acceptance, if any). An oversized story therefore has no defined exit from Refine.
- **Leaf-size scope by kind.** The guard table is written for story/defect leaves, and the kind matrix specifies substitutions only from Plan exit onward. Line 393 says "no implicit guard inheritance reintroduces exempt requirements", and line 409 says an epic passes "estimate" gates. Read literally, either the ≤4 h leaf-size guard applies to an epic's aggregate estimate (blocking every real epic) or no Refine/Backlog guard is defined for epics and spikes at all. The text does not say which.

**Why required:** this is a lifecycle contract the builder cannot derive. It affects the event schema, the fold, the CLI and the guard registry, and an M1 epic (including #1/#2 after migration, whose v0 kinds must map to something) cannot be walked as specified.

**Requested change:** define (a) how kind is recorded: for example a `--kind` input on `graduate`, carried in `core.story.graduated`, plus a typed `core.kind.changed` (or an equivalent operation) with its allowed transitions and states; (b) the Refine split operation or edge, naming the facts it records and the evidence it invalidates; and (c) the Backlog, Refine and Ready guards for each kind, stating explicitly that leaf-size applies only to story, defect and spike and what epic Refine exit requires instead. Add an acceptance row or case for an oversized story being split, and for an epic and a spike passing Refine. Migration should state how v0 stories get their kind. This does not touch any open owner choice.

### R1-F002 — Core-only code/deliverable review evidence has no defined record schema or independence/assurance policy

**Severity:** medium. **Required.**

**Where:** FUR 261 (`core.review.recorded`: "retained pull-request/code review verdict, source, attempt and reviewer refs"); 383 and 389–390 (Review exit requires "effective source review"; spike requires "Independent review of that exact deliverable"); 449 (`review pass|changes --evidence <record>` imports "a verifiable review result for the same source/deliverable, attempt, reviewer identity and applicable policy … a core-only agent review has its retained signed-by-session/declared provenance and explicit assurance. Bare pass assertions are not authoritative evidence."); 595 (the nominal walk: "import a real independent code-review record"); 116–120 (the committed review-policy definition covers document levels).

**Problem:** this evidence stops the four-hour clock (449–451) and is the precondition for delivered Done, yet for core-only operation the design never says:

- **What the record is.** Its format and schema, which fields bind it to the source head/tree or deliverable digest and the attempt, and which adapter imports it. Document reviews have a detailed portable-record contract (416–426); code review has one sentence.
- **What makes it independent or verifiable.** Line 424 gives document reviews explicit participant topology (SAR, SPR, XPR) and assurance kinds. Nothing comparable exists for code review: the implementing session itself could author a "review record" with declared provenance. "Independent" (390, 595) is undefined, and "applicable policy" (449) has no defined policy surface, because the committed review-policy definition (116, 418–422) is about document levels and content binding, not code-review reviewer independence.

The owner made PR review the event that stops the clock (`../../1/draft.md` 147). Without a contract, a builder will either accept any declared record (so the implementer can stop its own clock) or invent a policy. Either way the Review-exit guard and the nominal walk's "real independent code-review record" step are untestable as written.

**Requested change:** specify the minimal core-only code/deliverable review record (schema identity; source head/tree or deliverable digest; attempt and generation; reviewer participant identity with session kind; verdict; finding/disposition summary; response bytes and digest), its import adapter, and a committed code-review policy element. That element should name the required reviewer relation to the implementing session (for example "distinct session" at minimum, with optional provider distinctness) and the permitted assurance kinds, reusing the identity-comparison rules of line 424. Add acceptance cases: a review record from the implementing session, from an identity that cannot be compared, or with a mismatched source fails to activate the review; a conforming record activates it and stops the clock. Provider-observed PR reviews remain M2.

### R1-F003 — Acceptance matrix omits `pivot` and the `init --reconfigure` anchor/issuer fence

**Severity:** medium. **Required.**

**Where:** acceptance table, FUR 630–647. Contracts with no row: `pivot` (259, 360, 412, 475, 505); anchor/routing change fencing and issuer-namespace continuity (116, 118, 120, 134).

**Problem:**

- **`pivot`.** This is the owner's only human-only command (`../../1/draft.md` 152), introduced so that an agent cannot relabel a planning failure as a change of direction. The FUR specifies that it refuses known agent or tool invocation and that `--as-human` cannot override a detected agent session (412); that a scope pivot moves the active leaf and its affected expansion to Plan atomically and bypasses ordinary guards (360); that it closes and fences the attempt, with a new accepted plan opening a fresh one (475); and that it records the expansion disposition coherently (505). It is also recorded separately so planning is not charged (owner, `../../1/draft.md` 77). No acceptance row exercises any of this. "Trip and attempt" covers trips only, and "Local lifecycle" mentions only that there is no routine human sign-off.
- **`init --reconfigure`.** Line 120 makes any change to committed anchor/routing fields (store UUID, planning remote/ref, genesis or legacy root, identity-issuing backlog provider and namespace) adoption-pending, fencing routine writes until `init --reconfigure` validates the old and new anchors. An issuer change must preserve every issued ID. "Init and policy" proves only that story-edited routing cannot change policy; it does not prove the fence on a *delivered* anchor change, reconfigure validation, or issuer continuity (for example a local→GitHub numbering switch without reconfigure refused, and with reconfigure preserving IDs).

These are safety and owner-rule contracts. The master plan's C1 and C3 checkpoints rely on "the accepted core design's entire acceptance matrix" (master plan 39), so anything missing here will not be planned or tested.

**Requested change:** add acceptance coverage. Pivot: a detected agent session, including one using `--as-human`, is refused; a genuine interactive invocation records `core.pivot.recorded` separate from any trip, demotes the leaf and affected expansion to Plan, fences the attempt and its admissions, and the next accepted plan opens a fresh attempt; pivot time and outcome are distinguishable from trips in outcomes and learning data. Reconfigure: a delivered anchor-field change fences routine writes in both modes; `init --reconfigure` with valid old and new anchors resumes; an issuer/namespace switch without reconfigure is refused, and with it preserves all existing IDs and provider references; a githost change cannot redirect the store ref. Optionally also add `draft discard` (tombstone, unique-suffix collision, retained history), which likewise has no row.

## Required changes

1. R1-F001: define how story kind is recorded and changed (graduation input, a typed event or operation, allowed transitions); define the Refine split operation; specify the Backlog, Refine and Ready guards for each kind, with leaf-size scoped to leaf kinds and the epic Refine exit stated. Add acceptance coverage and the v0 kind mapping.
2. R1-F002: define the core-only code/deliverable review evidence record, its import adapter, and a committed code-review independence/assurance policy element. Add acceptance cases covering self-review, an uncomparable reviewer identity and a mismatched source, plus the conforming activation path.
3. R1-F003: add acceptance rows for `pivot` (agent refusal, Plan demotion, fencing, fresh attempt, separation from trips) and for anchor/issuer changes and `init --reconfigure` (fence, validation, ID continuity).

None of these changes decides an open owner choice (expansion-completion boundary, second-trip cap, review-depth matrix, every-push audit).

## Optional suggestions

1. **`expand` inputs and the child's initial state (FUR 254–255, 499, 541, 591).** `expand` lists no inputs, yet finalization reuses the graduation protocol, which requires a frozen draft snapshot. State what `expand` takes (kind defect|story, reason, a draft or description source), which state the child starts in (presumably Backlog), and that the child then passes its normal kind-specific design, plan and JIT gates before its own Develop clock starts. A builder can infer this, but stating it removes a choice that affects how long origins stay paused.
2. **A typed fact for `review open` (FUR 263–264, 491, 640).** The event table has only `core.doc-review.submitted` and `.completed`, while the live lifecycle and the acceptance row ("opened before its first turn") rely on a durable open fact for rebuild. Either add `core.doc-review.opened` or state that the story operation record is that fact. Also state whether the level's `started_at` in `.completed` comes from open or from the first turn's start.
3. **YAML value typing in `aitm.authored-content/v1` (FUR 416).** "Schema-defined JSON-compatible subset" leaves scalar typing open (YAML 1.1 vs 1.2 booleans such as `yes`/`on`, unquoted timestamps, numeric forms such as `1e3` and `0o12`). Pin the resolution rule (for example YAML 1.2 core schema with timestamps kept as strings, or schema-typed coercion) in the test vectors, so peer-review and core cannot compute different digests from the same header.
4. **Draft and idea editing route in the CLI table (FUR 208, 297, 324, 586).** The table has `draft open` but no explicit save/sync route for an unbound draft, and no edit route for an idea body after `idea add`. Name the command, or state that `sync` covers an opened draft handle.
5. **A `[review]` policy example (FUR 86–112, 116, 418–422).** The configuration example omits the mandatory review-policy definition that the text requires. A short illustrative `[review]` table (policy ID/schema, `exact-content` binding mode, levels per role, exception authority), clearly labeled as a fixture and not a product default, would make the schema concrete without deciding the open review-depth matrix. If R1-F002 adds a code-review element, place it alongside.

## Decision

revisions-requested
