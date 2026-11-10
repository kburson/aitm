# #139 independent source re-review · PR #197 · round 2

| Review field | Value |
| --- | --- |
| Reviewer | `codex-collaboration:/root/review139` |
| Author | `codex-collaboration:/root/impl139` |
| Execution | Isolated declared-manual Codex SPR. Reviewer model and effort inherited from the parent session. |
| Repository and PR | [`kburson/aitm` PR #197](https://github.com/kburson/aitm/pull/197) |
| Target | Literal `trunk` at `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2`, tree `978272c4242736049ee6531b8afd9c8d3b329b9f` |
| Reviewed candidate | `codex/aitm-139-inventory` at `36f700e330c07dc8750dfcfa9fe8841c49e35877`, tree `13f338628918c14f41b56f0c1ef52649b126fc41` |
| Corrective commit | `ffed933cc343700e65a83bbebcaa344071c05308`, first parent of the candidate. The exact target is the candidate's second parent. |
| Worktree | `<isolated review worktree>`, detached at the exact head. |

## Source and scope

The accepted #139 design, Plan and JIT at
`b62000a647dccd1343573deaddf436ca179a5177`, accepted #182 update at
`fe9daf927f2b07596e49a4ae9c3bc708951af010`, and round-one source review
remain the specification and review basis. I previously read the full
three-file source at `6687ba0262df6eb99e76c66509bf32262017d5b5`.
For this round I read the complete correction, verified that the
candidate's three owned files are byte-identical to the corrective
commit, and verified that the suite policy is byte-identical to round
one. The source diff against the literal new target adds these three
files. The target-to-candidate diff check passed.

| File | New-side physical lines | Git blob |
| --- | --- | --- |
| `tools/ci/tia/inventory.py` | 1–670 | `2f542dcdb9e6518c637d445fce673377d3dd34af` |
| `tools/ci/tia/suites.json` | 1–307 | `a00888bb1515f4effbdb3700f2ac378d70928bb8` |
| `tools/ci/tests/test_tia_inventory.py` | 1–512 | `fbe0e5e91472c15e36eb15ddf2e5c156902c8f7d` |

#194 reached the target through PR #198. The old-to-new target diff
changes `packages/aitm-usage/src/aitm_usage/install.py` and the existing
test modules `test_install.py` and `test_monitor_ledger_version.py`.
Both test modules already have the accepted integration and
`native-process-state` rules. The existing workflow, policy, observer,
Python gate, trusted verifier, file checks, package manifest and lock
blobs are identical to the target. The #103 verifier's
[`tools/ci/` scope rule](https://github.com/kburson/aitm/blob/c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2/tools/ci/verify_pr.py#L491)
classifies the three additions as changed gate controls.

## Round-one findings resolved

- **P2, malformed pytest parameter suffix.**
  [`inventory.py:171–181`](https://github.com/kburson/aitm/blob/36f700e330c07dc8750dfcfa9fe8841c49e35877/tools/ci/tia/inventory.py#L171-L181)
  rejects a missing outer closing delimiter while leaving the suffix
  opaque. The public full-workload probe refused three unterminated
  variants and preserved five exact valid suffixes, including
  independent interior opening or closing brackets, slash, double
  colon, Unicode and an empty parameter display ID.
- **P3, malformed hosted ref.**
  [`inventory.py:156–168`](https://github.com/kburson/aitm/blob/36f700e330c07dc8750dfcfa9fe8841c49e35877/tools/ci/tia/inventory.py#L156-L168)
  and
  [`inventory.py:449–456`](https://github.com/kburson/aitm/blob/36f700e330c07dc8750dfcfa9fe8841c49e35877/tools/ci/tia/inventory.py#L449-L456)
  require a syntactically valid fully qualified ref. The public hosted
  binding agreed with `git check-ref-format` on 22 valid and invalid
  references, including the four reported in round one. Valid values
  survive exactly. T07/T08 retain proof authentication and
  qualification.
- **P3, child evidence binding.**
  [`inventory.py:411–425`](https://github.com/kburson/aitm/blob/36f700e330c07dc8750dfcfa9fe8841c49e35877/tools/ci/tia/inventory.py#L411-L425)
  requires both reviewed label-to-selector associations and equality
  with #103's required set. Independent public-call probes refused
  transposition, omission from both input policies, reassignment to
  another mandatory node, and duplication. The valid projection
  retains `cli-help` on the installed CLI test and
  `service-one-shot` on the one-shot service test.

No new findings.

## Independent verification

- Locked Python 3.13.9 and uv 0.10.6 ran **134 tests successfully**,
  including 47 focused inventory tests and 87 neighboring snapshot
  and baseline tests. Ruff lint and format checks passed. Independent
  public interface probe log SHA-256
  `d373d78810a6f9fba62ac612112f4163a93c1bb141a5f4361a2dd4720a6862bf`.
- Ran both collect-only lanes against the same clean candidate in the
  isolated worktree. They exited 0 with zero deselections, phase
  records or child records. The 877 unique product/CLI IDs exactly
  match the archived #194 target push's raw observer report. Relative
  to my round-one local IDs, 10 installer IDs were added and none were
  removed. The 182 helper IDs are an exact match to my round-one
  helper IDs. The resulting 1,059-ID union digest is
  `718cc4b4d252f269c33af57331735789b1586d1ea6b644ede92d4f6a14065085`.
- Read the refreshed reconciliation receipt SHA-256
  `528a6880c45194f68b564b7a7c6980030d5fffa3b5a1b0485828ec1dd05539f9`.
  It binds both collected components to one clean target snapshot,
  preserves the historical comparison roles, and records the
  1,059-obligation full advisory inventory SHA-256
  `014424d5c140c939f6ef19c9cd4c7b5a05cc25c979050aefe3ed77526f8f73f9`.
  The 877 product and 182 helper obligations classify as 1,052
  integration, three system and four unit cases. The collect-only
  inventory establishes no runtime outcomes or coverage.
- Read the implementer's exact-head local validation receipt SHA-256
  `1c41f5addacf3d1b393aee368d9ffede3dcf20df7f838abffc0678a395d8b523`.
  It binds the exact base, head, tree and three source digests above
  and records **1,193 passed** with zero failures in the full suite.
  It also retains correction red evidence, 47 green focused cases,
  87 neighboring cases, and green Ruff, file checks and actionlint.
- Read the coordinator's authenticated exact-attempt hosted and raw
  replay receipt SHA-256
  `096f0c6e85ad74d0e643cd4810a7b4bd7f07cb237c42c417e8a22901a6c0db2c`.
  [Run 42917875102 attempt 1](https://github.com/kburson/aitm/actions/runs/42917875102/attempts/1)
  passed all six canonical jobs. The exact tested merge commit
  `f237b347b2bb0c019d3367f36d22468714cc71d4` has the reviewed
  candidate tree. Raw replay shows 877 candidate and 876 base
  outcomes, zero failures, 9,649/10,549 covered product lines and
  778/821 covered helper lines. The signed subject digest is
  `7e7f56386706a7ddf43228f5d0ef6a246c9232dff832d3f4b47919b7f1f26fa4`.
  The six jobs are `python-base`, `python`, `quality`,
  `file-checks`, `collect-evidence`, and `aitm-ci`.

## Decision

**Source review accepted** for the exact target, head and tree above.
All three published round-one findings are resolved. The worktree was
clean at the exact candidate before and after review.

The coordinator's #103 trusted-target verifier remains on hold
pending the owner's separate exact-tree gate-control disposition.
Source acceptance supplies the independent review evidence for the
stated head. The existing owner disposition and trusted-target
verification govern delivery.

Hosted TIA proof qualification and authentication remain within
T07/T08. Selection, sharding, hosted helper per-node outcomes,
and the #158 merge fence are outside the accepted leaf.

Signed `codex-collaboration:/root/review139` for the exact base, head
and tree above.

Private signed original SHA-256 `7af37690838a9890a8cd9c11ff013e258a30852e849d9420a68e7c12a8c00caa`. Local paths were sanitized for publication.
