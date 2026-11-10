# #139 independent SPR · target refresh

Reviewer `codex-collaboration:/root/prep158`. Author
`codex-collaboration:/root`. Reviewed all 60 physical lines of
`139-target-refresh.md`, raw SHA-256
`a3e9efc8ea1387efa527b3f4c43425eb3d650175672c4dc0e5bcb3d63c142ca4`.
Compared the delta with the accepted #139 design, plan and JIT at
`b62000a647dccd1343573deaddf436ca179a5177`. This verdict covers the JIT
refresh and the two taxonomy additions.

## Checked assertions

- Authenticated GitHub readback showed PR #195 merged to literal
  `trunk` at `49865245d175ce6c52913738f2c9a42c0abea632`, also the live
  target. The Git object has the claimed tree
  `9737a9685e928c57e922cc8a68343ae195b9bacf` and first parent
  `a495d60a87ac4ca764f019dc266e579f13f1787e`. Delivered #138 is an
  ancestor. Verified a zero diff across `tools/ci`, workflows, the
  package manifest and the lock. The product test diff has precisely
  the two new modules and the three modified modules in the delta.
- Authenticated run 42912899702 attempt 1 is a successful trunk push on
  that exact commit, workflow 412848571 and suite 116218799122.
  Quality, Python, file checks and collector passed. The PR-only jobs
  were skipped on this push. Authenticated artifact metadata matched
  the supplied ZIP for artifact 13808377023. Independently hashed
  the ZIP, raw `pytest.json` and sorted compact UTF-8 node array.
  All three digests match the delta. Verified 867 unique nodes,
  zero deselections, 2,601 passing phase reports, both required
  successful child exits, Darwin/APFS, and coverage of 9,638/10,538
  product lines and 778/821 lines in the four policy helper files.
- The old raw observer receipt and 748-node digest match the accepted
  JIT. The exact set comparison produces 119 additions and no removals.
  Counts are 40 legacy, 25 admission, 31 Codex, 22 Claude and one
  monitor-scope ID. The unchanged helper scope retains its separately
  bound 182-ID advisory reference. The 1,049-obligation full advisory
  total is conditional on fresh same-snapshot local collections.
- The two exact new module rules match the accepted integration
  taxonomy. The admission tests use the actual ledger and registry,
  CLI entry point, inbox publication locks and durable file effects.
  The legacy tests register and open a real ledger, exercise CLI and
  service interfaces, and reconcile publication under the legacy and
  monitor locks. `native-process-state` fits the accepted conservative
  group for these integration fixtures. The other additions occur
  under existing module rules. The delta preserves the reviewed
  Darwin/APFS scope, explicit per-test capabilities and unknown-module
  refusal.
- Pickup retains the original attempt and older proof, requires both
  fresh local collection components and their common snapshot, then
  calls for fresh #103 PR checks and independent source review on the
  resulting candidate.

## Findings

No required findings.

## Decision

accepted
