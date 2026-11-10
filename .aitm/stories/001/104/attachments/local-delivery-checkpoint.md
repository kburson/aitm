# #104 local delivery checkpoint · November 9, 2026

The independently reviewed [fresh delivery JIT](../plan/delivery-jit.md) admits local preparation under the owner's Full-Auto instruction. The [one authorized signing probe](github-signing-probe-result.md) passed. Production CI remains held by the accepted authority and preflight requirements. #104 and #103 remain in Planning.

## Reviewable local candidate

The isolated story branch is `codex/aitm-104-ci-bootstrap`. Its local head is `b7cf622baafcf8600fc0fff9d4ce2f4838f7daa7`, tree `fa55092e942b4f45c0ad404948fa0dc6fb6e19e1`, and production workflow blob `10a06180936fa5d575b00c093d7e0b203549dbdc`. The source is committed locally. Draft PR #107 still points to the signed diagnostic head `6f428770c41352fa0de8935a882fa10317ce6039`. Trunk is pinned at `f80f22645e2008c4cac9dc6e4003640bba976b5f`.

The prepared CI1 candidate adds the serial qualified macOS baseline and candidate tests, locked wheel and quality checks, a single fail-closed gate, and the isolated ordinary-PR v2 signing job. It pins the bootstrap observer `839b73cdcc1e44f45af78bcebdbf53e9adfeee67` and policy `b93942fb31a999702ed1c2ad14035b1a5a1d22a4` only at the original base. The local source review addressed all six findings on consistent test identities, full tracked coverage denominator, exact trusted base policy, limited bootstrap fallback, child receipt binding and signed checkout evidence. [Local review and final addendum](../plan/local-source-review.md).

## Local verification

- The isolated exact trunk baseline passed 530 tests. The candidate passed 531 product tests, including the normal CLI help subprocess. The full baseline inventory joined to the candidate under the shipped policy. Both normally exiting child PIDs matched nonempty product coverage shards before combine.
- Product line coverage was **6,285 of 6,910 (90.955%)**. Executable helper line coverage was **248 of 270 (91.852%)** with 49 behavioral helper tests passing. Branch coverage was recorded separately. The full local gate returned success with no failures.
- Ruff lint and format checks, actionlint and embedded shell syntax passed. The locked wheel built, its digest was verified before installation without dependency resolution, and its import and CLI help worked in a clean environment.
- The local workflow fixture executed the actual checkout and artifact-custody guard, v2 assembly and raw signer-input validation with the real local gate evidence and controlled GitHub API fixtures. It accepted the correct inputs and refused the wrong base checkout, stale archive name and wrong signer attempt. The fixture did not call the signing action.
- One earlier local run failed an unchanged service test on a token-count assertion. Exact-base repetitions and the fresh full serial rerun passed. The initial failure and its unproven cause remain recorded separately.

## Remaining authority and delivery

The accepted binding amendment requires a separate explicit production grant for recurring public signing permissions and publication of sanitized evidence subject digests and signing metadata. The existing explicit grant applies to one diagnostic. The reviewed local JIT also records the absent first production gate and claims no pre-Develop exception. The requested scoped exception would permit #104 to enter Develop before the first real CI result exists, with passing exact hosted CI and independent source review still required before merge.

After both authorities are recorded, recheck the current base and PR, refresh pickup as necessary, and run the actual hosted negative and corrected gate evidence. Verify the delivered trunk tree and controlled integration proof, sign off and close #104 immediately, then follow the reviewed [#105 plan](../../105/plan/implementation-plan.md) and [#106 plan](../../106/plan/implementation-plan.md). Their development remains gated by verified predecessor delivery. #100 follows #103 closure.
