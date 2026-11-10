# #139 independent source review · PR #197 · round 1

| Review field | Value |
| --- | --- |
| Reviewer | `codex-collaboration:/root/review139` |
| Author | `codex-collaboration:/root/impl139` |
| Execution | Isolated declared-manual Codex SPR. Model and effort inherited from the parent session. The reviewer has no separate provider attestation. |
| Repository and PR | [`kburson/aitm` PR #197](https://github.com/kburson/aitm/pull/197) |
| Target | Literal `trunk` at `49865245d175ce6c52913738f2c9a42c0abea632`, tree `9737a9685e928c57e922cc8a68343ae195b9bacf` |
| Reviewed candidate | `codex/aitm-139-inventory` at `6687ba0262df6eb99e76c66509bf32262017d5b5`, tree `ffc00d32b1fa7d9a91c986958a86d19dabc41dfe` |
| Worktree | `<isolated review worktree>`. Detached and clean before and after inspection and tests. |
| Terminal decision | **Changes requested** |

## Inputs and source read

Read the full accepted #139 design, implementation Plan, JIT, and the
independent planning verdict at `b62000a647dccd1343573deaddf436ca179a5177`.
Read the complete #182 target refresh and its independent acceptance at
`fe9daf927f2b07596e49a4ae9c3bc708951af010` and the accepted parent #133
T02 section at `dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84`.

Read all 1,401 changed physical lines. The single additive diff hunk per
file contains its entire source and uses the physical new-side line
numbers below. Confirmed the exact head, tree, immediate parent, Git
blob identities and clean `git diff --check`.

| File | Complete new-side lines | Git blob |
| --- | --- | --- |
| `tools/ci/tia/inventory.py` | 1–645 | `eef193ec3adbbe10df89ae9d06cfd85605221060` |
| `tools/ci/tia/suites.json` | 1–307 | `a00888bb1515f4effbdb3700f2ac378d70928bb8` |
| `tools/ci/tests/test_tia_inventory.py` | 1–449 | `1d92bcbc83c71440f4c80042cde94c958f234a1d` |

## Findings

### [P2] Reject an unterminated pytest parameter suffix

New-side [`tools/ci/tia/inventory.py:152`](https://github.com/kburson/aitm/blob/6687ba0262df6eb99e76c66509bf32262017d5b5/tools/ci/tia/inventory.py#L152).

Adding the collected item
`packages/aitm-usage/tests/test_service.py::test_review_probe[missing-final-bracket`
to a valid product component returns an inventory containing that exact
impossible pytest ID. The classifier drops the suffix for the selector
and never checks its framing. The locked pytest producer constructs a
parametrized function name with an outer closing `]`. A malformed or
truncated normalized row can therefore become an execution obligation
with a valid reviewed isolation group. Validate the outer closing
delimiter when a parameter suffix begins and retain its opaque interior
exactly, including embedded brackets and slashes. Add a refusal case at
the public call.

### [P3] Validate Git ref syntax in a hosted snapshot binding

New-side [`tools/ci/tia/inventory.py:428`](https://github.com/kburson/aitm/blob/6687ba0262df6eb99e76c66509bf32262017d5b5/tools/ci/tia/inventory.py#L428).

Passing `refs/pull/139/merge..bad`, `refs/pull/139/a b`,
`refs/pull/139/.hidden` or `refs/pull/139/base.lock` in both the
synthetic hosted envelope and component binding emits that malformed
ref as part of hosted identity. The generic repository-path check
accepts all four, and read-only `git check-ref-format` refuses each.
An offline format check would preserve strict provenance shape and
leave proof authentication with T07/T08. The actual authenticated
PR ref is unaffected.

### [P3] Cross-check the reviewed child labels with their specific nodes

New-side [`tools/ci/tia/inventory.py:388`](https://github.com/kburson/aitm/blob/6687ba0262df6eb99e76c66509bf32262017d5b5/tools/ci/tia/inventory.py#L388).

The checked-in policy has the approved mapping. With the same #103
policy bytes, transpose `required_children` between the two approved
suite overrides. The aggregate label, profile, and mandatory checks
accept the inconsistent pairing and project `service-one-shot` on the
CLI help node and `cli-help` on the service node. Tie the two existing
labels to their exact reviewed selectors during compatibility validation
or document the suite policy as the sole authority for associations
across independently reviewed versions.

## Verification

- In a private uv environment with uv 0.10.6, Python 3.13.9 and the
  locked dependencies, the focused inventory tests and the neighboring
  baseline and snapshot tests passed **116/116**. Ruff lint passed and
  all 15 CI Python files passed its format check.
- Private public-interface probes reproduced the three findings.
  The same checks refused bad observer, control, or receipt digests,
  an unknown platform scope or runner, an undeclared capability, a
  mismatched comparison role, and conflicting component tree, ref,
  run or attempt. The probe log SHA-256 is
  `97b9854d7a6a686cea0382ac9df5cc73b239e02c70a28aa256c1373c2dffa3fc`.
- Independently ran both exact-head collect-only lanes in the same clean
  worktree using the delivered observer. Both exited 0 with zero
  deselections, phase records and child records. The exact sorted ID
  digests match the reconciled 867-ID product/CLI
  `ee3b88c58ceb7607aebf994226ef05a2d11b537b4d2d7cd23029b336368ade5d`
  and 182-ID helper
  `69cef362f4c87ba65846443eda6a2c8ae3dca3431f76905dcefc459c1e7200a4`
  scopes. Their 1,049-ID union has digest
  `4fabf61d809759b974e488a31ac94313db3cdeb409ff98416efa16243cb6af37`.
- Read the implementer's exact-head local validation receipt
  SHA-256 `8f88e434c0a4a37220dc0528598b3f5277234370fd096d60c436923a9c1197a2`,
  which records 1,165 passing tests, and the separate sanitized
  reconciliation SHA-256
  `8345f3e19afb38aff144b08e4ed7bd8dc0b95d8e1edd71fce40ea859fafa487a`.
  The latter retains 592 historical base, two separately bound 630-ID
  product/CLI roles, 182 advisory helper IDs and the updated 867-ID
  push reference. The two 630-ID roles share their exact ID digest and
  retain distinct inventory identities.
- Read the coordinator's authenticated same-attempt hosted and raw replay
  receipt SHA-256
  `3a6864eed09872746ac023a511d4bd18d55c5887a2e4ed76ffdd126a3dda53b1`.
  [Run 42915266772 attempt 1](https://github.com/kburson/aitm/actions/runs/42915266772/attempts/1)
  reports successful `python-base`, `python`, `quality`, `file-checks`,
  `collect-evidence` and `aitm-ci`. The tested merge commit
  `33270fd195b5ff98323db7619fc4abf255527ef4` has the candidate tree
  listed above. Raw replay records 867 candidate and 866 base tests,
  zero failures, and exact product 9,638/10,538 and helper 778/821
  coverage lines. The signed subject digest is
  `95634e6d23a0c04c3d89cb784ce8da5be49911b0e66ae80f6db34438b0fc52d2`.

## Boundaries and decision

The three additive files are the entire candidate delta. Both new
#182 modules are explicit integration modules in `native-process-state`.
The eight existing #103 workflow, policy, observer, Python gate,
trusted verifier, file checks, package manifest and lock blobs are
byte-identical to the exact parent. The three new files are still
classified as changed gate controls by `tools/ci/verify_pr.py:489`.
The existing separate owner disposition and trusted-target verification
remain applicable. This review has no disposition or merge authority.

Set aside hosted TIA proof qualification and authentication, which the
accepted contract assigns to T07/T08. Set aside selection, sharding,
hosted helper per-node outcomes, and the #158 merge fence, which the
accepted leaf excludes.

**Changes requested on exact head
`6687ba0262df6eb99e76c66509bf32262017d5b5`.** The P2 refusal must be
corrected before source acceptance. A revised candidate requires its own
exact validation and review.

Signed `codex-collaboration:/root/review139` for the exact base, head
and tree above.

Private signed original SHA-256 `a262aec3f14cc303a7fe30be7f6fdf6b91966e081634a9cf8bf3a948a9d2018a`. Local paths were sanitized for publication.
