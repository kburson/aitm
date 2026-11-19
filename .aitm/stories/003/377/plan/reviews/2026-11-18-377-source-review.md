# #377 independent source review

| PR | Base | Head | Reviewed tree |
| --- | --- | --- | --- |
| [#378 baseline](https://github.com/kburson/aitm/pull/378) | `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7` | `11d4b9e73cdf3b0fe7a5d9a3bd89ca06534b8a37` | `2d914c419d10db721de5615d63d12ebb4920f02d` |
| [#379 Ubuntu cutover, stacked](https://github.com/kburson/aitm/pull/379) | `11d4b9e73cdf3b0fe7a5d9a3bd89ca06534b8a37` | `0beaff25e9150d9d6af25827fd5bec08cf296846` | `4378f7d06a6b2af9ccbcdf2d8f5eec005d819303` |

Independent Codex source review and a direct Claude Opus 5.5 high-effort review passed both exact source trees. The installed peer-review wrapper called a command absent from the installed CLI, so the cross-provider review used read-only Git object access in a separate Claude session.

The bridge review initially held the candidate over lost native ACL classification coverage, malformed platform evidence that did not produce a structured HOLD, and a test that stopped exercising the real capability refusal. The reviewed revision exercises kernel ACLs on Linux and Darwin classification, retains optional real Darwin probes, and keeps the previous TIA refusal test. The final scope fixture uses a private test-specific writer guard with the ledger ACL, ancestry and lease checks in force.

The cutover review checked exact-base outcome comparison, the raw line floors, child coverage, attestation and artifact custody. It checked the digest-pinned Linux gh release, the pinned Python runtime and the private scratch paths. The original macOS FSEvents lifecycle checks remain opt-in. The required watch tests exercise the public events.

Local corroboration included 1,513 candidate product tests, both expected child-process records, 14,472 of 15,925 product lines covered, 244 helper tests, 1,039 of 1,112 helper lines covered, and 23 opt-in and shared macOS watch and ACL tests. Hosted proof and trusted verification are separate. Retargeting #379 requires a fresh authenticated run on trunk and a check that the reviewed tree and diff are still exact.

After #378 landed, #379 moved to trunk base `fc2ef028aa4d87afc83924af54546358e426e6d0` and head `e4c1ac15ad73fcf3ea498a50bbcb745c743ff924`. Independent readback confirmed that the base and candidate trees were byte-identical to those already reviewed and the live diff was unchanged. The trusted verifier passed the [fresh canonical attempt](https://github.com/kburson/aitm/actions/runs/44448593908/attempts/2). The collector required both Ubuntu lanes to use the same hosted runner image revision.
