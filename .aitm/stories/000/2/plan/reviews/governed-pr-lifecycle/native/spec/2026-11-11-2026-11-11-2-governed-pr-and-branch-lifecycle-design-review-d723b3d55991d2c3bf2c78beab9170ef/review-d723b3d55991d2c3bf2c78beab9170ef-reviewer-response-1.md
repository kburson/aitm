<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-d723b3d55991d2c3bf2c78beab9170ef"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md"
artifact_commit: "71613ea0a2035e5e1e0ac2be6cfd70cc63b84487"
artifact_blob: "4cfedfcbfbb7815aa2c5ddfa8aae80881b00e526"
artifact_digest: "sha256:71dae425e57507082796dc4e8f475eadb4201de4eb0ead5d74c64942e6be419c"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4"
  identity_source: "runtime"
started_at: "2026-11-11T15:04:43.089Z"
submitted_at: "2026-11-11T15:08:18.729Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the round 1 independent XPR spec-phase review of `.aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` at commit `71613ea0a2035e5e1e0ac2be6cfd70cc63b84487`, with artifact digest `sha256:71dae425e57507082796dc4e8f475eadb4201de4eb0ead5d74c64942e6be419c` taken from this response's protected frontmatter. The scope is planning review only. It covers owner intent, accepted Core contracts, feasible GitHub boundaries, recovery and failure cases, host-qualification obligations and the Core/provider boundary. This review grants no hosted test, protection change, implementation or #159 pickup authority.

### Full-file read record

- **Tool and ranges.** I used Read in contiguous chunks of at most 60 lines and read lines 1–60 and 61–108. The request at offset 121 reported that the file has 108 lines, which confirms line 108 is EOF.
- **Truncation.** No output was truncated, so no recovery was needed.
- **Hashing.** Shell hashing was not available to this reviewer (Bash is limited to the package join/submit commands). The digest above therefore comes from the protected frontmatter and was not computed independently. It matches the design digest recorded in `spr-reviewer-round-3.md`.

### Related material read for handoff validation

I read each of the following to check handoffs. None of them is under review.

- **#2 plan.** `.aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` in full: lines 1–60, 61–120, 121–180, 181–240, 241–300 and 301–339. EOF is line 339 and nothing was truncated.
- **Core design.**
  - `core-design.md` §Providers, lines 564–623.
  - §Verification, delivery and sign-off and §Resident actions, lines 477–526.
- **Core plan.** The C76 leaf in `plan/core-implementation-plan.md` (lines 1195–1206) and the leaf-order rows 201–208.
- **#133 amendment.** `001/133/design/2026-11-11-133-merge-only-stop-the-line-design.md` in full (lines 1–60 and 61–113). §Scope, §One shared flag, §Hold, repair, and reopen and §Pending trunk PRs are all relevant.
- **#158 plan.** `001/158/plan/2026-11-11-158-merge-only-qualification.md` in full (lines 1–60 and 61–84).
- **Earlier reviews.** For context only, the prior SPR acceptance (`spr-reviewer-round-3.md`). Every finding below is my own, assessed independently.

### Independently verified (no finding)

- **Core/provider boundary.** Core owns policy, binding, intent, typed results and discovery. The git-host extension owns provider effects, and the runtime/service owns credentials and isolation. This matches core-design §Providers, which places endpoint details in extensions and requires replay obligations, dispatch claims and proof of absence.
- **Provisioning recovery.** Design lines 20–28 reuse Core graduation reservation and dispatch claims and gate branch and PR writes on verified shared publication. They also refuse adoption without positive ownership evidence. This is consistent with core-design lines 590–598.
- **#133 handoff.**
  - The live flag is read at the ready/merge boundary and cached refs are not used.
  - Only the nominated repair may leave draft while trunk is held.
  - An already-ready ordinary PR stays merge-blocked.
  - Retarget loses any old allowance.
  - Non-default targets are outside the trunk hold.
  
  These rules match #133 lines 52–66 and 108–112.
- **#158 handoff.** Default-branch merge needs the #158 flag/head/base/tree boundary. Managed readiness is a separate capability, and a #158 pass alone does not activate managed repair. This is consistent with #158 lines 31–54 and 76–83, where the host transaction has no PR ID and the merge path is refused if PR association is unprovable.
- **Integration delivery.**
  - The integration owner is an ordinary story with its own attempt, Test, Review and C41 admission.
  - The composed-source alternative to C76 is bounded to that story.
  - Plan lines 66–86 do not create an empty tagged commit, which is consistent with the C76 test-first clause rejecting empty or merge-only tagged changes.
- **Isolation honesty.** If isolation cannot be qualified, managed provider operations are reported unsupported. The plan never treats a CLI-only installation as an enforcement boundary.

The findings below are gaps this review found that are not closed by the design text.

## Findings

### R1-F001 — High — No base resolution for stories delivering to the default branch

**Location:** design lines 29–30 and 42, plan lines 35–36 and 46–47, design line 102.

**Problem.** The design says to "use the declared feature or epic parent as the child PR base" and that "a missing parent is an unavailable binding". The plan adds that "a missing or unbound parent blocks provisioning" and rejects "implicit default-target fallback". Plan line 88 says a pure aggregate epic has no branch.

**Effect.** Read together, these rules leave no way to provision an ordinary branch-backed story whose Backlog parent is a pure aggregate epic, or one that has no feature/epic parent. That is the ordinary trunk-bound story the #133 amendment governs (#133 lines 12–23: "An ordinary PR starts in draft … TIA against its actual target"). Its Backlog parent has no working ref, and the design forbids inferring trunk. The only explicit default-target route in the design is the integration owner of a top-level epic.

**Consequence.** The primary managed workflow, a story PR into trunk, is either unprovisionable or depends on an unstated fallback. Either outcome contradicts the Outcome section ("each branch-backed story gets … draft PR") and the #133/#158 trunk flows.

**Closure criteria.** The design states that every managed working branch carries an explicitly declared literal delivery target, separate from Backlog parentage. It must state:
- (a) when that target is derived from a branch-backed feature/epic parent;
- (b) how a story under a pure aggregate epic, or with no parent, explicitly declares the protected default branch or another literal target at graduation or provisioning, without implicit fallback;
- (c) that "missing parent" means a missing or unbound declared target.

Acceptance and the plan's proof matrix must include provisioning, parent selection and denial cases for a trunk-targeted ordinary story under a pure aggregate epic.

### R1-F002 — Medium — No managed lifecycle after successful delivery, and GitHub's implicit retarget/close routes are unaccounted for

**Location:** design lines 8, 51–58 and 99–101, plan lines 257–280 and 196–220.

**Problem.** Retirement is specified only for abandonment and scrap. The design does not say what happens to a story's or integration story's working ref, linked PR and owned worktree after verified delivery: whether they are retained or retired, by which claim, and in what order relative to dependents.

**GitHub boundary.** GitHub has host-initiated routes that bypass broker admission:
- When a merged PR's head branch is deleted (manually or through the repository's automatic head-branch deletion setting), GitHub automatically retargets open PRs based on that branch to the merged PR's base.
- Deleting an unmerged base branch closes its dependent PRs.

**Consequence.** After an epic integration branch delivers upstream and is retired, an open component PR could be moved to `trunk` (or to a non-default upstream) by the host. That would happen without the verified-draft and fresh-admission rule that design line 83 and plan lines 211–216 require. The #158 merge gate still protects trunk mutation, but the governed retarget invariant and the PR's recorded target would silently diverge.

**Closure criteria.**
- The design defines post-delivery disposition of the working ref, PR and worktree for ordinary and integration stories, including whether retirement waits for every dependent PR to be terminal.
- It requires qualification, or explicit control, of host-initiated retarget and close behavior and of the repository's automatic head-branch deletion setting.
- It states that the broker reconciles any observed host-side base change as a retarget that invalidates admission and CI.

The plan's proof matrix must include a dependent-PR case during retirement of a delivered parent ref.

### R1-F003 — Medium — No governed read path for CI results and review feedback under managed isolation

**Location:** design lines 47–50, 72–75 and 103–105, and the plan agent-interface table at lines 21–29.

**Problem.** Managed mode removes all direct provider tool and network routes from the agent, including anonymous API reads (design line 72, plan lines 179–181 and 332). The governed operation families cover create, pickup, push/refresh, ready, merge, abandon and discover/inspect. They do not name any observation operation for:
- check-run and CI results, or failure logs;
- PR review comments and requested changes;
- review state.

The #133 amendment relies on agents "receiving CI results" while background work continues (#133 lines 13–15), and normal rework needs reviewer feedback. "Supported observation remain available" (design line 75) is stated only for the case where isolation is unsupported.

**Consequence.** Under qualified managed isolation, an agent cannot read why its PR failed CI or what the reviewer asked for. The workflow then either stalls or pushes implementers to request a direct-access exception, which would undermine the isolation guarantee.

**Closure criteria.**
- The design names the governed, read-only observation operations available in managed mode: at least PR state, check results with logs or artifacts, and review threads/state. Each is bound to the caller's own incarnation and authorized targets, with typed results and catalog entries.
- Alternatively, the design explicitly states another qualified read route and its isolation argument.

Acceptance must show that a managed agent can obtain CI and review feedback for its own PR through that route and is denied the same data for an unrelated resource where policy requires it.

### R1-F004 — Low — The bootstrap commit has no defined identity or accounting in source and delivery proofs

**Location:** design lines 42–46 and 24–25, plan lines 93–100, 112–113, 66–86 and 331.

**Context.** GitHub normally refuses to create a PR when head and base point to the same commit ("No commits between"), so the content-free bootstrap commit is the likely qualified route, not an edge case.

**Problem.** The design records "initial base" and the working ref but not the bootstrap commit as a typed provisioning artifact. It also does not state how that commit relates to:
- (a) the attempt's pinned baseline for C76, which counts commits on the attempt branch after the baseline;
- (b) the composed-source receipt's rule that a candidate must be "fully mapped" with no unexplained history, since each child's bootstrap and the integration branch's own bootstrap enter the integration history;
- (c) Core delivery mapping;
- (d) the frozen "initial source OID" read-set.

**Consequence.** Implementers may resolve this inconsistently, so the guard rejects or misattributes empty provisioning commits, or the receipt silently ignores commits it should account for.

**Closure criteria.** The design or plan states:
- the bootstrap commit's recorded identity: OID, tree equal to the parent tree, author/service role and incarnation;
- that the attempt baseline is pinned at or after it;
- that the composed-source mapping and delivery verification treat a recorded bootstrap commit as an explained, content-free provisioning commit and treat any other empty or unrecorded commit as unexplained.

The deterministic guard fixture covers both the recorded-bootstrap case and the unrecorded-empty-commit case.

### R1-F005 — Low — The proof does not cover caller-identity binding against other stories' resources

**Location:** design lines 62–67 and 102, plan lines 171–176 and 332.

**Problem.** The service "authenticates the caller" and binds the operation to the current resource incarnation. However, the design does not state where the caller's managed-session identity comes from. It needs to come from runtime-attested identity rather than an agent-readable token or a caller-supplied argument. The proof row tests unauthorized repository, ref, action and stale generation, but not a valid managed session acting on another story's live incarnation in the same repository.

**Closure criteria.**
- The design states that broker caller identity is runtime-attested and is not transferable through the agent workspace.
- The proof matrix includes the denial of a current managed session that tries to push, ready, retarget, merge or abandon another story's current incarnation.

## Required changes

1. **R1-F001:** Define explicit literal-target declaration for stories without a branch-backed parent, including trunk-targeted stories under pure aggregate epics. Update acceptance and the proof matrix to match.
2. **R1-F002:** Define post-delivery disposition of the ref, PR and worktree, and address GitHub's host-initiated retarget and close behavior and the automatic head-branch deletion setting. Add a dependent-PR retirement case to the proof matrix.
3. **R1-F003:** Name governed read-only observation operations for CI results and logs, PR state and review feedback in managed mode, or state a qualified alternative route. Add acceptance coverage.
4. **R1-F004:** Record the bootstrap commit as a typed provisioning artifact and define how C76, the composed-source receipt, delivery mapping and the initial-source read-set treat it. Extend the guard fixture.
5. **R1-F005:** State that broker caller identity is runtime-attested, and add a cross-story impersonation denial to the isolation proof.

## Optional suggestions

1. Design line 88 says "Require exact parent delivery evidence on every managed merge". The phrase "parent delivery evidence" is ambiguous: it could mean evidence required by the parent's policy, or evidence of the parent's own delivery. Consider "apply the declared target's exact delivery policy (C39–C41) on every managed merge".
2. Design Acceptance (lines 99–105) omits two items the plan proves: the composed-source integration guard and the verified scrap source-retention receipt. Consider naming both so that design acceptance matches plan lines 330 and 335.
3. Design line 72's requirement to block anonymous public-API reads exceeds what mutation safety needs. If its purpose is to stop direct state gathering that bypasses governed observation, consider saying so, so qualification knows which read routes must be denied and which may be offered through the broker (see R1-F003).

## Decision

revisions-requested
