# #139 independent source review · PR #197 · #202 target refresh

| Review field | Value |
| --- | --- |
| Reviewer | `codex-collaboration:/root/review139` |
| Author | `codex-collaboration:/root` for the exact target refresh. The previous classifier correction was authored by `codex-collaboration:/root/impl139`. |
| Execution | Isolated declared-manual Codex SPR. Reviewer model and effort inherited from the parent session. |
| PR | [`kburson/aitm` PR #197](https://github.com/kburson/aitm/pull/197) |
| Target | Literal `trunk` at `1282538954dc5a7e7f7b27da4e3ab096892e3add`, tree `906680801e3f6d0a121248fe20fb4c80397478aa` |
| Reviewed head | `a5fdd76f7e682e2a9ff547db900a9c82ac502fc1`, tree `7709cca894edba3e40e4b193a091e3077e4d5534` |
| Reviewed checkout | `isolated source review worktree`, detached and clean at the exact head. |

## Source and scope

The accepted design, Plan and JIT at
`b62000a647dccd1343573deaddf436ca179a5177`, #182 delta at
`fe9daf927f2b07596e49a4ae9c3bc708951af010`, and accepted journal
delta at `d86b891fa1304f1e80100a9ce6455697c5a8010d` remain the
scope basis. The earlier exact-source verdict for head
`a2b52e4367325f1638102dba6709933e1634d262` is preserved in
planning commit `65ac1393c8d8ea0f00bedc3e8d667c7178336526`.

The candidate directly merges that previously reviewed head and the
new literal target. The target-to-candidate diff passes
`git diff --check` and adds only the three owned files. I read their
complete source in the earlier reviews and verified that the three
candidate blobs are byte-identical to the previous accepted head.

| File | Complete new-side lines | Git blob |
| --- | --- | --- |
| `tools/ci/tia/inventory.py` | 1–670 | `2f542dcdb9e6518c637d445fce673377d3dd34af` |
| `tools/ci/suites.json` | 1–317 | `e0d88968b23412c0f5594149d87e643554a0e9af` |
| `tools/ci/tests/test_tia_inventory.py` | 1–512 | `fbe0e5e91472c15e36eb15ddf2e5c156902c8f7d` |

#202 merged through PR #207. The change from the former to the current
target modifies only `_monitor_journal_store.py`, `monitor_journal.py`,
`test_monitor_journal.py`, and `test_monitor_journal_store.py` within
`packages/aitm-usage/`. Both changed test modules match the existing
[`suites.json:165–174`](https://github.com/kburson/aitm/blob/a5fdd76f7e682e2a9ff547db900a9c82ac502fc1/tools/ci/tia/suites.json#L165-L174)
exact rules. The new journal cases use the existing native/Claude
capture, ledger and registry writer fixtures for durable dispute
behavior. The new journal-store cases use the existing SQLite and
registry writer fixtures for transaction, migration and table custody
behavior. Both remain `aitm-usage` integration tests in
`native-process-state` under the accepted rule.

The workflow, #103 policy, observer, Python gate, trusted verifier,
file checks, Python manifest and lock blobs are byte-identical across
both target trees and the candidate. The existing
[`tools/ci/` rule](https://github.com/kburson/aitm/blob/1282538954dc5a7e7f7b27da4e3ab096892e3add/tools/ci/verify_pr.py#L491)
still classifies the three additions as changed gate controls.

## Independent validation

- Ran all 47 focused inventory tests on the exact candidate using
  locked Python 3.13.9 dependencies. All passed. Ruff check and
  format check passed. The checkout was clean before and after
  collection, projection and testing.
- Ran both exact-head observer lanes in private scratch. They
  reproduced the same 996 unique product/CLI IDs and 182 unique
  helpers as the two frozen observations on the literal target.
  Both collect-only lanes completed with zero deselections, phase
  reports or child records. The preceding 970-ID product set has
  26 additions and zero removals. Ten additions are in the journal
  module and 16 in the journal-store module. The 182 helper IDs are
  identical to the pinned advisory helper set.
- Independently projected the two target observations with the
  exact candidate classifier and policy, the matching before/after
  T03 snapshot
  `f8eca962d779a4c196e4ed2d57ce6f2791eff1c182f1923b9939b4d8010a169b`,
  and the existing scope metadata. All 34 journal and 57
  journal-store IDs retained the approved ownership, profile,
  platform scope, suite and isolation group. The full advisory
  workload has 1,178 obligations, with sorted-node-array digest
  `d54705c680c8c875cb276f5fc6312bdf1fad11ba768887ff1fff510f3e68e595`.
  Its product/CLI node-array digest is
  `c47bc7d715eb65a709ebcae1c18018baad064ac8608e1210dc95ee587ba19f7e`.
  The helper node-array digest remains
  `69cef362f4c87ba65846443eda6a2c8ae3dca3431f76905dcefc459c1e7200a4`.
  Independent probe log SHA-256
  `8b9752241f4ce0b3e350f24194d95973f07f4a8584157202a0b834096c14319b`.
- Read the replacement reconciliation SHA-256
  `c137dc0d570d64134715d7b9811e0a77d8d4631f88194bf7aab46505a156da5e`.
  The independently projected advisory inventory matched its SHA-256
  `8f1d0ccd24c9df907135d0e3f699b6a551616f37a3aead20e734ac7051d7d8e5`
  and totals of 1,171 integration, three system and four unit
  obligations. The reconciliation binds the exact matching 996
  product IDs and original outcomes to [trunk push 42945628106
  attempt 1](https://github.com/kburson/aitm/actions/runs/42945628106/attempts/1),
  artifact 13823420424. The helper set remains an advisory
  collection with its own provenance.
- Read the replacement exact-head full local receipt SHA-256
  `d3800ed5f716bff2532e1c22cabb219f4437d75b8253b8859c5dc6d6bffd0fc2`.
  It binds the reviewed base, head, tree and reconciled inventory
  and records 1,312 passed with zero failures. The retained full
  log hashes to the receipt's
  `66d2c23ed8f51eca9616879b8a3779df51d5212938cbed5115327361da127aa7`.
- Read the coordinator's authenticated exact-attempt hosted and raw
  replay receipt SHA-256
  `8601c34aae39c35db8727f5c6d09bbc77725283a1708cdd7ac9e91d02f2a1619`.
  [Run 42945914184 attempt 1](https://github.com/kburson/aitm/actions/runs/42945914184/attempts/1)
  passed `python-base`, `python`, `quality`, `file-checks`,
  `collect-evidence` and `aitm-ci`. Tested merge commit
  `1b7fb25bf73ab3a74161e723433264673cf95bd3` binds the reviewed
  tree. Raw replay verified 996 candidate and 995 base outcomes,
  zero failures, 10,461/11,407 covered product lines and 778/821
  covered helper lines. The signed subject digest is
  `6431d31552d912a5317c861aaf8a37ec6f92fad8d8a525f23b5ddd4d6c964fea`.

## Findings and decision

No new findings. The original three findings remain resolved in the
unchanged classifier and tests. **Source review accepted** for the
exact target, head and tested tree above.

The trusted-target verifier returned a separate #103 gate-control
hold, receipt SHA-256
`30ba04305b0a885f5fbdb2ef8505e3e03d353a1ee56ad5cf482dc00da3fbdb7e`.
Delivery requires the first owner disposition for tested tree
`7709cca894edba3e40e4b193a091e3077e4d5534` and a trusted-target
verification pass. Any base or candidate change requires fresh
exact evidence.

Signed `codex-collaboration:/root/review139` for the exact base, head
and tree above.

Original review SHA-256 `15e03dc8b2b367204848354e7bf1376bdec10953706a725f4b342529ec65ec94`. The published copy omits the local checkout path.
