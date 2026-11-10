# AITM #138 · Pin the serial baseline

**Refinement proposal** · T01 · **2.5 implementation agent-hours · S · P1**
· No predecessor · Direct successor [#139](../../139/story.md).

As an AITM contributor, I want an exact, reproducible record of the existing
serial CI inventory, outcomes, coverage, and timing so I can compare later
test selection and sharding against the same verified workload.

This leaf derives from the [accepted #133 design](../../133/design/test-impact-analysis-design.md),
SHA-256 `2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928`,
and [accepted plan, T01](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L172),
plan SHA-256 `ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7`,
section SHA-256 `116458afe27d4ab862a97146e04d72bbf6be8f13dc63b491adb1569f3aa8361e`.
The [#103 CI contract](../../103/design/github-ci-quality-gates-design.md)
governs input verification.

## Exact reference and custody

- **PR comparison.** Use PR [#179](https://github.com/kburson/aitm/pull/179),
  [run 42869601092 attempt 1](https://github.com/kburson/aitm/actions/runs/42869601092/attempts/1).
  Base `9b12927da1a368f254537277f7fdc7139f90cc44`, head
  `ddf87559f352a1f62f947b683e512d68348a1ecc`, synthetic merge
  `2b5208ebca881bc1b383f71af0e8e9355b4839bc`, tree
  `c1c9bc00e7845278b805d4f2828de3663a79c18e`. Use the retained passing
  [#103 verifier and independent delivery record](../../115/plan/delivery-checklist.md#snapshot-repair-review-checkpoint)
  from before merge. That receipt and the exact six jobs establish the PR
  role. Require all four same-attempt archives listed below. Match base
  identity and signed inventory/base digests to the raw records. The signed
  subject SHA-256 is
  `28d8102a38ca8c130e8c5c5f95eeea8a2d34d648d7fef96367e58c09c68811e2`.
  Keep the exact trusted PR base outcomes as a separate role within that
  attempt. A fresh PR reference would require the delivered verifier from
  the current trusted target and a complete current attempt.
- **Trunk comparison.** Use the delivered trunk commit
  `37a22922f072e39c35434ae645a1c20692b8da01`, with the same tree and
  ordered parents, from
  [run 42871778928 attempt 1](https://github.com/kburson/aitm/actions/runs/42871778928/attempts/1).
  Establish the push event, exact trunk commit/tree, canonical workflow
  and GitHub Actions check suite, and successful `python`, `quality`,
  `file-checks` and `collect-evidence` jobs for that attempt. Push mode
  deliberately skips the PR base and signer jobs. Bind the Python archive
  below and independently replay the trusted #103 push gate on its raw
  inputs. Keep the push proof separate from the PR proof even when their
  trees match.
- Each role records repository ID, event/ref, exact commit/tree and
  applicable base/head, canonical workflow, run/attempt, authenticated
  job and archive identities, policy, gate, observer, verifier,
  configuration and lock identities, and runner capability/toolchain.
  The observed controls match the parent plan's inspected source. Pin
  Python 3.13.9, uv 0.10.6, macOS-26 Darwin/APFS, actual image
  `macos26:20261102.0473.1` and Xcode 26.6 build 17F113 for these
  observations. At JIT reread archive custody and the current delivery base,
  controls, runner and toolchain. Keep the historical identities frozen.

| Role and archive | Artifact ID | Archive SHA-256 |
| --- | --- | --- |
| PR base | `13789881233` | `ef902445d3fa71f9b35f9e2417e69a6f0b841a2bce6e8312b227b87ea593fde2` |
| PR Python | `13788603444` | `927e1113fc7b02dfafb587c43e71490448c0d24781bc366fbad9dec242415f78` |
| PR collector | `13788903030` | `70f2df3db8aa241cae9f7f98ef79a70e8acf18563085ae53e57672d16b7293a4` |
| PR signed | `13790255902` | `3ab42fd5de5735616dc4c500e85ce933159ddd373f576effc9296f1449d8d264` |
| Push Python | `13788584397` | `aab36e6826ad136601408cbfc6f830513cbd9f8b201986997a8d5c356e8cd631` |

Authenticated GitHub metadata reports the push archive created at
`2026-11-10T18:08:33Z`, attached to run `42871778928` on the delivered
commit and named `aitm-ci-python-a1`. Both the attempt-specific job list
and archive naming bind attempt 1. Use the owning run, attempt, name and
digest for custody. Numeric ordering carries no custody evidence.

## Baseline contract

`build_baseline(verified_ci103, timings) -> Baseline` is a deterministic
projection of closure-owner-supplied proof. The closure owner uses the
retained passing `tools/ci/verify_pr.py` result for the historical PR and
replays `tools/ci/python_gate.py` in push mode using the protected,
exact historical controls and authenticated push inputs. The projection
receives those results and proof envelopes. It checks their binding and
completeness and has no GitHub credentials or network access of its own.

At trust boundaries use canonical JSON envelopes `aitm.tia-ci103-input/v1`
and `aitm.tia-baseline-timings/v1`, with evidence roles and custody
identities. Reject duplicate JSON keys before decoding into maps,
unsupported envelope or receipt schemas, and absolute, aliased or
escaping source, archive-entry and coverage paths before use. Support
only the declared #103 shapes for raw embedded receipts.

Emit canonical `aitm.tia-baseline/v1`. Preserve the exact role bindings,
source and test inventories and their digests, classified product outcomes,
helper collection provenance, coverage scope and counts, child/wheel/file
proof, and timing observations with units and boundaries. #139 consumes
source/test identities, ownership, role and platform bindings, and the
helper collection provenance for reconciliation. T35 consumes the timing
roles, boundaries and matching runner/control/cache identities.

Use the #103 observer for product test node IDs and outcomes, including the
candidate-only CLI evidence test, and retain the distinct trusted PR-base
inventory and outcome comparison. The historical hosted helper lane ran
four explicit test targets and recorded coverage and job success. It did
not record helper node IDs or per-node outcomes. The `python-base` job
ran product tests only, so it has no helper test obligations.

Pin the helper test node inventory from controlled collection of those
four exact workflow targets from the shared PR-tested and trunk tree.
Use its lock, Python 3.13.9 and the exact #103 observer with pytest
`--collect-only`. Retain the sorted unique IDs, evidence digest, tree,
command, lock and runner scope as a **local advisory collection**, separate
from hosted results. Refinement reproduced 182 unique IDs with no
deselections, sorted compact JSON-array SHA-256
`69cef362f4c87ba65846443eda6a2c8ae3dca3431f76905dcefc459c1e7200a4`.
#139 reconciles helper ownership and obligations against this exact-tree
collection and keeps its advisory classification. It cannot use it as a
hosted `CollectionProof` or infer historical per-node outcomes. A missing
or discrepant required helper collection blocks #138 acceptance and #139
pickup pending reassessment.

Keep raw line and available branch coverage evidence for both scopes,
including coverage digests and covered/executable counts, the two normally
exiting child receipts (`cli-help`, `service-one-shot`) and the exact
installed-wheel smoke and file-lane receipts. The current pair records 630
candidate and trunk package/CLI outcomes, 592 PR-base outcomes, 22 product
source files, 7,146/7,825 product and 778/821 helper lines. Validate the
unrounded 90% floors through #103. Keep the detailed authenticated inputs
in existing custody and publish safe links, digests, scope, counts,
timings and verification limits in the sanitized report.

The record is for historical comparison and downstream inventory work.
#103 remains the PR gate. T01 has no authority to emit a future
`FullProof`, qualify an observer or a scheduled run, authorize a merge
or trigger Stop the Line.

## Timing

For each retained observation store the exact evidence role, commit/tree,
workflow/run/attempt, runner capability, lane and timer boundaries, and
cache profile and observed hit/miss with provenance. Cold means no
restored dependency cache. Warm means a verified hit on the approved
primed lock/image/key. Distinguish an intended profile from the observed
result. The candidate's cache profile never inherits the uncached
`python-base` job's setup. Compare matching role, workload, controls,
lock and runner scope and keep unlike observations labeled separately.

| Verified role | Observed dependency cache | Python evidence setup / test bucket / lane total | Python runner | Python start after event |
| --- | --- | --- | --- | --- |
| #179 PR candidate | Warm hit | 5 / 181 / 187 s | 205 s | 305 s |
| Exact trunk push | Warm hit | 3 / 111 / 115 s | 127 s | 3 s |
| Exact comparable cold samples | Unknown | Unknown | Unknown | Unknown |

The `test` bucket includes the serial package and helper work and
intervening coverage/tool setup. The lane total also includes wheel smoke.
Python start after event uses attempt-specific job start minus run creation.
Neither attempt observed the comparable cold profile. Reassess at JIT if
an additional cold experiment is required within the leaf budget.
Record queue, setup, test execution, collector duration or latency, total
feedback, and hosted runner consumption separately using their observed
boundaries. Sum non-skipped job durations for runner consumption and keep
that apart from wall time and billed cost. Unit/integration splits, finer
test-only boundaries, unmatched cache keys and billing remain Unknown
when absent. A valid `Unknown` includes its role, scope and reason. It
is distinct from zero and from a verified empty scope. These two warm
observations establish neither a cold comparison nor the later
qualification windows.

## Ownership and acceptance

- Proposed leaf document
  `.aitm/stories/001/138/design/pin-serial-baseline-design.md`.
  Source ownership is `tools/ci/tia/baseline.py` and
  `tools/ci/tests/test_tia_baseline.py`. Proposed sanitized report
  `.aitm/stories/001/138/attachments/serial-baseline.md` belongs to the
  story's planning evidence.
- #138 and [#140](../../140/story.md) can prepare independently from their
  own pinned source bases. #138 gets its own source branch and worktree at
  pickup. #140 owns `tools/ci/tia/snapshot.py` and
  `tools/ci/tests/test_tia_snapshot.py`. Neither leaf needs the other's
  source or proof. Use the implicit `tia` namespace without an initializer.
  Put the physical checkout's `tools/ci` on `PYTHONPATH` for the focused
  run and import `tia.baseline`. Neither leaf owns a common package file.
- Shared workflow, verifier and policy changes are outside T01. The raw
  CI coverage collector scans `tools/ci`, but the #103 gate sums only the
  explicit `policy["helpers"]` files through `python_gate._line_totals`.
  The four pinned helpers exclude `tools/ci/tia/**`, so the new uncollected
  module does not increase the current gate denominator. Confirm this at
  JIT and the exact head. Keep the unchanged #103 floor and attach separate
  focused evidence for the new code. A drifted scope or failed required
  floor blocks delivery and returns to planning or the existing policy
  authority for disposition. #103's verifier still classifies additions
  under `tools/ci/` as gate-defining paths. Obtain the required exact-tree
  owner disposition and independent review through the existing procedure.
- Acceptance requires an exact historical pair with both proof roles,
  raw replay matching the verified scopes, complete attempt custody and a
  sanitized report that can be reconciled to its inputs. Each cold/warm
  slot carries a matching observation or an explicit `Unknown`.
- Refuse mismatched repository, role, ref, base/head/tested tree, policy,
  lock, runner scope, run/attempt, conflicting or duplicate identifiers
  or digests, missing/expired evidence without verifiable retained custody,
  and missing, failed, unexpectedly skipped or cancelled required evidence.
  Reject supplied cross-attempt artifacts or timings, including a plausible
  base or shard from a different attempt. A missing measurement can be
  Unknown. It cannot fill a missing proof.
- Start implementation verification with a failing
  `test_baseline_rejects_mixed_attempts`. Then pass the positive exact-pair
  and refusal cases with `V(baseline)`, using
  `PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_baseline.py`
  from the physical checkout root. Retain exact-head command, tree,
  runtime, collected node IDs and red/green results in the story's
  delivery evidence. The current #103 job does not collect the new leaf
  test by default. Complete exact-head #103 validation separately.
- Keep **2.5h / S / P1**. The authenticated readback and available raw
  archive custody keep the work to one small projection, focused tests,
  and one report. Budget 0.5h for custody and exact identity readback,
  0.75h for projection, 0.75h for focused behavior tests and verification,
  and 0.5h for the report. P1 reflects the direct #139 inventory
  prerequisite. Hosted queue and review wait are separate. Reassess at JIT
  if retained proof is unavailable or the work needs an additional live
  experiment. Leaf design acceptance, own plan, JIT and implementation
  authorization are separate checkpoints.
