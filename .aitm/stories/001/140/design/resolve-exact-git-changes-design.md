# AITM #140 · Resolve exact Git changes

**Refinement draft.** [Story #140](../story.md) · [Accepted #133 design](../../133/design/test-impact-analysis-design.md) · [Accepted T03 plan at publication](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L204)

As a story implementer or trusted CI planner, I want an exact before and after view of the source under test so that impact analysis can find current and former test consumers, or stop narrowing the test set when the Git or working-tree evidence is incomplete.

## Scope and estimate

- **Owned implementation** `tools/ci/tia/snapshot.py` and `tools/ci/tests/test_tia_snapshot.py`. No required predecessor. The snapshot pair feeds #141 (Python and package edges) and #147 (gate changes and inventory dispositions).
- **Retain 3 implementation agent-hours, size M, P1.** Allow about one hour for immutable Git resolution and path records, one for the local observation and refusal path, and one for the focused fixtures and checks. The immutable resolution hour includes canonical serialization and digests. P1 reflects the two direct consumers and the risk of missing former test consumers. The budget assumes a small standard-library resolver using the existing Git evidence contract and fixtures. Recheck at JIT. Bring any new platform, CI integration, or wider ownership requirement back to refinement before exceeding the four-hour leaf limit.
- #138 owns the separate serial comparison baseline, its report, timing and outcome custody. #140's baseline identity is the exact source endpoint used for a diff. It does not consume #138's report or edit its files. GitHub metadata acquisition, policy changes, selection, test execution, authoritative outcomes and fallback orchestration belong to their existing or downstream owners. The two modules use the implicit `tia` namespace without an `__init__.py` or other shared package file. The focused test imports `tia.snapshot` with `tools/ci` on its module path.

## Resolver contract

`resolve(repo, request) -> tuple[Snapshot, Snapshot]` returns a complete pair in before/after order. A typed uncertainty carries mode and a stable reason when exact resolution fails. An uncertain call returns no usable pair. A successful empty change set means the requested comparison was established and found no changes.

Both snapshots carry repository identity, mode and ref role, their endpoint and baseline identities, and a stable sorted change record shared by the comparison. Each change preserves status and the present old and new paths, with mode and content identity on each present side. Additions have a new side, deletions an old side, and Git-detected renames both. Preserve mode or type changes. If Git reports a move as a deletion and an addition, retain both independently. Both endpoints support reading the content at the recorded identity for downstream graph construction. A missing or changed endpoint read yields uncertainty.

Keep Git paths as raw repository-relative bytes in parsing, comparison and ordering. At a serialization boundary use versioned canonical JSON with a reversible path encoding, such as base64, and a SHA-256 digest of the canonical record. Hash local file bytes with SHA-256 and retain hosted Git object IDs. Avoid case folding, Unicode normalization and replacement decoding. Reject malformed NUL records, duplicate or aliased paths, absolute paths, and empty, `.` or `..` components before path access. Paths that the active filesystem cannot represent safely yield uncertainty. Display names carry no identity.

### Hosted inputs

Accept the exact repository, ref and run/attempt binding and applicable base, PR head, tested commit and tested tree from a trusted caller. Cross-check the pinned objects. For a PR, the tested commit must have exactly the ordered parents `[base, head]` and the object-derived tree must match the expected tested tree. Diff the actual base tree against that tested tree using NUL-delimited tree output. Read tree or blob content from Git objects by identity. For a hosted full trunk comparison accept its explicitly pinned tested commit/tree and applicable baseline when supplied by the caller. PR parent rules apply to PR requests.

The current #103 verifier resolves the live target and head and checks ordered test-merge parents, exact tree, canonical run and attempt. Its receipt shape supplies the input binding precedent. The trusted controller may establish the same identity before execution. #140 uses that binding and Git objects. Missing objects or provider linkage, a mismatch or stale binding, or an unreadable Git result yields uncertainty. No fallback to a checkout's contents, a moving ref, a merge base, the PR head tree, or an earlier attempt. The caller owns freshness checks against live authority before use. Refuse a changed gitlink or other non-blob endpoint when its effective input cannot be bound by this repository.

Disable Git replacement refs for every pinned commit, tree, diff and
blob read using `git --no-replace-objects` or its equivalent. Apply
the same constraint to the local story-base and any later endpoint
content read so the object identity continues to name original bytes.
[Git replacement reference behavior](https://git-scm.com/docs/git-replace#_description)

### Git observation profile

Use read-only Git plumbing with raw, NUL-delimited records, original
objects, no optional index writes, and no on-demand fetch. Use the Git
version and supported command profile in provenance. Refuse before
reading objects if the Git version lacks an offline object-read control
and a promisor or partial repository cannot be ruled out.

Use the physical repository with a clean Git environment. Remove inherited
repository and command-config overrides, skip system and global config,
and override the repository fsmonitor and untracked cache to off. Keep
repository metadata needed to identify its object store and index. For
Git diff commands explicitly disable external drivers and text conversion,
disable path ordering overrides and submodule omission, and pin rename
similarity to 50% with a fixed limit of 1,000. A rename-limit warning,
command failure or truncated output yields uncertainty. Retain both sides
when the fixed profile reports an addition and a deletion. Recheck the
profile at JIT on the supported Git version.

### Local inputs

Take the declared story-base commit, the physical worktree and the current HEAD. Observe committed base-to-HEAD changes, HEAD-to-index staged state and index-to-worktree unstaged state separately. Record stage modes, paths and object IDs and preserve old and new endpoints across the layers. Hash effective worktree content for tracked paths and relevant untracked paths, including files with no index entry. Default to all untracked files outside the repository `.gitignore` rules, plus any independently declared relevant ignored inputs. Use per-directory `.gitignore` rules without personal global exclusions or `.git/info/exclude`. Bind the consulted ignore paths and contents and recheck them with membership. If relevant ignored input or an ignore source cannot be accounted for, return uncertainty.

The before endpoint is the story-base tree. The after endpoint is the actual worktree view, with file bytes, modes, membership, and absent paths recorded. Staged content remains provenance when an unstaged edit or deletion supersedes it. Bind HEAD and index state in the after identity, including changes that cancel across layers. Hash tracked content even if Git's status or cached stat data appears clean. Preserve a staged rename followed by an edit or deletion at its destination. Treat an unpaired local move as old-path deletion and new-path addition.

Read under the pinned physical repository root with a no-follow path walk or equivalent checked open. Bind a symlink as a link only where the observation can safely account for the effective input. An external or unverifiable target, unsafe ancestor, unresolved index stages, or an unsupported effective file type yields uncertainty. Repeat the Git identity, stage and path membership observation and effective content digests after reading. Compare the file identity and metadata around reads. A changed HEAD, index, file, mode or path set, including a new or disappearing untracked path, invalidates the result. A stable pair describes the observed bytes. The downstream local runner must revalidate at use or run from captured immutable bytes. Local results are advisory and remain private.

### Refusals

Return a reason for missing authority or objects, contradictory identity, malformed or unsupported data, path escape or alias, command failure or timeout, an unreadable file, an unsupported observation profile, or observation drift. Treat failed or truncated Git output as uncertainty even if it contains a valid prefix. A hosted identity failure holds hosted validation. If only selection is uncertain and independent evidence still establishes the exact candidate and applicable base, downstream policy may use the full suite. Never interpret a refusal as an empty change set.

## Acceptance evidence

| Case | Required observation |
| --- | --- |
| `test_hosted_diff_matches_tested_tree` | A Git fixture whose merge tree differs from its PR head produces the actual base-to-tested changes, including merge-only content. Incorrect base, head, parent order, tested tree, or unbound run provenance refuses. Missing Git objects or a failed read refuses without returning a partial pair. |
| `test_local_staged_untracked_rename_and_deleted_paths` | The fixture includes committed changes after the declared base, a staged rename and staged bytes, a separate unstaged edit or deletion, and a relevant untracked file. Verify the old and new identities, rename endpoints, deleted content on the old side, and effective worktree content on the new side. Exercise clean and cancelled-layer comparisons, and inject same-path byte, index, or path-set changes during observation to require uncertainty. |
| Original Git objects | With a replacement ref on the pinned base or its blob, the comparison and endpoint content read use the original bytes or return uncertainty. |
| Path handling | Round-trip non-ASCII, non-UTF-8 and delimiter-bearing names where supported, keep their stable byte identities, and refuse an escaping or aliased path. A normal deletion remains distinct from an unreadable file or an unresolved Git object. |
| Git configuration isolation | Conflicting global rename and exclude settings and `.git/info/exclude` leave the fixed comparison and untracked membership unchanged. Repository `.gitignore` still applies. Configured external diff and fsmonitor programs do not run. |
| Delivery | Retain exact-head command, tree, runtime, collected node IDs and red/green behavior results for the focused run. Record exact-candidate #103 evidence separately. |

Run the namespace-aware V(snapshot) command from the physical checkout root.
The red case must reach the expected behavior assertion rather than fail
collection or import.

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_snapshot.py
```

At the pinned trunk revision, #103 neither executes the new focused test
nor measures `snapshot.py` in its gated helper scope. It sums only the
four named `policy["helpers"]` files, with 778/821 observed gated lines.
The focused run supplies the new module's execution evidence. This design
claims no numeric coverage for `snapshot.py`. Keep the helper policy,
coverage roots and workflow test list out of this leaf. Reconfirm the
protected target, qualified CI route and gate-defining path set at JIT.
The pinned verifier includes `tools/ci/` additions in that set. Obtain the
existing #103 exact-tree owner disposition and independent review when
required. A changed scope or failed gate holds delivery for reassessment.

Refinement inspected source ref `origin/trunk` at `37a22922f072e39c35434ae645a1c20692b8da01`. The relevant interfaces are `tools/ci/verify_pr.py` (`verify_pr`, `report_evidence`), `.github/workflows/ci.yml` (pinned candidate checkout and base/run evidence), and `tools/ci/file_checks.py` (byte-oriented Git file enumeration). The leaf design, plan, JIT, and implementation authority remain separate gates.
