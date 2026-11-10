# #140 Resolve exact Git changes Implementation Plan

> **For agentic workers** REQUIRED SUB-SKILL. Use `subagent-driven-development` or `executing-plans` after separate implementation authorization. The checkboxes describe future work.

**Goal** Give the trusted CI planner and the local advisory runner the exact before and after source, including former paths, or a typed uncertainty that prevents narrowing.

**Architecture** Share one strict raw-byte Git observation profile and one canonical snapshot format. The hosted path binds immutable Git objects to trusted caller evidence. The local path binds the story-base tree to two matching observations of HEAD, the index, membership and effective worktree bytes.

**Tech stack** Python 3.13, standard library, Git plumbing, locked uv and pytest. The current #103 route pins Python 3.13.9 and uv 0.10.6.

**Spec** [Accepted #140 design](../design/resolve-exact-git-changes-design.md), SHA-256 `29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248`. [#133 T03 at publication](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L204).

## Global constraints

- Own `tools/ci/tia/snapshot.py` and `tools/ci/tests/test_tia_snapshot.py`. Use the implicit `tia` namespace. #138 owns the separate serial baseline and shares no writable paths. #141 and #147 consume the snapshot interface.
- Preserve Git's raw repository-relative path bytes and ordering. Preserve Git object IDs and modes for committed and staged content. Use SHA-256 for effective local bytes and the canonical snapshot.
- Preserve original Git objects, a read-only profile, and fail-closed observations. No live authority acquisition, test selection, fallback execution, gate-policy changes, or new dependencies belong to this leaf. Keep local snapshots private.
- Budget 3 implementation agent-hours, with a four-hour cap. The [JIT pickup note](2026-11-10-140-jit.md) binds the target and current evidence. Planning is the current stop point.

## Review focus

- Git replacement refs can silently substitute a pinned object. Task 1 verifies comparison and later content reads.
- Global/repository config can redirect object access, invoke a driver, or change paths and membership. Tasks 1 and 2 prove the fixed profile, ignore sources and offline refusal.
- APFS may resolve a different case or normalization spelling to the same inode. Task 2 checks the filesystem byte spelling and refuses aliases. Task 1 round-trips byte names directly from Git objects.
- A clean cached stat, restored mtime, or staged rename can hide the effective after bytes. Task 2 hashes files independently of status and preserves each observation layer.
- A failed Git read, unsupported file type, or changed index or path set can leave a plausible partial result. Both tasks assert typed uncertainty instead of a pair.

## Files and interfaces

- Create `tools/ci/tia/snapshot.py` for the two request types, snapshot and change records, Git observation, and safe local reads.
- Create `tools/ci/tests/test_tia_snapshot.py` for temporary Git repositories and injected Git/read failure fixtures. Use the real public resolver for successful paths and refusals. Isolate process config changes through pytest fixtures.

Expose `resolve(repo: Path, request: HostedRequest | LocalRequest) -> tuple[Snapshot, Snapshot]`, before first, and `SnapshotUncertain` with `mode` and a stable machine-readable `reason`. Use reasons that distinguish missing authority or baseline, contradictory identities, missing or unsupported objects, malformed data, unsafe paths, command failure/timeout, unsupported profile, unreadable input and drift. A refusal returns no pair. Use `Snapshot.read_content(path: bytes) -> bytes` against the recorded endpoint identity, and make the sorted endpoint entries and shared changes available to consumers. A failed read raises the same typed uncertainty.

Each `Snapshot` and its versioned canonical record carries `repository`,
`mode` (`hosted` or `local`), `ref_role`, `endpoint_identity`,
`baseline_identity`, sorted endpoint entries and the shared sorted
changes. `baseline_identity` is the exact baseline commit and tree on
both sides. The before role is `baseline` and its endpoint identity
equals that commit and tree. The after role is `pr-tested`,
`trunk-tested` or `local-effective`, as applicable. The hosted after
identity is the exact tested commit and tree, with the trusted ref and
run/attempt retained in hosted provenance. The local after identity is
the effective worktree observation digest, binding HEAD, the index,
membership, modes and content. SHA-256 of the canonical snapshot bytes
binds these fields and the applicable provenance as well as the paths.

`HostedRequest` carries repository, ref role and ref, trusted run/attempt binding, applicable base, tested commit/tree and PR head when applicable. Validate agreement with the supplied binding. The trusted caller acquires provider evidence and checks freshness. A local request carries the repository identity, local ref role, declared story-base commit and explicit relevant ignored input paths when known. The physical worktree is `repo`, and HEAD is observed there. For hosted full comparison use the supplied explicit baseline and tested endpoint without PR parent validation. If the applicable baseline is unavailable, refuse the comparison.

## Task 1. Bind hosted Git snapshots and the observation profile

**Files** Both owned paths. **Budget** 1 hour including canonical record and digest.

- [ ] Add a minimal importable API scaffold for the red run. Add `test_hosted_diff_matches_tested_tree` with a merge result deliberately different from the PR head. Assert that merge-only bytes are read from the after snapshot, old deletion bytes from the before snapshot, and the sorted changes include the actual base-to-tested endpoints. Inspect both snapshots and decoded canonical records for repository, hosted mode, baseline and PR-tested roles, exact before and after commit/tree, shared baseline, and trusted run/attempt. Rebind an otherwise identical valid fixture to a different matching trusted attempt and assert the canonical digest changes while paths and content stay equal. Assert that wrong base/head, reversed or extra parents, wrong tested tree and missing or contradictory run/attempt/ref linkage each raise `SnapshotUncertain`. Add a hosted full comparison with an explicit baseline, and assert that a missing baseline refuses.
- [ ] Add `test_hosted_object_failures_and_raw_paths`. Round-trip a tab/newline name, a non-ASCII name and a non-UTF-8 name from Git tree objects created without a filesystem checkout. Assert order by raw bytes, reversible path encoding, stable digest for the same record, and a changed digest for changed endpoint identity. Exercise add/delete, a rename, a mode or type change, a malformed or duplicate NUL record, an escaping path, a changed gitlink, missing commit/blob, and command failure/truncation with a valid prefix. Assert the prior pinned bytes under a replacement commit or blob ref, including a later read. Assert that an unsupported offline profile with possible promisor state refuses before object reads.
- [ ] Run the focused command below with `-k hosted`. Red must collect/import and reach the positive comparison assertion, which fails because the scaffold cannot return the expected pair. Retain the actual red assertion and exit status.
- [ ] Implement immutable hosted resolution. Verify full pinned object identities and types, read the actual ordered parents for a PR, and compare the tested commit's object-derived tree to the expected tree. Enumerate tree entries and diff base tree against tested tree using `--no-commit-id --raw --no-abbrev -r -z`. Validate full object IDs, field counts and complete NUL framing. Retain old and new path, mode and identity as applicable. Keep delete/add separate when Git reports them separately. Read immutable endpoint bytes by original object ID. Keep the records versioned and canonical, with reversible base64 path encoding, deterministic key and raw path order, and SHA-256 over the canonical record.
- [ ] Implement the shared Git profile. Verify Git identifies the pinned physical root, strip inherited Git overrides, skip global and system config, and force fsmonitor and untracked cache off. Disable replacements, optional index writes and lazy fetch, including later endpoint reads. Probe the offline flag on the actual executable. Without it, proceed only if a possible promisor/partial repository has been ruled out from repository metadata and all applicable object stores. Unknown alternates or unreadable metadata cannot establish absence. Set explicit time/output limits, require successful complete parsing, and refuse rename-limit warnings. Use `--no-ext-diff --no-textconv -O/dev/null --ignore-submodules=none --find-renames=50% -l1000` for diffs. Record Git version and profile in provenance.
- [ ] Rerun `-k hosted`. Expect all hosted cases to pass with no collection error. Checkpoint only the two owned paths under the eventual implementation authority.

## Task 2. Observe and recheck the effective local worktree

**Files** Both owned paths. **Budget** 1 hour for observation/refusals and 1 hour for fixtures and verification.

- [ ] Add `test_local_staged_untracked_rename_and_deleted_paths`. Use a committed change after base, a staged rename with staged bytes, an unstaged edit or deletion after the rename, a separate deletion and a relevant untracked file. Assert original and effective content reads, both rename endpoints, stage identities and deletion versus unreadable. Inspect both snapshots and decoded canonical records for repository, local mode, baseline and local-effective roles, and the shared baseline commit/tree. Assert that the before endpoint equals the baseline and the after endpoint names the effective digest. Assert a clean comparison yields empty changes, and cancelled final changes can be empty while layered provenance and the after digest still bind the changed HEAD/index state. With fixed HEAD, index and worktree, use two baseline commits that share a tree. Assert equal change records and after endpoint identities, but distinct baseline identities and after canonical digests.
- [ ] Add `test_local_observation_drift_refuses`. Inject changes to HEAD, stage OID, same-path bytes with restored mtime, mode, or untracked membership between observations. Each raises drift. Assert a preexisting same-stat byte change is captured, and a changed later read either refuses or serves the exact immutable captured bytes. Unresolved stages, unsupported files, unreadable or escaping paths and unsafe symlink ancestors/targets raise uncertainty.
- [ ] Add `test_local_git_config_and_path_identity`. Use conflicting global rename/exclude config, `.git/info/exclude`, a repository `.gitignore` and a separately declared relevant ignored input. Assert stable fixed-profile changes and membership, retention of consulted ignore path/content identities, refusal on ignore drift, and no invocation of configured external diff or fsmonitor. Exercise a decomposed UTF-8 filename on APFS with `core.precomposeUnicode=true` in the fixture repo. Assert either the observed filesystem byte spelling round-trips or a spelling the filesystem cannot safely represent raises uncertainty. Include a deliberate case/normalization alias and require refusal. Use hosted object fixtures for raw names the filesystem cannot create.
- [ ] Add `test_local_unaccounted_ignore_inputs_refuse`. Keep Git's raw membership output valid and stable. Inject a checked-read failure first for a consulted repository `.gitignore` and then for a declared relevant ignored path. Assert that each call raises `SnapshotUncertain` with local mode and an unreadable-input reason before it can return a pair. Also resolve a declared ignored leaf whose absence can be established beneath a verified parent. Assert successful resolution with that leaf observed absent.
- [ ] Run the focused command with `-k local`. Red must reach the local behavior assertion and fail because the local resolver is absent. Preserve the red output and identify any fixture/platform skips separately.
- [ ] Implement local observation. Read the original story-base tree, pin HEAD, retain base-to-HEAD changes and capture every `git ls-files --stage -z` stage mode/path/OID. Observe staged and effective unstaged changes separately so cancellation and staged rename provenance survive. Derive effective content by reading and hashing every tracked worktree file, even when Git reports it clean, plus untracked membership from per-directory `.gitignore` alone and explicit relevant ignored inputs. Bind the consulted ignore inputs and membership. Refuse if any required ignore rule or declared relevant ignored input cannot be bound to bytes or to verified absence, even if Git reported the same membership twice. Use `git ls-files --others --exclude-per-directory=.gitignore -z` without standard exclusions. Treat an unpaired move as delete/add. Distinguish observed absence from permission, path or object errors.
- [ ] Bind all reads beneath a pinned physical root with descriptor-relative no-follow walks or equivalent checked opens. Compare exact directory-entry bytes and reject aliases. Disable Git Unicode precomposition and case folding for the raw-path profile and record the effective settings. Bind a symlink as a link only if its effective in-root target can also be accounted for. Compare file identity and metadata around reads. Repeat HEAD, index, path membership including ignores, modes and effective digests. Any disagreement invalidates the pair. Revalidate later worktree content against the recorded identity or serve captured immutable bytes. Leave revalidation at execution to the downstream runner.
- [ ] Rerun the full focused command. Expect all cases to pass and retain exact-head evidence below. Checkpoint only the two owned paths.

## Verification and delivery evidence

Run from the physical source checkout root. For the red runs append the listed `-k` filter. Collect node IDs for the same focused file using the same command with `--collect-only` added.

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_snapshot.py
uv run --project packages/aitm-usage --locked ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/snapshot.py tools/ci/tests/test_tia_snapshot.py
uv run --project packages/aitm-usage --locked ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/snapshot.py tools/ci/tests/test_tia_snapshot.py
```

Retain each red and green command, exit, assertion or result, node IDs, runtime and Git/APFS profile, tree and base. Bind red from the recorded test/scaffold input and green to the exact candidate, rerunning the focused green on the reviewed tested tree when it differs from the story head. Record any unavailable fixture capability with its effect on proof. Keep focused proof separate from the [#103 CI contract](../../103/design/github-ci-quality-gates-design.md). The existing hosted workflow does not collect the focused file or include the resolver in its gated line denominator. Both new paths count as gate-defining under `verify_pr.py`. The [JIT pickup note](2026-11-10-140-jit.md) specifies the current target proof, exact-candidate owner disposition and independent review, verification and hold conditions.
