---
schema: "aitm.review-response/v0"
level: "xpr"
story: 140
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/001/140/design/resolve-exact-git-changes-design.md"
artifact_base_commit: "9308cffd586c003c5ce8112ab3c91d1088999db8"
artifact_digest: "sha256:f20d48b0ad669f29378901b275ad8b22f1e0f364503c19460e37da41367fe029"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:c8254d8e818025ffb23e08bc62f632a5bcbb5293376cd944530280a09f8db56e"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T18:55:56.453Z"
submitted_at: "2026-11-10T18:58:06.532Z"
start_basis: "claim"
start_source: "native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-review-manifest.md#claim-claim-46194394-fd6f-4011-ac77-4bb668b5de2a"
finding_ids: ["R1-F001", "R1-F002", "R1-F003"]
answered_finding_ids: []
native_source: "native/spec/2026-11-10-resolve-exact-git-changes-design-review-2717a3266155585c61b8d6e9cf75c84a/review-2717a3266155585c61b8d6e9cf75c84a-reviewer-response-1.md"
native_source_digest: "sha256:127f5b0daf8bf014f3278e3170a3ab82af5b811f07c75e3e82edb95db0f27801"
---

Mode: `normal`

## Summary

Independent cross-provider review of the #140 leaf design at artifact
blob `fc752b3eeff4aa622960c46ab8f4a1be19be4392`. Retrieval: fresh
numbered Reads of the exact invitation artifact path, lines 1–40 and
41–58; line 58 is EOF. No range was truncated.

Compared against: the accepted T03 section of the #133 plan (lines
204–215), its global constraints, interface table, V(module) convention
(lines 87–126) and coverage boundary (lines 851–876); the accepted #133
design §2 validation modes and §3 inputs, resolution and fallback
(lines 40–145); the #140 story excerpt and `plan-origin` (publication
`dbe0d68b…`, matching the artifact's link); the #103 design's verifier
and gate-defining rules (lines 17–21, 51); and the source facts at
pinned trunk `37a22922f072e39c35434ae645a1c20692b8da01` supplied in the
review instructions (explicit #103 helper test list; `python_gate`
helper denominator; 778/821 unchanged by an unmeasured `tools/ci/tia/`
file; the paired #138 revision's `tia` boundary).

What is sound:

- **Scope and parent fidelity.** Owned paths, interface signature,
  "no predecessor", consumers #141/#147 and the 3h/M/P1 estimate match
  T03 and the story. The leaf takes no #138 report or file and
  correctly separates #138's serial comparison baseline from #140's
  diff-endpoint baseline identity. Downstream selection, policy,
  execution and fallback stay with their owners.
- **Exact hosted identity.** Lines 23–25 bind repository, ref,
  run/attempt, base, PR head, tested commit and tested tree; require
  ordered parents `[base, head]` and an object-derived tree match; diff
  base tree to tested tree with NUL output; and refuse rather than fall
  back to a checkout, moving ref, merge base, PR head tree or earlier
  attempt. This matches #133 §2/§3 and the #103 verifier precedent.
  Freshness against live authority is correctly left to the caller.
  Replacement refs are disabled for all object reads (lines 27–31).
- **Fail-closed local snapshot and paths.** Lines 33–39 separate the
  committed, staged and unstaged layers, hash effective content
  regardless of stat state, include untracked files, bind HEAD and
  index in the after identity, use a no-follow walk under a pinned
  root, re-observe after reading, and invalidate on any drift. Raw-byte
  paths, reversible encoding, and rejection of NUL, duplicate, aliased,
  absolute and `.`/`..` paths before access are specified (line 19).
  Refusal is never an empty change set (line 45). Local results stay
  advisory and private, matching #133 §2.
- **Former consumers.** Both rename endpoints and old-side deletion
  content are preserved, and an unpaired move keeps both sides, which
  is what T04/T05 need for the base graph.
- **Acceptance cases** cover the plan's named tests, missing objects,
  path escape and non-ASCII fixtures, plus replacement refs and
  mid-read drift.

Three material issues remain, all in the delivery and determinism
boundary rather than the core resolver model: the `tia` import and
namespace boundary is unstated and the focused command as written does
not establish it; the delivery row does not say that #103 provides no
execution or coverage evidence for the new module; and Git
configuration that changes the observed change set or untracked
membership is not pinned.

## Findings

### R1-F001 — `tia` import/namespace boundary and focused command are unspecified

Line 9 owns only `tools/ci/tia/snapshot.py` and its test, and line 55
reuses the plan's V(module) form
`uv run --project packages/aitm-usage --locked pytest -q tools/ci/tests/test_tia_snapshot.py`.
The design never states how the test imports the module, whether
`tools/ci/tia/` has an initializer, or what puts `tools/ci` on
`sys.path`. A bare `pytest` entry point run from the repository root
does not by itself make `tools/ci` importable for a `tia.snapshot`
import, so the stated red/green command is not shown to exercise the
owned module.

This also affects independent implementation paths. #138 and #140 both
have no predecessor and both add files under `tools/ci/tia/`. Neither
owns `tools/ci/tia/__init__.py`. The paired #138 revision specifies an
implicit `tia` namespace with no initializer,
`PYTHONPATH="$PWD/tools/ci"` and `python -m pytest` for focused tests.
If #140 lands first with an initializer, or with a different import
root, it either exceeds its owned paths or creates a conflicting
package boundary for #138 and for later leaves (T04 must treat
namespace packages carefully).

### R1-F002 — Delivery row does not state that #103 gives no execution or coverage evidence for the new module

Line 55 correctly says the default #103 job does not collect the new
test. At pinned trunk the helper lane runs only `test_python_gate.py`,
`test_pytest_evidence.py`, `test_verify_pr.py` and `test_file_checks.py`,
and `python_gate._line_totals` sums only `policy["helpers"]`
(`python_gate.py`, `pytest_evidence.py`, `verify_pr.py`,
`file_checks.py`). A controlled locked run showed a new unmeasured
`tools/ci/tia/` file leaves the helper counts at 778/821. #103 applies
its 90% floor to "first-party executable CI policy helpers".

The row still lists "the required exact-candidate #103 checks" beside
the focused run without saying what they do and do not prove. A reader
can take a green #103 run as evidence that `snapshot.py` was executed
or covered; it is neither. The row also asks for "the existing
gate-defining path disposition for additions under `tools/ci/`"
without saying whether such an addition is a gate-defining change under
#103 line 21 (it does not alter `policy["helpers"]`, coverage roots,
exclusions or the explicit test list), or confirming that #140 must not
edit the helper policy or the workflow test list (both gate-defining
and outside owned paths). T10's disposition mechanism is downstream of
#140 and cannot supply this approval.

### R1-F003 — Git configuration that changes the change record or untracked set is not pinned

Line 17 relies on "Git-detected renames", and line 35 defaults to "all
nonignored untracked files". Both depend on ambient Git configuration:

- Rename pairing depends on `diff.renames`, the similarity threshold
  and `diff.renameLimit`. Above the limit Git silently degrades to
  delete/add with only a warning. The same tree pair can then yield
  different change records and different canonical SHA-256 digests on
  different hosts or users, contrary to the "stable sorted change
  record" claim and to downstream use of snapshot identity in
  `Selection` and T10.
- Untracked membership depends on `core.excludesFile` (a user-global
  ignore file) and `.git/info/exclude`. A personal global ignore can
  silently drop a relevant untracked input from the local after
  endpoint with no uncertainty.
- Diff drivers or text conversion (`diff.external`, textconv) and
  `core.fsmonitor`/untracked-cache state can alter output or execute a
  configured program during supposedly read-only observation.

Line 37 already hashes tracked content regardless of status, which
neutralises stale-status risk for tracked files, but not the rename,
ignore-source or driver effects. Lines 43–45 require read-only raw
output and disable index writes and implicit fetch; they do not pin
these options.

## Required changes

1. **R1-F001.** State the `tia` import boundary: `tools/ci/tia/` is an
   implicit namespace package with no initializer, the test imports
   `tia.snapshot`, and #140 creates no `__init__.py`. Replace the
   focused command with one that establishes the import root, aligned
   with the paired #138 revision, for example
   `PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_snapshot.py`
   from the repository root. Note that this refines the plan's
   V(module) form only to make the module importable, and require the
   red step to fail on the missing behavior rather than on an import
   error.
2. **R1-F002.** Rewrite the delivery row to say that the exact-head
   #103 checks are recorded separately and only show that existing
   gates still pass; they do not collect `test_tia_snapshot.py` and do
   not measure `snapshot.py` (helper counts stay at the policy
   denominator, 778/821 at the pinned trunk). The focused run is the
   only test evidence for the module. State the focused coverage
   expectation for `snapshot.py`, or explicitly make no coverage claim.
   State that #140 does not edit the helper policy, coverage roots or
   workflow test list. Replace "obtain the existing gate-defining path
   disposition" with a JIT check: confirm against the trusted
   gate-defining path set whether a new unwired `tools/ci/tia/` file is
   gate-defining. If it is, obtain #103's existing owner disposition
   and independent review. Do not rely on T10.
3. **R1-F003.** Require every Git call to run with explicit,
   configuration-independent options: fixed rename detection mode and
   threshold (or no rename detection, retaining add/delete pairs), with
   a rename-limit warning or truncation treated as uncertainty;
   `--no-ext-diff` and `--no-textconv`; and isolation from global or
   system configuration and from fsmonitor/untracked-cache hooks, or
   record the effective values in the snapshot identity. Define the
   ignore sources used for "nonignored untracked" (for example,
   repository `.gitignore` files only) and record them, or treat an
   ignore source outside the repository as unresolved scope. Add one
   acceptance assertion that a conflicting global rename or exclude
   setting does not change the change record or untracked membership.

## Optional suggestions

1. State how a gitlink (mode `160000`) or other non-blob tree entry in
   the hosted diff is handled. It should be uncertainty unless trusted
   policy classifies it, since its content cannot be read by identity
   from this repository.
2. The 3h estimate covers hosted resolution, three local layers,
   no-follow reads, drift re-observation, replacement refs and
   canonical serialization. Consider naming which hour carries the
   canonical JSON and digest work, so JIT can tell early if the leaf
   approaches four hours.

## Decision

revisions-requested
