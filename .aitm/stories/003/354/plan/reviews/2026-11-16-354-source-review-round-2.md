# Independent #354 implementation review, round 2

**Disposition — PASS for the exact replacement source and local behavior.** Both round-one findings are resolved.

Signed — Codex independent source reviewer `/root/review_354`, 2026-11-16 UTC.

- Base and evidence anchor `8799c5a445dd4b51d499132e9a314b64796ae918`, tree `456a155fbe7d10cb7daafd2bf46f134be78366a8`.
- Replacement PR head `4770d3259d7c4c8db5aaffb0eda9109ae4c65ea3`, tree `90f2cc4007a82493029799d1a1cec10a855cc4a7`.
- Governing XPR-accepted plan `.aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md`, recomputed SHA-256 `0267141e5b25ee88112e23b081e8d392aca09d0142ad8f6b4d1b1e1dabab0530`.
- Previous review covers head `37121ba4783119839313da107a3c1e61d0d0a1e8`, tree `6c7ea2f986f1dc9180a760459418fda995f4dfae`. Its saved CLI probe belongs to that earlier tree. The independent replays below used the replacement tree.

## Resolved findings

1. **Bytecode writes.** The documented command and subprocess tests now use `python -B -E -s -m`. The added test inventories the fresh tooling filesystem before and after startup, so ignored bytecode would fail the assertion. In my independent positive replay from the exact replacement checkout with that same checkout as `--repo`, the tool reported all 30 IDs and preserved HEAD, the raw index SHA-256, tracked status, audited source bytes and the absence of bytecode caches.
2. **Suffix-validation memory.** The validation now scans whitespace and matches a single comment at a time by byte offsets in the existing captured buffer. The LF boundary check guarantees a terminator for each comment and rejects non-LF-terminated suffixes. The preliminary search requires at least one suffix comment marker, and the per-line match rejects each non-admitted byte, including CR, FF, VT, NUL and DEL. There is no suffix copy or accumulating match state. I compared the revised matcher to the accepted grammar over 66,430 small byte cases and inspected the passing transient-allocation regression using 2,048 comment-and-blank-line pairs.

## Verification

- Ran the exact guide invocation in scratch against both the evidence anchor and replacement delivery tree. Each returned the same 30 unique IDs as #352, with the current HEAD and tree separate from the evidence anchor, the audited content digest, and both candidate inventory and impact completeness marked `unqualified`. The report still matches the retained uncompressed #344 source-case inventory byte for byte. Import tracing confirmed the namespaced map and snapshot modules and showed no pytest, source package, stock planner, inventory, Python gate or bare selector import. The probe ran no candidate test collection or bodies.
- Replayed exit 2 with exact structured JSON and empty IDs for clean and syntactically valid unknown bases, the reverted index-only extra path on a qualified delivery tree, and a comment containing CR followed by source text. The test suite also exercised staged and mixed edits, rename, delete, symlink, mode, inventory and selector failures, drift, bad arguments and the trusted/target boundary.
- Independently ran all 92 focused and adjacent report, snapshot and path-map tests in a detached scratch clone of the exact replacement, using the repository's CPython 3.13.9 environment. Ruff check passed and all 39 files passed the format check. The scratch checkout remained clean. `git diff --check` passed. The entire base/head diff contains the same four planned paths. Hosted workflows, selector, map, suite and coverage policy, snapshot resolver, Python gate and verifier have identical bytes at base and head.

## Declined judgments

This PASS covers source and local report behavior at the named head and tree. Authenticated hosted CI, GitHub merge disposition, delivery verification, sign-off, closure, impact completeness, candidate inventory and #355 execution evidence require their separate authority.
