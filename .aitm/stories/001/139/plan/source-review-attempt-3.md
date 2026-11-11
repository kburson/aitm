# #139 independent source review · PR #197 · refreshed trunk

| Review field | Value |
| --- | --- |
| Reviewer | `codex-collaboration:/root/review139` |
| Author | `codex-collaboration:/root` for the two rule additions. The previous classifier correction was authored by `codex-collaboration:/root/impl139`. |
| Execution | Isolated declared-manual Codex SPR. Reviewer model and effort inherited from the parent session. |
| PR | [`kburson/aitm` PR #197](https://github.com/kburson/aitm/pull/197) |
| Target | Literal `trunk` at `5324a80bad7730b2bdb4a2b87acf00f7171305c0`, tree `d34be057faf72d4c157c0dbf4e43003ccf40612d` |
| Reviewed head | `a2b52e4367325f1638102dba6709933e1634d262`, tree `583a652fb4e1d9112c2f77401095b814f8c7e625` |
| Reviewed checkout | `isolated source review worktree`, detached and clean at the exact head. |

## Source review

The review applies the accepted design, Plan and JIT at
`b62000a647dccd1343573deaddf436ca179a5177`, the #182 delta at
`fe9daf927f2b07596e49a4ae9c3bc708951af010`, the prior source review
on `36f700e330c07dc8750dfcfa9fe8841c49e35877`, and the journal
delta at `d86b891fa1304f1e80100a9ce6455697c5a8010d`. The published
journal delta and its acceptance are byte-identical to the two
independently reviewed scratch documents.

The candidate's immediate parent `6d3b8766ff43d52d7fcc79ed51073ffecde0c63e`
joins the previously reviewed head and exact target. The merge base
of the candidate and target is the target. The target-to-candidate diff
adds only the three owned files and passes `git diff --check`.

| File | Complete new-side lines | Git blob |
| --- | --- | --- |
| `tools/ci/tia/inventory.py` | 1–670 | `2f542dcdb9e6518c637d445fce673377d3dd34af` |
| `tools/ci/suites.json` | 1–317 | `e0d88968b23412c0f5594149d87e643554a0e9af` |
| `tools/ci/tests/test_tia_inventory.py` | 1–512 | `fbe0e5e91472c15e36eb15ddf2e5c156902c8f7d` |

I read the complete source in earlier rounds and verified that the
classifier and test blobs are byte-identical to the previous accepted
head. The complete owned-path difference from that head is ten
additive lines in
[`suites.json:165–174`](https://github.com/kburson/aitm/blob/a2b52e4367325f1638102dba6709933e1634d262/tools/ci/tia/suites.json#L165-L174).
The two records apply the accepted `aitm-usage`, `integration`,
and `native-process-state` values to the exact journal and
journal-store module paths. The journal tests exercise actual capture
fixtures, ledger, registry writer and durable cursor/claim state.
The journal-store tests exercise actual SQLite WAL/sidecars,
transactions, migration, custody and registry writer behavior. The
existing adapter and scope rules cover the other added IDs. The
dashboard module remains outside the accepted workloads.

The existing workflow, policy, observer, Python gate, trusted
verifier, file checks, package manifest and lock blobs are
byte-identical to the literal target. The verifier's existing
[`tools/ci/` rule](https://github.com/kburson/aitm/blob/5324a80bad7730b2bdb4a2b87acf00f7171305c0/tools/ci/verify_pr.py#L491)
classifies all three additions as gate controls.

## Evidence

- The locked Python 3.13.9 and uv 0.10.6 run passed 134 focused
  and neighboring tests, including 47 inventory tests. Ruff check
  and format check passed. Independent exact-head observer runs
  reproduced 970 unique product/CLI IDs and 182 unique helper IDs
  with no deselections, phase records or children. The exact product
  IDs match the raw successful #201 trunk-push observer. The exact
  helpers match the separately pinned advisory helper reference.
  The sorted-node-array digest of the 1,152-ID union is
  `d76c1bb93037346516f64b79f8a48e834f678553cc852213da6f05caa2d040cb`.
- Independently replayed all six frozen normalized inputs through
  the exact candidate classifier and policy. Each projection matched
  the recorded inventory byte-for-byte, including both historical
  630-ID roles and their distinct identities. All 24 journal and
  41 journal-store IDs project to the exact approved owner, profile,
  scope, suite and isolation group. Removing either rule independently
  refuses the full input as an unclassified node. Probe log SHA-256
  `23d0737940186da0f5f64b74e938caa5f52c767bec5a6ccfb6f46ed275b9d10d`.
- Read the sanitized reconciliation SHA-256
  `b0d05440d13fb3783baed55201e3fcac129350368992bcdd726bc415a70c8b0d`.
  The shared before/after target snapshot is
  `ae49cc4f00ed734485b003ce3dbf2a717e37eadc553025209548bb5f9e376a58`.
  The classified advisory union has SHA-256
  `623b052fdcd0ceba7b201fc8eff93df341de2c1fa17138333d4f423526eecb89`,
  with 1,145 integration, three system and four unit obligations.
  Hosted outcomes and coverage remain with the hosted receipts.
- The #201 baseline application condition was satisfied by
  [exact trunk run 42940157251 attempt 2](https://github.com/kburson/aitm/actions/runs/42940157251/attempts/2).
  Rehashed the retained archive
  `ef3a59a38d63e895486445be261abb0d342770ec6e40bf83b654f608ee0060e3`
  and its raw pytest observer report
  `61029da1be74ac1786447aec2e6c38b0b00202db87d628dec309af73a3c92d0a`.
  The previous failed attempt remains separately recorded in planning.
- Read the published exact-head local validation receipt in planning
  commit `65416c1`, SHA-256
  `95f8a815d845656a09c364ac708e1716a8015e0afd1b2ba4b4a560b196d71e0b`.
  The receipt binds this target, head and tree and records 1,286 tests
  passed with zero failures. The rehashed full-run log SHA-256
  `f7215ed35ec1a27274f6782fee06bc8be2e45c1117bde414483d0a92ba7d722a`
  matches the receipt. The published reconciliation bytes also match
  the independently replayed reconciliation.
- Read the coordinator's authenticated exact-attempt hosted and raw
  replay receipt SHA-256
  `26aa001fc6f99a225de9cd75c153e6619dedcafc8caacad846eb42552300be45`.
  [Run 42944835329 attempt 1](https://github.com/kburson/aitm/actions/runs/42944835329/attempts/1)
  passed all six canonical jobs, `python-base`, `python`, `quality`,
  `file-checks`, `collect-evidence` and `aitm-ci`. The tested merge
  commit `dee2d17be88da7239bc9f81cd706e997fd9845c7` binds the
  reviewed tree. Raw replay verified 970 candidate and 969 base
  outcomes, zero failures, 10,360/11,301 covered product lines and
  778/821 covered helper lines. The signed subject digest is
  `a2d9f1051d3b711ba6ba5be27a85ae05e156abfe33ccfdbe8c4ff7310cec1522`.

## Findings and decision

No new findings. The three earlier findings remain resolved in the
unchanged classifier and its tests. **Source review accepted** for
the exact target, head and tree above.

The trusted-target verifier returned a #103 gate-control hold with
receipt SHA-256
`392e0cecc7c6ad330337d01726faca85ea12c0cedcd2ed6ea8d6b59e412049d4`.
The first owner disposition for tested tree
`583a652fb4e1d9112c2f77401095b814f8c7e625` remains pending.
Delivery requires that separate disposition and a trusted-target
verification pass. Any base or candidate change requires fresh
exact evidence.

Signed `codex-collaboration:/root/review139` for the exact base, head
and tree above.

Original review SHA-256 `1ec88aa5ae92da7dc517d64507ce82a9447891e9d4e5f36dda1983de08057801`. The published copy omits the local checkout path.
