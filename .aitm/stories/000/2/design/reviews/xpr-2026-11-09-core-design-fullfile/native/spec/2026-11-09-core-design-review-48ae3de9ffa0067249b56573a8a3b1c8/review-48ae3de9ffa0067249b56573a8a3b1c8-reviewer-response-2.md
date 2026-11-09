<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-48ae3de9ffa0067249b56573a8a3b1c8"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_commit: "86ac9caf47c95d6443e329759ede387c2cfe37e6"
artifact_blob: "dfed3624be221f3f7358a00b065bbbc2a456cbc4"
artifact_digest: "sha256:3355a89fdfd38e16b9f4aeb37fc8fb368ea74ce8b7e608f0504b67a2e9288253"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:35a1a3958c703c369c77ad51a58d221a0d89a598752b450dcfc98a8a996b9cb8"
  identity_source: "runtime"
started_at: "2026-11-09T12:48:50.030Z"
submitted_at: "2026-11-09T13:01:23.830Z"
finding_ids: ["R2-F001","R2-F002"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revisions requested. This is round 2 of the separate full-file validation of `.aitm/stories/000/2/design/core-design.md`. The reviewer is Anthropic Opus 5.5 at effort high, in the same registered session as round 1. The author is gpt-6-astra (Codex).

### Fresh full-file reread

- Tool: Read, contiguous chunks of at most 60 lines, in this round, restarting at line 1 after the author's revision.
- Ranges read: 1–60, 61–120, 121–180, 181–240, 241–300, 301–360, 361–420, 421–480, 481–540, 541–600, 601–660, 661–710. The final request (offset 661, limit 60) returned through the end of the file: EOF.
- Observed line count: 709 authored lines plus the terminating newline. The Read display shows a 710th, empty element. The author's note on round 1 applies here too: round 1 showed 658 display elements for a 657-line file for the same reason.
- Native input artifact identity, from this turn's package-generated response header (shell access is unavailable in this session, so I did not recompute it): `artifact_digest` `sha256:3355a89fdfd38e16b9f4aeb37fc8fb368ea74ce8b7e608f0504b67a2e9288253`, `artifact_blob` `dfed3624be221f3f7358a00b065bbbc2a456cbc4`, `artifact_commit` `86ac9caf47c95d6443e329759ede387c2cfe37e6`.
- Truncation: none. Grep for `^.{2000,}$` over the FUR returned 0 matches, so no line was silently truncated.

### Preceding responses read

I read my round-1 response (`reviewer-response-1.md`) and the complete author response (`author-response-1.md`). I also checked the real v0 store records the design must migrate: `.aitm/stories/000/3/story.md` (header), `.aitm/stories/000/3/events.jsonl` (all 8 lines), and a Grep confirming a `kind:` header in all 72 `story.md` files under `.aitm/stories/000/`.

### Verification of round-1 dispositions

- **R1-F001 — resolved.** Kind now has a typed source: `graduate --kind` recorded in `core.story.graduated` (FUR 267, 386, 632). The only M1 kind change is the new `core.kind.changed` (268), produced by `split`. `split` is bounded to an oversized story, defect or spike in Refine before any Develop attempt. It converts the item in place into the same-ID Backlog epic, invalidates old acceptance and estimate applicability while keeping their history, and creates children through the normal graduation route (388–390, 634). Planning guards per kind are explicit: leaf-size applies to story, defect and spike only, and an epic's aggregate estimate has no ceiling (404). v0 kind mapping is defined, with unknown kinds left unresolved (663). The new "Kind and splitting" acceptance row covers all of this (682). Consistency check: the Refine→Backlog move in split matches the existing design-rework edge (394). A leaf found oversized later, at Plan or JIT, can still reach `split` by design-rework demotion to Backlog and then Refine, so no edge is missing.
- **R1-F002 — resolved.** `aitm.source-review/v1` now has a schema, an adapter, retained response bytes and source/attempt/generation binding (487). `[review.source]` policy requires `distinct-session` independence, checked against retained binding history, not against the envelope's own claims (131–134, 489). Declared assurance limits are stated truthfully (491). The "Source-review evidence" acceptance row covers self-review, an uncomparable identity, an omitted implementing participant, mismatched source and unresolved required findings, plus conforming activation at its actual time (692). This does not touch the open document review-depth matrix.
- **R1-F003 — resolved.** New acceptance rows cover "Reconfiguration" (680), "Human pivot" (683) and "Pre-story editing/discard" (693). They state the provider-neutral scope and keep the actor-authentication limit.
- **Optional suggestions 1–5 — all adopted and verified.** `expand` now takes `--kind/--draft/--reason` and creates a Backlog child that passes the ordinary gates (543, 636). `core.doc-review.opened` exists and is the outer start, with Unknown for legacy records (288, 535). The JSON-scalar header resolver has cross-language test vectors (454). Entity-scoped `idea open` / `draft open` / `sync --entity` / `unbind --entity` exist (350, 630, 633). The labeled fixture review policy states it is not a product default or owner decision (118–140).

None of the revisions decides an open owner choice. The expansion-completion boundary, second-trip cap, review-depth matrix and every-push audit remain open (156, 460, 546, 709).

### New findings

Two required gaps remain. Both concern the real store the design must carry forward: the accepted core plan has already decomposed #2 into leaf stories #3–#72 on planning, created by a "manual-bootstrap" route that bypasses the normal CLI, and the design has neither a lifecycle route for those children nor a migration contract for their record shapes. These records were already present at round 1's input commit (`bcacb13`, "Publish core leaf records…"); I missed them in round 1. They are raised now because the instructions require reviewing the full current FUR against the accepted parent and owner scope, not only historical findings.

1. Children decomposed from an accepted parent plan have no design-acceptance, estimate or graduation contract (R2-F001).
2. Migration mapping and fixtures cover only the #1/#2 record shapes, not the #3–#72 shapes actually present in the v0 store (R2-F002).

## Findings

### R2-F001 — Leaves decomposed from an accepted parent plan have no design-coverage, estimate or graduation contract, so they cannot reach verified Done

**Severity:** high. **Required.**

**Where:**
- FUR 404: "Backlog exit for every kind requires the complete structured description and current accepted design."
- FUR 410–411: the guard table's `design-accepted` row.
- FUR 390: children are created "through ordinary `graduate --kind ... --parent <epic>`", which takes a `<draft-handle>` (632).
- FUR 276: `core.estimate.set` phases are `refine`, `plan` and `jit` only.
- FUR 497 and 505: sign-off "evaluates all applicable lifecycle requirements, including previously waived ones", and advisory override yields only `done/unverified`.
- Parent and owner context: architecture 115 (Backlog leaves when "Design accepted"); master plan 28 ("its accepted implementation plan decomposes into leaves of at most four hours").
- Real store: `.aitm/stories/000/3/story.md` header (`plan-origin` binding the parent plan's publication, raw digest and section digest; `files.design: []`) and `.aitm/stories/000/3/events.jsonl` lines 1 and 4 (`origin_kind: "accepted-parent-decomposition"`, `draft_history: "synthesized at record creation; no prior draft conversation"`, estimate phase `parent-plan-decomposition`).

**Problem:** the master plan makes plan decomposition into leaves the normal way a section epic produces work, and #2 has already been decomposed into 70 leaves. The design gives those leaves no route:

- **Design coverage.** A decomposed leaf has no design document of its own. Its "what to build" is a digest-bound section of the parent's accepted plan, under the parent's accepted design. Under FUR 404, every such leaf needs its own design accepted under the configured policy before leaving Backlog. Advisory can waive that, but sign-off re-evaluates waived requirements, so each leaf ends `done/unverified` and cannot satisfy a delivered dependency (446) for the leaves that follow it. The effect is one of two outcomes:
  - per-leaf design documents plus the configured review levels for every decomposed leaf, which the design silently forces without saying so; or
  - the tool being the reason those stories can't close, contrary to the architecture's first goal (architecture 28).

  Neither outcome is stated, and whether a plan-section binding may satisfy Backlog design coverage is not expressible at all in the policy schema (FUR 118–140, 456–462).
- **Estimate phase.** The leaves carry a decomposition-time estimate. The design has no phase for it and does not say whether it satisfies the Refine estimate guard or must be re-recorded in Refine.
- **Graduation without a draft.** `graduate` requires a draft handle and freezes a draft snapshot (580, 586). Decomposed leaves have no draft. The bootstrap route synthesized one, which is the kind of manufactured record the design otherwise avoids.

**Why required:** this is a missing lifecycle contract on the main path from an accepted section plan to deliverable leaves, and the M1 work itself is planned through it. A builder must invent either the inheritance semantics or a mass per-leaf design obligation. Both choices touch owner-level review scope, so the design should give the policy a way to express that choice, not leave it implicit.

**Requested change** (it does not select the open review-depth policy):

1. Define a typed decomposition route, for example `decompose <epic> --plan-section <key>` or `graduate --from-plan-section`. It creates a child from an accepted parent plan section without a synthesized draft, binding the parent design and plan canonical digests and the section key and digest, under the normal identity protocol and the one-intent-per-entity rule.
2. Define an explicit design-coverage evidence kind for such children (for example `parent-plan-section`). Committed review policy may permit or deny it for Backlog exit. If the policy does not permit it, the guard reports unavailable or failed, never an inferred pass. If policy requires per-leaf design, say so explicitly.
3. State that a later change to the parent plan section or design digest invalidates that coverage, as authored edits do.
4. Add an estimate phase for decomposition, or state that the Refine estimate guard needs a fresh `refine` estimate.
5. Add acceptance cases: decomposition-bound coverage is accepted only when policy permits it; it is refused or unknown when policy omits it; it is invalidated by a parent plan change; the leaf's estimate is handled as stated; no draft is synthesized.

### R2-F002 — Migration mapping and fixtures name only #1/#2 shapes, while the actual v0 store contains #3–#72 with additional event and header shapes

**Severity:** medium. **Required.**

**Where:**
- FUR 661: "For #1/#2 it maps `core.state.entered` … pairs `core.link.child-added` and `core.link.parent-set` …"
- FUR 663: kind mapping, "#1 and #2 remain epics".
- FUR 665: unknown or contradictory material "blocks only an unsafe cutover".
- FUR 671: tests use "copies of the actual hand-built #1/#2 fixtures".
- FUR 698: Migration acceptance row, "Actual #1/#2 v0 fixtures".
- FUR 310: last-worktree "physical path stays clone-local".
- Real store, story #3 (representative of the 70 decomposed leaves):
  - events: `core.link.dependent-added` with `{"blocking": N}`; `core.estimate.set` with phase `parent-plan-decomposition` plus `priority` and `plan_key`; `core.story.graduated` whose `from` is a plan path with `plan_key`, `origin_kind` and `draft_history: synthesized`; a top-level `provenance` block (`route: manual-bootstrap`, `runtime_transition: false`, source publication and digest) on every event.
  - header: `plan-origin`, `priority`, `blocking`, and an absolute `last-worktree` path.

**Problem:** C6 migrates the real planning tip, which now has 72 stories, not two. The adapter contract and the test corpus enumerate only the #1/#2 shapes:

- `core.link.dependent-added` has no stated mapping into the reciprocal, cycle-checked dependency relation (446).
- The `parent-plan-decomposition` estimate phase has no stated mapping (see R2-F001).
- The manual-bootstrap `provenance` envelope has no stated mapping to imported, non-runtime facts.
- Absolute `last-worktree` paths have no stated conversion to clone-local worktree identity.

Under FUR 665, unmapped required facts in 70 stories either block cutover or force ad hoc mapping at apply time. In particular, dependency facts are needed for the Ready-for-Plan guard. A builder following FUR 671/698 literally ships an adapter tested only on #1/#2 that fails on the real store.

**Requested change:**

- Make the adapter contract inventory-driven over the pinned tip: every observed v0 event type, data key and header field is mapped, retained opaquely under explicit schema status, or listed as a cutover blocker.
- Name the mappings for the shapes listed above:
  - dependent links → the directed, reciprocal dependency relation, with reciprocal consistency checks;
  - decomposition estimate and graduation → the R2-F001 contract;
  - `provenance.route = manual-bootstrap` / `runtime_transition: false` → imported, non-runtime facts that never claim CLI-observed workflow execution;
  - absolute `last-worktree` → clone-local identity, with the original path retained as provenance.
- Extend the Migration acceptance row and test fixtures to copies of the full current corpus, or at least a representative decomposed leaf plus the full-corpus dry-run inventory. Do not limit them to #1/#2.

The master plan's C4 wording ("Actual #1/#2 v0 fixtures") is downstream and should follow this change in its own validation. This finding does not ask the design to edit it.

## Required changes

1. R2-F001: define the typed decomposition route from an accepted parent plan section (no synthesized draft). Define a policy-expressible design-coverage evidence kind for decomposed children, with invalidation when the parent plan or design changes, and leave it unavailable unless policy permits it. Define how the decomposition estimate relates to the Refine guard. Add acceptance cases.
2. R2-F002: make v0 migration inventory-driven over the full current tip. Map `core.link.dependent-added`, the decomposition estimate and graduation, manual-bootstrap provenance and absolute `last-worktree`. Extend the migration fixtures and acceptance row beyond #1/#2.

Round-1 findings R1-F001, R1-F002 and R1-F003 are verified resolved. No open owner choice is decided by these requests.

## Optional suggestions

1. **Stray hard line break (FUR 543–544).** The expansion-transaction paragraph breaks mid-sentence after "Advisory may record a waived continuation,". Markdown renders it as one paragraph, but the break looks accidental and becomes part of the canonical body bytes. Consider joining the lines.
2. **Oversized leaf discovered at Plan or JIT (FUR 388, 394).** `split` is Refine-only. A leaf found oversized during planning reaches it by design-rework demotion to Backlog and then Refine. One sentence saying so would stop builders from adding a Plan→Refine edge. The real leaf records already say "At JIT, resplit/review if current evidence makes the cap implausible", so this path will be used.

## Decision

revisions-requested
