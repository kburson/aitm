<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-2717a3266155585c61b8d6e9cf75c84a"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_commit: "87c3f104e7349fcc6b77c67ec5ae2fb0f664469a"
artifact_blob: "d3c7ccce15ec822ca38d582d7c42cdd99dba0694"
artifact_digest: "sha256:29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:c8254d8e818025ffb23e08bc62f632a5bcbb5293376cd944530280a09f8db56e"
  identity_source: "runtime"
started_at: "2026-11-10T18:55:56.402Z"
submitted_at: "2026-11-10T19:00:21.142Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Round 2 review of artifact blob
`d3c7ccce15ec822ca38d582d7c42cdd99dba0694` at commit `87c3f104…`.
Retrieval: fresh numbered Reads of the exact invitation artifact path,
lines 1–40, 41–80 and 81–95; line 95 is EOF. No range was truncated. I
checked author response 1 against this full read, not against its
summary.

**R1-F001 — resolved.** Line 11 states that #138 and #140 share the
implicit `tia` namespace with no `__init__.py` or other shared package
file, and that the test imports `tia.snapshot` with `tools/ci` on its
module path. Lines 75–81 give the focused command
`PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_snapshot.py`,
run from the physical checkout root. The red case must reach the
behavior assertion rather than fail collection or import. This matches
the paired #138 boundary. It keeps the owned paths to the two named
files, so either leaf can land first without conflict.

**R1-F002 — resolved.** Line 73 records the focused run's exact-head
command, tree, runtime, collected node IDs and red/green results,
separately from the exact-candidate #103 evidence. Lines 83–92 state
that #103 does not execute the new test or measure `snapshot.py`; only
the four `policy["helpers"]` files count, at 778/821. The design claims
no numeric coverage for the module. The helper policy, coverage roots
and workflow test list are explicitly excluded from the leaf. The
pinned verifier treats `tools/ci/` additions as gate-defining (author
verification of the prefix matcher), so the leaf uses the existing #103
exact-tree owner disposition and independent review. It does not rely
on downstream T10. The gate-defining set is reconfirmed at JIT, and a
changed scope or failed gate holds delivery. These statements agree
with the pinned-trunk evidence supplied for this review.

**R1-F003 — resolved.** Lines 33–50 add a Git observation profile with
these properties:

- read-only raw NUL-delimited plumbing with original objects;
- no optional index writes and no on-demand fetch, with the Git version
  recorded in provenance;
- refusal when offline object reads cannot be guaranteed for a possible
  promisor or partial repository;
- a clean environment that drops inherited config overrides and skips
  system and global config;
- fsmonitor and untracked cache forced off;
- external diff, textconv, orderfile and submodule omission disabled;
- rename detection pinned at 50% similarity with a 1,000 limit;
- a rename-limit warning or truncated output treated as uncertainty.

Line 54 limits untracked membership to repository per-directory
`.gitignore` rules, excluding personal and global excludes and
`.git/info/exclude`. It binds the consulted ignore paths and contents
and rechecks them with membership. Line 72 adds a configuration
isolation acceptance case. Line 25 now also refuses an unbindable
gitlink or other non-blob endpoint, and line 10 assigns serialization
to the immutable-resolution hour. Both optional suggestions are taken
up.

A re-check of the earlier strengths found no regressions:

- scope, owned paths, consumers and estimate still match T03;
- exact hosted identity still binds `[base, head]` parents and the
  tested tree;
- the local snapshot still fails closed;
- raw-byte path handling is unchanged;
- refusal still never becomes an empty change set;
- implementation stays independent of #138.

No required changes remain. This acceptance precedes refinement. It
grants no implementation, activation or publication authority.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. On macOS, the repository-local `core.precomposeUnicode` setting
   (normally true on macOS clones) makes Git report NFD on-disk names
   as NFC. The recorded path bytes for an untracked or worktree path
   could then differ from the filesystem's bytes. Consider adding it to
   the fixed observation profile (or recording its effective value).
   Consider also adding an NFD-named fixture to the path-handling case
   on the qualified APFS route, so the "no Unicode normalization" rule
   holds end to end.

## Decision

accepted
