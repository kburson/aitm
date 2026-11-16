# Independent #354 implementation review, round 1

**Disposition — HOLD.** Resolve both findings and submit the replacement commit and tree for review.

Signed — Codex independent source reviewer `/root/review_354`, 2026-11-16 UTC.

- Base and evidence anchor `8799c5a445dd4b51d499132e9a314b64796ae918`, tree `456a155fbe7d10cb7daafd2bf46f134be78366a8`.
- PR head `37121ba4783119839313da107a3c1e61d0d0a1e8`, tree `6c7ea2f986f1dc9180a760459418fda995f4dfae`. The base is its exact parent.
- Governing XPR-accepted plan `.aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md`, SHA-256 `0267141e5b25ee88112e23b081e8d392aca09d0142ad8f6b4d1b1e1dabab0530`. I recomputed the digest and checked the round-two verdict against it.

## Findings

1. **[P2] The documented invocation writes bytecode into a fresh checkout.** The example at `docs/ci.md:60` uses `python -E -s -m`. CPython 3.13.9 created `tools/ci/__pycache__/path_map.cpython-313.pyc`, `tools/ci/tia/__pycache__/snapshot.cpython-313.pyc` and `tools/ci/tia/__pycache__/working_tree_report.cpython-313.pyc` even for `--help` in a fresh archive of the exact head. A second positive replay reproduced all three writes with one scratch checkout serving as both the trusted tooling checkout and the inspected checkout. The repository ignores these files, so the reported Git status and the existing smoke custody checks miss this effect. Use `-B` in the documented invocation and subprocess tests, and verify the fresh tooling filesystem is unchanged. The same positive scratch control with `-B -E -s` returned 30 IDs, created zero bytecode files and preserved the audited source and raw index checksum.
2. **[P2] Whole-suffix matching uses disproportionate memory on valid input.** The quantified regex at `tools/ci/tia/working_tree_report.py:36` leaves state for every short line in `fullmatch` at line 193. In an isolated macOS arm64 scratch checkout at this head, the CPython 3.13.9 CLI peaked at 40,091,648 bytes RSS for one 25-byte comment and 626,458,624 bytes for the same comment after 2 MiB of permitted LF-only blank lines. Both runs produced the pinned obligations. The resolver permits a substantially larger regular file. The matcher can exhaust available memory before the report emits structured JSON. Scan line boundaries with bounded state, preserving the exact bytes and at-least-one-comment rule. Add a regression for a modest many-line suffix and maintain the existing control-byte refusals.

## Review evidence

- Verified the exact four-path diff, file modes, and clean `git diff --check`. Hosted workflows, the audited selector and map, suite policy, Python gate, coverage policy, verifier and snapshot resolver have identical bytes at base and head.
- Recomputed the #352 finding and independent review SHA-256 values against the implementation constants. Decompressed the #344 source-case inventory by receipt, byte-compared it to the new file, and verified SHA-256 `812bc918dd9da7b413786454906d2ec8f486b5624bc8d1deecf9d546928d48e6`. All four file hashes in the #354 local probe match the exact reviewed Git blobs.
- Replayed the exact #352 comment from the trusted tool against the exact candidate delivery tree. It reported the actual head and tree, audited content SHA-256 `d71cd5853453d5f85dfb2c369ff1c9c0efb37f898ae13134a4538bab16101647`, all 30 IDs matching the #352 receipt, and `unqualified` for both candidate inventory and impact completeness. Import tracing found the namespaced selector and snapshot modules, with no pytest, source package, bare selector, stock planner, inventory or Python gate import.
- Inspected staged, unstaged and effective admission, including the resolver's independent index and worktree observations. The committed exception admits exactly the three listed additions and same-mode documentation change. Local provenance forbids a staged extra path that was reversed in the worktree. The second resolver capture checks both snapshot digests. Map and selector custody, SHA-1 blob identity construction, scoped mapped module, and report refusal shape conform to the plan in the reviewed source. The named tests cover the planned ordinary decisions, with the gaps identified above.

## Declined judgments

This disposition covers source and isolated CLI observations for the named head and tree. It provides no candidate inventory, impact completeness, test execution or verdict, authenticated hosted-run disposition, delivery verification, sign-off, release approval, or #355 execution assurance. Review probes ran no candidate test bodies or collection.
