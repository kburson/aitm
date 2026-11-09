<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-19d319c42ae6474b0b404114fd611a9c"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/1/design/architecture.md"
artifact_commit: "42c19d20382c324703e791390a6f8747640974b9"
artifact_blob: "53345663dd176a1c51703ad26ce34ae791ca83f8"
artifact_digest: "sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:767689f69b20228949123d8faba84671fb404a4027e939125a5f4ad422c4d3a4"
  identity_source: "runtime"
started_at: "2026-11-09T03:53:44.261Z"
submitted_at: "2026-11-09T03:57:41.019Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revisions requested. This is an independent cross-provider (XPR) review by an Anthropic model of the post-SAR/SPR architecture, whose SAR and SPR rounds both ran on OpenAI models. The reviewed FUR is `.aitm/stories/000/1/design/architecture.md` at the digest in the frontmatter above (the same digest SPR accepted).

Reading order: the decision record (`../draft.md`) in full; the complete FUR; the master plan (`../../plan/master-plan.md`); the context-only core design (`stories/000/2/design/core-design.md`); the peer-review draft, including its interim procedure (`drafts/2026-11/20261108-1310-peer-review/draft.md`); the store README (`.aitm/README.md`); and the SPR reviewer and author responses (read after forming my own view, to avoid re-raising points already checked). I did not read the SAR responses. I made no network calls this round; the claims about GitHub behaviour below come from reviewer knowledge, plus the workflow-ref fact that SPR checked against the primary source. They are labelled where they matter.

The architecture is strong. It keeps every `[user]` and `[agreed]` decision I checked: implementation-only clocks; the origin's pause during an expansion; an expansion's fresh clock and its lack of any allowance of its own; agent sign-off; `pivot` as the only human-only command; advisory dogfooding; git as the authority; and REST before GraphQL. Unresolved owner choices are labelled as such rather than promoted to policy. The cross-provider read found five contract-level gaps that earlier rounds missed. Each one would mislead a section designer or make a stated contract impossible to satisfy, and each fix is a sentence or two in the FUR. None of them requires reversing an owner decision.

1. Version-bound acceptance conflicts with machine-owned frontmatter inside the accepted file (R1-F001).
2. The interim review procedure, which the architecture says to follow until M4, depends on a planning checkout that M1 retires and that guard layers 3 and 5 forbid (R1-F002).
3. Delivery evidence is required before Done, but neither provider role is responsible for supplying it, "delivered version" has no definition under squash or rebase merges, and a core-only or offline install has no path to it (R1-F003).
4. No rule says which copy of `.aitm.toml` governs a transition, so a story branch can relax the policy applied to its own story (R1-F004).
5. The Pages build has the same workflow-ref constraint as the every-push audit, but the FUR only flags the audit (R1-F005).

All five required changes are small additions to the FUR text. None reverses a `[user]` or `[agreed]` decision, and none needs a new owner decision. R1-F003 option (3) and R1-F004 leave the choice of mechanism to the core design. This review does not accept or revise the core design or master plan, and it does not resolve the open items listed on FUR lines 211–218.

## Findings

### R1-F001 — Content-bound acceptance is broken by machine-owned frontmatter in the accepted file

**Where:** FUR lines 103 and 131–132. Line 103 says machine-owned frontmatter is a generated view. Lines 131–132 say acceptance names the reviewed content version and that "a later change to design or plan bytes needs renewed acceptance".

**Problem:** The decision record (`[user]`, draft line 96) requires every story data file to carry frontmatter that includes last update and last working branch/worktree. The core design (line 184) regenerates that frontmatter on every sync. A design or plan document's bytes therefore change during routine work after acceptance, with no change to what the author wrote. Read literally, line 132 then invalidates acceptance on every sync: `design-accepted` and `plan-accepted` stop holding, and the story either cannot leave Backlog or Plan or has to be re-reviewed for metadata noise. That is a tool-caused block, the outcome Goal 1 and the first anti-goal rule out. The FUR shows the problem itself: its frontmatter carries `updated`, `last-branch: review/1-architecture-sar` and `status: draft (awaiting review)`. Moving `status` to accepted after this review would, under the stated rule, require renewed acceptance of the very document just accepted.

**Why it is architecture-level:** It involves two architecture contracts (generated-view ownership and version-bound acceptance) plus a `[user]` decision. The core, peer-review and GitHub section designs all inherit it, and each would otherwise pick its own canonicalisation.

**Required change:** State what "reviewed content version" covers. Either (a) it is the authored content only, excluding machine-owned metadata, with the core and peer-review designs obliged to define one canonical digest that both the review record and `core.doc.accepted` use; or (b) machine-owned metadata for reviewed documents lives outside the reviewed file (for example in `story.md` or a sidecar), so the reviewed bytes are author-owned only. Either way, add one sentence saying that regenerating machine-owned metadata never invalidates acceptance, while any change to authored content does. The choice between (a) and (b) can go to the core design, but the FUR must name the obligation and add it to the core-reconciliation paragraph (line 220).

### R1-F002 — The interim review procedure conflicts with the M1 guard layers during M1–M4

**Where:** FUR line 134 (follow the interim procedure "until the M4 refactor ships") and lines 88–90 (layer 3: git hooks refuse commits on a checked-out planning branch; layer 5: core refuses writes while planning is checked out anywhere). Master plan M1 retires the `aitm-planning` checkout.

**Problem:** Step 4 of the linked interim procedure commits the imported FUR and collateral "into the planning checkout … with a fast-forward push", and step 1 pulls in that checkout. From M1 onward the checkout no longer exists, the layer-3 hooks refuse commits on it, and the layer-5 core checks refuse every aitm write while it exists. The architecture still tells reviewers to follow the procedure until M4, so for the whole M1–M4 window (M2 and M3 reviews included) the architecture asks for a procedure its own guards forbid. Step 2 also creates review branches from the planning tip in their own worktree. Depending on how the harness deny rules in layer 4 are written, that worktree creation may be denied too.

**Why it is architecture-level:** The FUR adopts the interim procedure by reference as the review contract for that period. The guard layers and the M1 retirement are also architecture contracts.

**Required change:** Add a sentence to the Review contract saying that once the core's plumbing writer replaces the planning checkout (M1), the interim import goes through the core writer rather than a planning checkout. Either name it as an M1 obligation (a core command that imports a review folder plus the revised FUR into a story path through compare-and-swap, without touching any other path), or say plainly that the procedure must be revised before M1 ships. Also state that a review worktree branched from planning is not "the planning branch checked out", so layers 3–5 do not refuse it, or else require the harness design to allow it explicitly.

### R1-F003 — Delivery evidence has no owning provider role, no squash-safe definition and no core-only path

**Where:** FUR lines 119 ("Review passed for the delivered version"), 126 ("authoritative delivery evidence supplied through the relevant provider or deliverable mechanism"), 161–162 (provider responsibilities), 164 ("installing only core must still support local setup") and 168 (the local *backlog* provider exists for tests and offline use).

**Problem:** Done on the delivered path requires delivery evidence, but:

- Neither provider role is responsible for delivery or merge status. The git-host list ("PRs, CI status, …") can be read that way, but it does not say so. A backlog-side reading ("issue closed") is just as plausible and would be wrong.
- "Delivered version" has no definition under squash or rebase merges, which the decision record names as a design concern ("the record survives squash merges"). The commit that lands on the default branch has a different SHA, and often a different tree, from the reviewed head. Read literally, "review passed for the delivered version" cannot be met by the trunk commit unless the delivered version is defined as the reviewed head that the provider reports as merged.
- With only `aitm-core` installed (`githost = "none"`, local backlog provider), nothing in the architecture can supply delivery evidence for a leaf story. A story delivered by a local merge then cannot reach Done. That contradicts Goal 1, and also the core design's acceptance criterion of a core-only walk from backlog to done.

**Why it is architecture-level:** It is the provider-role split and the definition of a lifecycle exit condition. The FUR already reserves "provider mechanics and merge strategy" for section design, which is fine. Who supplies the evidence, and what it must identify, is not a mechanics question.

**Required change:** (1) Add delivery or merge status of a reviewed head to the git-host provider's responsibilities. (2) Define "delivered version" as the reviewed head (or deliverable) that the delivery mechanism reports as landed, independent of merge strategy. (3) Require a provider-independent delivery evidence path for core-only and offline use; local git ancestry is one candidate, though it cannot see through squash merges, so the core design must pick a mechanism. Alternatively, state explicitly that a core-only install cannot complete the delivered path, and reconcile that with Goal 1. Add this to the core-reconciliation paragraph.

### R1-F004 — No authoritative source for `.aitm.toml`; a story branch can relax its own policy

**Where:** FUR lines 83, 155 and 191 (`.aitm.toml` lives on the default branch) and lines 146–151 (enforcement modes; "advisory mode relaxes workflow policy, not ownership").

**Problem:** Story branches are cut from trunk and so carry their own copy of `.aitm.toml`. The architecture does not say which copy the core reads when it evaluates a transition: the working tree's, the story branch's, or the configured default branch's committed tip. If it is the worktree copy, an agent can edit its own story branch to switch `enforce` to `advisory`, raise `leaf_agent_hours`, disable an extension's guards, or change the configured test command (core design `[test] command`), and that edited policy then governs its own story's guards and trip checks before any review sees the change. The architecture already guards against this class of self-serving relabelling for pivots (line 143). The same reasoning applies to policy configuration, and Goal 2 ("planning failures surface when detected") depends on it.

**Why it is architecture-level:** It decides where the authority for workflow policy comes from, for every section. Getting it wrong quietly defeats enforce mode in consumer repos, and the enforce→advisory checkpoint depends on enforce mode being real.

**Required change:** State that workflow policy (enforcement mode, limits, enabled extensions, the test command) comes from the configured default branch's committed `.aitm.toml`, read locally from the fetched default-branch ref. Changes made on a story branch take effect only once they are delivered to the default branch. Add that each transition event records the effective policy it was evaluated under (the core already records `mode`). Bootstrap before the first `.aitm.toml` lands, and the exact ref, can stay core-design details.

### R1-F005 — The Pages build shares the workflow-ref constraint the FUR flags only for the audit

**Where:** FUR lines 93 (GitHub section obligation, scoped to the every-push audit), 187 (`aitm-viewer` ships a "Pages workflow") and 203 ("a GitHub Pages build reads generated JSON from planning"). Decision record line 115 says "A GitHub Action builds JSON from `planning` for Pages."

**Problem:** The constraint the FUR records for the audit also applies to the Pages build. A `push`-triggered workflow is read from the pushed ref, so a workflow that lives only on trunk is not triggered by pushes to the isolated, `.aitm/`-only planning branch, and the architecture forbids adding workflow code to planning. As far as I know (not verified this round), GitHub Pages "deploy from a branch" serves only the branch root or `/docs`, and planning holds only `.aitm/`, so that route is closed too unless something is added to planning's root. The viewer design will therefore need a scheduled, dispatched or trunk-triggered build, or a provider-side dispatch after aitm pushes. At present the FUR flags this only for the audit, so a viewer designer reading line 203 could reasonably assume a planning-push trigger.

**Why it is architecture-level:** The FUR already records this exact constraint as an architecture-level GitHub obligation and as an open item. Leaving out the second consumer makes the obligation look narrower than it is.

**Required change:** Extend the GitHub section obligation (line 93), or add a sentence in the viewer paragraph (line 203), so that the Pages build is subject to the same workflow-ref constraint. State that a non-push trigger is acceptable for the viewer because snapshot freshness is already disclosed (line 203). Keep the restriction on substituting polling scoped to the audit, as it is now. Do not resolve the audit question here.

## Required changes

1. **R1-F001:** Define the "reviewed content version" so that regenerated machine-owned metadata does not invalidate acceptance and authored-content changes do. Use either a canonical authored-content digest or reviewed files that carry no machine-owned metadata. Add this to the core-reconciliation obligations.
2. **R1-F002:** State how the interim import works once M1 retires the planning checkout (through the core writer, as an M1 obligation, or by revising the procedure before M1). State whether a review worktree branched from planning is exempt from guard layers 3–5.
3. **R1-F003:** Make delivery or merge status of a reviewed head a git-host provider responsibility; define "delivered version" independently of merge strategy; and either provide a core-only delivery path or explicitly reconcile its absence with Goal 1.
4. **R1-F004:** State that workflow policy comes from the default branch's committed `.aitm.toml` (story-branch edits take effect only after delivery), and that transition events record the effective policy.
5. **R1-F005:** Extend the workflow-ref constraint to the Pages build, and say a non-push trigger is acceptable there.

## Optional suggestions

1. Line 104: "Its current multiple-writer/event-union builder call is not an exception to this agreed ownership contract" can be read in two opposite ways: "it is consistent with the contract" or "it is not granted an exception". Suggested wording: "The core design's current multiple-writer/event-union proposal is not accepted as an exception; the later core review must either show it satisfies single-owner ordering through the append API or replace it."
2. Line 80 says planning holds "`.aitm/` story data only", but the core design's pre-push invariant also permits a root `README.md`. Either add that to the core-reconciliation paragraph or allow it here, so the hooks and the architecture agree.
3. Out of scope for the FUR, noted for the record: the Review contract says all levels use common response formats, but the SAR/SPR records in this story use `aitm.review-response/v0` while this XPR uses `ai-peer-review.response/v1`. The interim-procedure import, or the M4 work, should normalise or map these, so that the "one format" goal behind SAR holds for this story's own record.

## Decision

revisions-requested
