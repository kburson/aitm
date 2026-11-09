<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-4fd804fb61330759842fa8d75f4dedd9"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_commit: "618703dd2dd54871e66ad58e0b3c8fb5e5164cb0"
artifact_blob: "d68b6e037fe7d22dad8b4905d97b2cdf11125d76"
artifact_digest: "sha256:1f8fc7179cc17141598e985d9e8136c8ead8c44156cbbff27bad8f03d86192dd"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:3559f054cec2522b1120f6a4e60f8b5b8c15950a5c65a28cc3236dd95ed4de32"
  identity_source: "runtime"
started_at: "2026-11-09T07:29:06.774Z"
submitted_at: "2026-11-09T07:33:35.731Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005","R1-F006","R1-F007","R1-F008","R1-F009","R1-F010","R1-F011","R1-F012"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent native XPR of the full current `core-implementation-plan.md` (1215 lines, artifact digest as in frontmatter), checked against the accepted core design (`core-design.md`, especially Package layout, Configuration, `aitm init`, CLI, Performance budgets, Migration and Acceptance).

Mechanical checks performed and passed:

- Estimate arithmetic: the 63 table rows sum to exactly 199 h; every leaf is within 2.5–4 h; table and section estimates agree.
- Topological order: every row's Depends on keys appear earlier in the table.
- Shared-file serialization: I enumerated every touched path that appears in more than one leaf allowlist (`services.py`, `store/backend.py`, `store/sync.py`, `store/validation.py`, `store/gate.py`, `cli/dispatch.py`, `cli/planning.py`, `cli/setup.py`, `setup/init.py`, `setup/doctor.py`, `cli/stories.py`, `cli/plan.py`, `cli/deliver.py`, `cli/evidence.py`, `cli/bind.py`, `cli/migrate.py`, `cli/sync.py`, `cli/app.py`, `reviews/activation.py`, `outcomes.py`, `machine/transitions.py`, `machine/kinds.py`, `events.py`, `docs/release/core-m1.md`, `packages/aitm-core/pyproject.toml`). Each pair of writers is ordered by a direct or transitive Depends on edge. `services.py` forms one total chain: C01→C06→C07→C08→C14→C09→C10→C11→C12→C17→C21→C28→C31→C35→C43→C63.
- Coverage: every accepted-design CLI group appears in the CLI coverage map, and every design Acceptance row has an owning leaf and an integrated proof.

The decomposition is careful and mostly internally consistent. Several defects remain that would cause predictable JIT churn or block named proofs:

- One mandatory port has no owning contract and undefined interim behavior (F001).
- Touched-file allowlists cannot hold changes that the plan itself requires: dependencies/lockfile, CLI registration and package init files (F002, F003).
- A global test-lane invariant is enforced only at the end (F004).
- The final release leaf's proof is not executable as written (F005).
- One design-required init option has no owner (F006).
- The two largest qualification leaves are not credibly 3–3.5 h even though their scope is fully known now (F007).
- Leaf Produces lines omit contracts that later leaves consume by name (F008), and one test-lane placement contradicts the proof it requires (F009).

All of these can be fixed within the plan without changing the design.

## Findings

### R1-F001 — AttemptPreflight port has no owning contract and undefined behavior before C31

Evidence:

- The interface map (line 60) says C04 owns "the typed AttemptPreflight port and operation category before normal/recovery dispatch". However, C04's **Produces** line (line 284) lists only `Backend.read`, `transact`, `RelatedWriteSet`, `FinalizationIntent`, `WriteAuthorizer` and `PendingActionRunner`. C04's test (line 286) mentions neither AttemptPreflight nor operation categories.
- C28 (line 694) requires an "authored-sync ... own operation category". C31 (line 738) requires a "typed non-implementation category" and "Wire the C04 AttemptPreflight port". Both consume a contract that no leaf's Produces or test actually defines.
- C01 (line 202) makes ports mandatory: an absent implementation "returns unavailable. No permissive production fallback". AttemptPreflight is not in C01's enumerated port list, so its absent-implementation semantics are undefined.
- C28 is delivered before C31 (C31 depends on C28). Yet C28's own test asserts "Own the normal state-command pipeline: C31 preflight first, then C17 sync ...". It also asserts that a real advisory promote creates a provisional attempt, and that a later `attempt reconcile` preserves it. Between C28 and C31, an attempt-bearing story exists but no preflight implementation does.

Failure scenario: the C28 implementer has two options, and both are wrong:

- Treat the absent preflight as unavailable (C01's rule). The real promote/reconcile proofs then cannot pass.
- Treat it as pass-through. That is exactly the permissive production fallback C01 forbids.

Either way the C28 JIT must invent a contract the plan says was frozen at C04/Gate A. C31 may then find a different category model already embedded in C28's dispatch.

### R1-F002 — Dependency manifest and lockfile ownership is missing from the allowlists

Evidence:

- `packages/aitm-core/pyproject.toml` is touched only by C01 and C53 (shared-file table, line 1214). `uv.lock` appears in no leaf (a grep of the plan finds no occurrence).
- C03 (line 234) requires "Dependency/library selection must prove RFC8785". It also requires rejecting duplicate YAML keys/aliases/tags, which the common PyYAML defaults do not do. Both very likely add runtime dependencies, but C03's allowlist has no `pyproject.toml` or `uv.lock`.
- The same applies to any later leaf that needs a library, for example a SQLite FTS helper (C18), test dependencies for packaging (C59) or containment helpers (C36/C37).
- The plan states (line 47) that the touched-file expansion "defines the touched-file allowlist". The leaf cycle (step 5) commits exact paths.

Failure scenario: C03 either cannot commit its dependency, which violates the allowlist, or edits `pyproject.toml`/`uv.lock` outside any serialization edge. Meanwhile another parallel-eligible leaf in the same window (C02/C54/C55 branch independently after C01) may also modify the lockfile. The plan's shared-file overlap check (line 1189) cannot detect this because the paths are absent.

### R1-F003 — CLI registration and package-module creation do not fit the touched-file allowlists

Evidence:

- Line 62: "C01 establishes lazy command dispatch; leaves register only their own modules, with serialized changes to shared dispatch/schema exports when necessary."
- `cli/app.py` is touched only by C01 and C63. `cli/dispatch.py` is first touched by C09, and then C28.
- About 20 leaves add a command module (C06 `cli/planning.py`, C11, C12, C15, C16, C17, C18, C19, C22, C25, C26, C27, C28, C29, C30/C31, C34, C35, C38, C39, C42, C44, C45, C46, C61). None lists `cli/app.py`, `cli/dispatch.py`, a registry file or `pyproject.toml` entry points.
- So either the registration mechanism is convention-based (not stated anywhere) or every one of those allowlists is incomplete. In addition, the plan does not say whether C01 or C09 owns "lazy command dispatch" (`cli/app.py` vs `cli/dispatch.py`).
- Similarly, no leaf creates `src/aitm_core/__init__.py` or any subpackage `__init__.py` (`store/`, `models/`, `reviews/`, `machine/`, `verification/`, `delivery/`, `migration/`, `ext/`, `providers/`, `index/`, `reducers/`, `setup/`, `rules/`, `execution/`, `cli/`). C59 (line 1074) asserts on `aitm_core.__file__`, which is `None` for an implicit namespace package. `reducers/` (C54–C56) is also absent from the File and interface map (line 49–58).

Failure scenario: C15 adds `cli/describe.py` but cannot make `aitm describe` reachable without touching an unlisted shared file. Or several leaves each touch `cli/app.py` in parallel with no serialization edge. Either way, `test_cli_surface` in C49 fails, or merge conflicts arise that the overlap table claims are impossible.

### R1-F004 — Unit-lane isolation and the 10 s budget are enforced only at C52, and C52's check contradicts the rule it enforces

Evidence:

- Line 76 makes a global rule: "The shared unit suite contains no subprocess Git/network and must stay under 10 s." Fifteen leaves (C02, C03, C04, C13, C14, C15, C23, C27, C28, C29, C44, C54, C55, C56, C57) deliver unit-lane tests long before C52.
- The only enforcement artifact is C52's `tests/unit/test_isolation.py` ("actual complete MemoryBackend unit suite <10s with process/network calls trapped"). No `conftest.py` (or equivalent autouse guard) exists in any allowlist; a grep finds no occurrence.
- A test located inside `tests/unit/` cannot measure the wall time of the complete unit suite it belongs to without spawning pytest as a subprocess. That would violate the same no-subprocess rule, or be trapped by its own guard.
- C52's boundary (line 1064) limits it to "bounded lazy-import corrections". Anything else becomes a replan.

Failure scenario: an early unit leaf (for example C14 or C28, see F009) quietly spawns Git or touches the filesystem through a helper. Nothing fails until C52, roughly 55 leaves later. C52 then can only replan, and the fix belongs to an already delivered, reviewed and signed-off owning leaf. The invariant is cheap to enforce at C01 and expensive to retrofit.

### R1-F005 — C60's verification is not executable as specified

Evidence (lines 1100–1110, 1184):

- The checker is described ("checker rejects mismatched version/hash/source", "read-only dual-platform checker with `--release-manifest`"), but no allowlisted file implements it. C60 touches only `docs/release/core-m1.md` and `tests/packaging/test_published_release.py`.
- `--release-manifest` is not a pytest option. It requires a `pytest_addoption` hook (conftest or plugin) or a separate checker script, and neither is allowlisted.
- The **Verify and retain** command (line 1109) runs `test_published_release.py` without `--release-manifest`. The plan also says this suite is "invoked only after the publication operation completes" (line 1184), and "No leaf may mark a skipped requirement passed" (line 78). Without a manifest the suite must either fail or skip, so the leaf's own verify step cannot produce a valid PASS. It is also not separated from the "Checker fixture verification" step (line 1106), which has no command at all.
- Line 1184 refers to "The C60 job" running the full C5 manifest on both platforms. However, C60 touches no `.github/workflows/` file, while `core-ci.yml` (C59) and `core-release.yml` (C53) are owned by earlier leaves. C59 cannot define the C5 manifest job because the manifest is defined in C60 (line 1104).

Failure scenario: at C60 JIT, the implementer must add the checker module, an option hook and a CI job outside the allowlist, or the dual-platform released proof required for master C5 has no execution path. Both outcomes require changing an accepted decomposition at the last leaf.

### R1-F006 — Design-required `init --planning-branch` has no owning leaf or proof

Evidence:

- Design `aitm init` step 2 (core-design.md line 142) requires a configurable planning branch name: `--planning-branch <name>` non-interactively, default `planning`, an interactive accept/type prompt, and validation as a ref name. The name must also differ from the detected default branch, and must not already exist locally or remotely unless its full history and store identity match the trusted anchor or the same init journal.
- Design Acceptance "Init and policy" begins "Configurable orphan planning ref". The design also states "No code hard-codes the name" (line 114).
- In the plan, the CLI coverage map row for init (line 103) lists only `--local --default-branch --review-policy --reconfigure`. C11's test (line 436) covers UUID/genesis resume, publication and protection but not name selection or the collision/default-branch-equality refusals. The plan contains no occurrence of `planning-branch`.
- C49's `test_cli_surface` checks "the entire map". Because the map omits the option, the omission is invisible to the qualification audit.

Failure scenario: core ships with a hard-wired `planning` ref, or an implementer adds the option ad hoc without the existing-branch refusal rules. That is a direct design-acceptance gap that no planned test catches.

### R1-F007 — C50 and C49 are not credible ≤4 h leaves, and their scope is fully known now

Evidence:

- C50 (3 h, line 1002, scenario map lines 1171–1178) must build deterministic-barrier, seeded-schedule, two-real-clone infrastructure and pass at least nine named real-CLI scenarios:
  - `test_eight_by_fifty`
  - `test_conflicting_inputs`
  - `test_expansion_completion_fence`
  - `test_shared_stop_no_test_launch`
  - `test_trip_before_sync_and_pass`
  - `test_reservation_and_review_rebuild`
  - `test_local_delivery_admission`
  - `test_delivery_crash_reconcile`
  - `test_delivery_checkout_race`

  On top of that come six fault-injection families, then source review. That is about 20 minutes per cross-clone race scenario, including review.
- C49 (3.5 h, line 1046) must deliver:
  - the full nominal walk;
  - `test_cli_surface` over the entire ~25-route map;
  - `test_authored_sync_and_late_activation`;
  - `test_provisional_attempt`;
  - `test_evidence_only_rerun`;
  - `docs/learn/core-cli-walk.md`.
- C60 (2.5 h) includes checker fixtures, a release operation with lost-result reconciliation, dual-platform observation and docs.
- The plan's own rule (line 41) says a leaf whose proof burden makes four hours implausible should be split before Develop. It also says changes to leaf scope "invalidate the relevant accepted decomposition and need applicable review". Splitting these at JIT is therefore guaranteed re-review churn, even though the burden is visible today. C50 already has two independent suite files, which is a natural split.

Failure scenario: C50/C49 attempts trip the four-hour clock or consume their one expansion as planned overflow. The plan explicitly forbids that. Or the decomposition is re-reviewed mid-execution, at the most dependency-heavy point of the graph.

### R1-F008 — Produces lines omit contracts that later leaves consume by exact name

Evidence: line 60 states "Names/signatures below are proposed integration contracts; no task may silently fork one". Leaf issues are generated from each leaf section (line 1156). Several named contracts are defined only in prose inside test bullets, or consumed by name from a leaf whose Produces line omits them:

- `materialize_finalization(intent, chosen_child, pinned_snapshot) -> RelatedWriteSet` and the finalizer registration API. They are introduced in C22's test text, and consumed by C21 and C30 ("register the core expansion finalizer with C22"), but absent from C22 Produces.
- `ForwardRepairVerifier`: declared in C06's test text, installed by C10, absent from C06 Produces.
- `CutoverBuilder.preview(...)`: declared in C46's test text, absent from C46 Produces. C48's `build_cutover(...)` is likewise absent from C48 Produces.
- `reconcile_attempt(attempt, plan, binding)`: in C27's test text (consumed by C28/C49), absent from C27 Produces.
- `build_expansion_related(...)`: in C30's test text, absent from C30 Produces.
- `run_installed_suites(artifact, suite_manifest, platform)`: in C59's test text, consumed by C60, absent from C59 Produces.
- Port ownership is duplicated between C01 ("write authorization ... init hooks, action retry" ports) and C04 (`WriteAuthorizer`, `PendingActionRunner` ports) and C11 (`InitHooks.install` port). The plan does not say which leaf owns the type and which owns the wiring slot.

Failure scenario: a consumer JIT checks the producer's Produces line, which is the declared contract index, finds the interface missing, and either re-derives it differently or treats it as unfrozen. That is the silent fork line 60 prohibits, and the Gate A contract freeze (line 1140) cannot verify contracts that are not indexed.

### R1-F009 — C28 is placed in the unit lane but its required proof needs real sync, binding and CLI behavior

Evidence:

- C28's verify command uses `packages/aitm-core/tests/unit/test_c28.py` (line 696). Yet its test requires:
  - a "Real advisory promote to Develop";
  - real `bind --implementation` and `attempt reconcile`;
  - "C17 sync of eligible bound authored inputs as a separate saved/reported operation";
  - sync-conflict retention of both versions.
- C16 and C17 own binding/workspace sync and are integration-lane leaves (`tests/integration/test_c16.py`, `test_c17.py`) because they touch real worktree/branch state.
- The unit lane forbids subprocess Git (line 76).

Failure scenario: the C28 author must either fake the binding/sync path, weakening the "real" proof that C49's `test_authored_sync_and_late_activation` relies on as the producer's delivered behavior, or add subprocess Git to the unit lane, breaking the 10 s/no-subprocess rule (see F004). Either outcome is a JIT-time scope change.

## Required changes

1. F001: Add AttemptPreflight and the typed operation-category contract (normal, authored-sync, stop/reconciliation, recovery) to C04's **Produces** line and C04's test. Add AttemptPreflight to C01's mandatory-port enumeration, or explicitly exclude it with stated semantics. State the interim behavior between C04 and C31. For example: "no attempt in read-set → not applicable; attempt present and no installed preflight → C28 tests use a declared typed fixture preflight, and production reports preflight unavailable for attempt-bearing implementation mutations". Then have C31 re-run C28's pipeline-order assertions with the real preflight. Apply the same interim-semantics statement to write authorization before C14.
2. F002: Add `packages/aitm-core/pyproject.toml` and `uv.lock` (root) to C01's allowlist, and to the allowlist of every leaf expected to add a dependency, at minimum C03, plus any leaf whose JIT adds one. Add serialization edges for those paths to the shared-file table. Alternatively, state that C01 pins every planned runtime/test dependency up front and that later dependency additions are a coordinated contract change.
3. F003: State the CLI registration mechanism explicitly:
   - either convention-based discovery that requires no shared-file edits, or a named registry file added to every CLI-owning leaf's allowlist with serialization edges;
   - which of C01/C09 owns lazy dispatch in `cli/app.py` vs `cli/dispatch.py`.

   Also add `src/aitm_core/__init__.py` and the needed subpackage `__init__.py` files to the creating leaves' allowlists, or state a creation convention. Add `reducers/` to the File and interface map.
4. F004: Move the unit-lane guard (an autouse fixture trapping subprocess/socket, for example `tests/unit/conftest.py`) into C01 so every unit leaf runs under it from the start. Then have C52 measure total unit-suite wall time from a non-unit lane (performance/CI job), not from a test inside `tests/unit/`.
5. F005: Add to C60's allowlist:
   - the checker implementation (module or script path);
   - the `--release-manifest` option hook;
   - the CI workflow job that runs the post-publication C5 manifest on both platforms (or move that job definition to C59/C53 with the manifest it needs).

   Split C60's verification into explicit commands: (a) a checker-fixture suite that runs and passes before publication; (b) the post-publication command with `--release-manifest <path>`. Make clear which one is the leaf's PASS evidence before source review and which one is retained evidence after the authorized release.
6. F006: Add `--planning-branch` (and the interactive name prompt) to the init row of the CLI coverage map. Add to C11's test:
   - name validation;
   - refusal when equal to the detected default branch;
   - refusal of an existing local/remote ref unless its full history/store identity matches the trusted anchor or the same init journal;
   - a non-default name used end to end (no hard-coded `planning`).
7. F007: Split C50 at least into a shared-store conflict leaf (`test_shared_store.py`) and an execution/delivery race leaf (`test_execution_races.py`). Split C49 at least into a nominal-walk leaf and a CLI-surface/provisional/evidence-rerun leaf. Reassess C60 together with F005. Update the estimate total, leaf count, dependency rows, scenario map and acceptance table accordingly.
8. F008: Add each consumed-by-name contract listed in F008 to its producer's **Produces** line. Resolve the C01/C04/C11 port-type vs wiring-slot ownership in the interface paragraph (line 60).
9. F009: Move C28's test to the integration lane, or split it into a unit-lane transition-matrix test and an integration-lane real promote/sync/attempt-reconcile test, with both commands named in the Verify step.

## Optional suggestions

### R1-F010 — Replace the absolute local path to the interim review strategy

Line 1154 binds this plan's review procedure to `/Users/kpburson/projects/aitm-workspace/trunk/.tmp/interim-review-strategy.md`. That is an absolute, machine-local, `.tmp` path with no digest. The file exists on this host, but other clones, reviewers and the later C46/C51 migration fixtures cannot resolve or verify it. Consider citing a committed location, or recording its SHA-256 and the exact revision used.

### R1-F011 — Map or remove C44's `cli/outcomes.py`

C44 creates `src/aitm_core/cli/outcomes.py`, but neither the accepted design CLI table nor the plan's CLI coverage map has an outcomes/usage route. Either map the route (and include it in `test_cli_surface`) or drop the module so C49's "complete accepted-design CLI map" audit does not silently skip a shipped command.

### R1-F012 — Remove duplicated test paths in qualification-leaf allowlists

C49–C53, C59 and C60 list both `tests/...` (relative to P) and `packages/aitm-core/tests/...` for the same file, for example C51 line 968. Under the line-47 convention both resolve to the same path. Listing one form avoids confusion when the overlap check is rerun at JIT.

## Decision

revisions-requested
