<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-095b15003bea70559dd3ce3bb285292a"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_commit: "63c7e85d66153db6dc03e5aa41fc8d8191845632"
artifact_blob: "a21256d003ec73b3e278038c42d4051171525b80"
artifact_digest: "sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01"
  identity_source: "runtime"
started_at: "2026-11-09T05:57:59.810Z"
submitted_at: "2026-11-09T06:02:03.195Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Revisions requested. This is an independent cross-provider (XPR) review, by an Anthropic model, of the core design. Its SAR and SPR rounds ran on OpenAI models. The reviewed FUR is `.aitm/stories/000/2/design/core-design.md` at the digest in the frontmatter above, the same digest SPR round 3 accepted.

Reading order: the complete FUR; the story draft (`../draft.md`); the relevant parts of the parent architecture (`../../1/design/architecture.md`), mainly the lifecycle table, the trip and mode rules, and line 111, which hands kind-specific guards to this design; and the final SPR reviewer response. I read that response only after forming my own view, so that I would not re-raise points already settled. I did not re-read the SAR or SPR author responses or patches. I made no network calls. No finding below depends on external facts.

The design is thorough and internally careful. It keeps the settled owner decisions I checked: an implementation-only four-hour clock per attempt; one expansion per attempt with no nested expansion; the origin pausing while its expansion is unresolved; agent sign-off with no routine human gate; `pivot` as the only human-only path; git as the authority with a single writer per surface; and core-only operation with no model calls. It keeps open the questions it says are open: the expansion-completion interpretation, the second-trip cap, the review-depth matrix and the hosted every-push audit. The concurrency, publication, repair and timing contracts are specified well past the level earlier designs reached, and I found no contradiction in them.

The cross-provider read found four builder-facing gaps. Each one either leaves a required M1 walk step unimplementable as specified, or leaves a contract the builder would have to invent. None reverses an owner decision or settles an open question. Each fix is a sentence, a short paragraph or a small table.

1. The authoritative `aitm test` lane, which the M1 walk and the Test exit guard depend on, has no specified mechanism, input-manifest scope or declaration route for untracked inputs (R1-F001).
2. The design delegates kind-specific guards for spikes but does not specify them. The guard table, read as written, blocks a spike at Develop and Test exit (R1-F002).
3. Committed configuration is not split between settings that take effect from the pinned default-branch tip and anchor fields that need `init --reconfigure`, so clones can disagree about effective policy (R1-F003).
4. `init` adds an unanchored `.aitm/` pattern to `.gitignore`. That pattern also ignores every nested `.aitm/` directory, including the store fixtures that the Migration acceptance row requires the aitm repo to carry (R1-F004).

## Findings

### R1-F001 — The authoritative test lane and its input manifest are unspecified, but the M1 walk depends on them

**Where:** FUR line 408 (`test` captures "a complete manifest of relevant tracked and untracked inputs"; it refuses "an unaccounted test-input file"; authoritative verification runs against "a captured stable input snapshot, or an execution lane with equivalent evidence"; "a lane that cannot establish stable actual inputs may run diagnostically but cannot issue an authoritative pass"). Also lines 107–108 (`[test] command` is the only test configuration), line 368 (Test exit `test-passing`), line 551 (core-only walk: "run the configured test over the recorded clean input") and line 597 (acceptance: "an unsupported execution lane remains diagnostic").

**Problem:** The design sets a strong requirement: inputs cannot change during the run, and comparing hashes before and after is explicitly not enough. It never says which lane M1 ships that meets that requirement, so the builder is left with three unanswered questions:

- **Mechanism.** Running in the user's story worktree cannot meet the stated requirement, because another writer in that worktree can change the bytes the subprocess reads. The obvious lane is a private materialization of the captured tree, for example `git archive` of the recorded head into a core-owned temporary directory plus copies of the declared extras. The FUR neither names nor requires it. Line 308 says "the core never … creates/removes a worktree", which a builder could reasonably read as ruling out `git worktree add --detach` for a scratch lane, even though that sentence concerns story worktrees.
- **Manifest scope.** "Relevant" untracked inputs has no definition. The configured example command (`uv run pytest`) reads ignored, mutable environment state such as `.venv/`, tool caches and lockfile resolution, and may reach the network. The design does not say whether ignored environment directories are inputs, are excluded and recorded as environment, or are rebuilt in the lane. Each choice gives different receipts and a different meaning for "clean".
- **Declaration route.** The text requires "explicitly accounted untracked inputs", but no config key, CLI flag or schema lets anyone declare them. `[test]` has only `command`.

If no lane is specified, a builder who reads the immutability rule literally ships only a diagnostic lane. Test exit can then never pass in enforce mode, and the core-only walk on line 551 cannot reach delivered Done. A builder who reads it loosely runs in place, and the receipts quietly fail to meet line 408. Either outcome defeats the Test guard's purpose. Line 605 does not leave this choice to the builder.

**Required change:** State the M1 authoritative lane, and the manifest and environment contract it uses. For example: "M1's authoritative lane materializes the captured source tree and the declared extra inputs into a core-owned private temporary directory outside every worktree (not a registered Git worktree), and runs the command there. Ignored environment state (the virtualenv, tool caches) is either rebuilt in the lane or recorded as declared environment with its identity/digest, never treated as source input." Add a declaration route for extra untracked inputs, such as `[test] inputs = [...]` globs relative to the repo root, recorded with the effective policy. Clarify that the line 308 prohibition concerns story worktrees and does not prevent the lane. If the design instead makes in-place running authoritative in some bounded form, say how that form meets the immutability sentence. Otherwise remove the sentence.

### R1-F002 — Kind-specific guards for spikes are delegated to this design but not specified

**Where:** Architecture line 111 ("Spikes and other kinds have appropriate deliverables. The core design proposes detailed kind-specific guards"). FUR line 344 (the single leaf chain), line 346 ("The kind-specific edge table is checked before policy guards"), lines 356–369 ("Core guards for executable leaves"), line 384 (spike paragraph) and line 385 (epic paragraph).

**Problem:** The guard table gives one guard set for "executable leaves". A spike is a leaf on the same chain, and the table's Develop exit (`story-commits`, "story-tagged implementation commits") and Test exit (`test-passing`, a tool-produced test receipt) cannot pass for it. Line 384 says only that a spike "uses an immutable registered deliverable instead of implementation commits and test receipts" and "follows the leaf planning/review flow and its attempt clock". That leaves these questions open:

- whether a spike passes through Test, and if so what its Test exit guard checks (a registered deliverable version? nothing?);
- whether Plan exit `jit-current / implementation-bound` applies to a spike, and whether a spike has an implementation branch or binding at all, given that `bind --implementation` "selects or creates an isolated story branch from the pinned code baseline";
- what Develop exit checks for a spike (a deliverable registered for the current attempt?);
- what "its attempt clock" covers for a spike, given that the clock is defined as "develop entry → review passed".

Line 385 lists the epic exemptions explicitly ("no implementation branch, JIT guard, clock, commits, test receipt, PR…"). The spike gets no matching list. The "kind-specific edge table" on line 346 is referred to as if it exists, but appears only as prose. In enforce mode, a builder following the table as written refuses every spike at Develop exit. In advisory mode, every spike reaches only `done/unverified`.

**Required change:** Add a short kind × slot matrix, or per-kind rows, covering story/defect, spike and epic for the Plan exit, Develop entry/exit, Test exit and Review exit slots. For each kind, name the guard that replaces or drops each leaf guard (for example, spike Develop exit: "a registered deliverable exists for the current attempt"; spike Test exit: "skipped, or a deliverable-validation receipt"), and state whether JIT and implementation binding apply to spikes. Alternatively, state explicitly which guard decisions are left to the builder and add them to "Left to the builder". The architecture assigned this decision to this design, so leaving it implicit means it is not reviewed anywhere.

### R1-F003 — Committed configuration is not split into tip-effective settings and reconfigure-only anchor fields

**Where:** FUR line 113 ("`init --reconfigure` is the explicit adoption route for later routing/policy changes"), line 115 ("a delivered config change must be checked against the current anchor and adopted through `init --reconfigure`"), line 121 (each command refreshes the default ref, "pins the policy commit", and "Publication rechecks current committed policy"), line 125 (trust anchor fields), line 394 (review policy) and line 588 (acceptance: "Story-edited mode, command or routing cannot change effective policy").

**Problem:** These sentences support two incompatible models:

- **(a) Tip-effective.** Any change to `.aitm.toml` merged on the anchored default branch takes effect at the next command, because each command pins the current policy commit (line 121).
- **(b) Adoption-gated.** Policy changes take effect only after a clone runs `init --reconfigure`, which records its adoption in clone-local `installation.json` (lines 113 and 115 say "routing/policy").

Under (b), two clones of the same repository evaluate different effective policies (enforce versus advisory, different limits, different test commands, different review policy) until each one reconfigures. That contradicts "committed effective policy" as the single authority, and the "Publication rechecks current committed policy" rule. Under (a), changing a trust-anchor or routing field (store UUID, genesis, planning repo/ref, default-branch ref) by a trunk merge alone would retarget the store, which lines 115 and 125 forbid. The design clearly intends a mix of the two, but never says which keys belong to which class. The review-policy definition is the hardest case: line 113 groups it with the bootstrap and trust fields, while lines 394–396 describe re-evaluating it whenever policy changes. A builder therefore cannot tell whether merging a review-policy change on trunk changes `design-accepted` results at the next command.

**Required change:** Add a short classification to the configuration section:

- **Anchor/routing fields:** store UUID, genesis or legacy root, planning remote/ref, default-branch routing and the allocation authority. A trunk change to any of these is detected and refused as an integrity or adoption-pending condition until `init --reconfigure` validates both the old anchor and the proposed one.
- **Policy settings:** enforcement mode, limits, enabled extensions, the test command and inputs, and the review-policy definition. These take effect from the pinned validated default-branch commit at the next command, with no per-clone adoption, and every operation records them.

If the review-policy definition belongs in the first class, say so and explain how clones stay consistent. Adjust the "routing/policy" wording on lines 113 and 115 to match.

### R1-F004 — The unanchored `.aitm/` gitignore pattern also hides nested store fixtures in the code repository

**Where:** FUR line 136 ("adds `.aitm/` to `.gitignore`"). The Migration acceptance row (line 602) and line 580 ("Tests use copies of the actual hand-built #1/#2 fixtures"). Also lines 304 and 318, which put core-managed worktree state only at `<worktree>/.aitm/`.

**Problem:** In `.gitignore`, a pattern with no leading slash, such as `.aitm/`, matches a directory with that name at any depth. aitm develops itself in its own repository, and its test suite has to carry real store-layout fixtures: copies of the hand-built #1/#2 stores, migration inputs, and validator vectors for "Reject outside-path…" and repair. The natural layout for these fixtures is `tests/fixtures/<case>/.aitm/...`, and the unanchored pattern silently excludes all of it. `git add` then skips those files, CI never sees them, and the acceptance-required fixtures go missing without any error. Any consumer repository with nested `.aitm/` content (vendored examples, documentation samples) hits the same problem. The core only ever needs the worktree-root `.aitm/` ignored.

**Required change:** Make `init` add the root-anchored pattern `/.aitm/` and state that only the worktree-root store directory is ignored. When `init` detects an existing unanchored `.aitm/` entry, `doctor` (or `init`) should report it.

## Required changes

1. **R1-F001:** Specify M1's authoritative test lane (mechanism and location), the input-manifest scope including how ignored environment state is treated, and a declaration route for explicitly accounted untracked inputs. Clarify that the line 308 worktree prohibition does not cover the lane.
2. **R1-F002:** Add a kind × slot guard matrix, or explicit per-kind substitutions, for spikes alongside story/defect and epic. Cover Test, Develop exit, JIT/implementation binding and the spike clock. Alternatively, move the undecided cells into "Left to the builder".
3. **R1-F003:** Classify committed configuration keys into anchor/routing fields (which need `init --reconfigure`) and policy settings (effective from the pinned default-branch tip, the same for all clones). Place the review-policy definition explicitly, and align the "routing/policy" wording.
4. **R1-F004:** Have `init` write the root-anchored `/.aitm/` gitignore pattern, and have `doctor` or `init` report an existing unanchored entry.

## Optional suggestions

1. Line 97: rename `expansions_per_story` to `expansions_per_attempt`. Its own comment says "per attempt", and the rest of the design consistently scopes the allowance to an attempt. The current name invites a per-story reading that would wrongly deny a fresh attempt its allowance after a trip.
2. Line 233: the `core.state.changed` "Recorded by" column lists only `promote`, `demote` and `abandon`. State changes also come from `signoff` (Done), `reopen`, a confirmed trip's demotion to Plan, `pivot`, design rework, and the atomic expansion and trip transactions. Listing them, or saying "every state-changing operation", stops a builder emitting a different event type from those paths, which would break `events.fold`.
3. Line 272: `story.md` frontmatter carries `last-worktree`. That is a clone-local absolute path committed to the shared planning branch, so it exposes local filesystem layout to every clone and the hosted viewer, and differs between clones for the same logical binding. Consider recording a repo-relative label or a worktree ID instead, keeping absolute paths in clone-local `.state`.
4. Line 167 and line 176: say what happens to the draft's own `drafts/<YYYY-MM>/…/` directory when it is discarded (retained in place, moved, or removed by the discard operation), and confirm that the discarded record is keyed by the stable entity ID as well as the stamp and slug.

## Decision

revisions-requested
