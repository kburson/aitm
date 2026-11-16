# #354 development checkpoint

The exact [implementation plan](2026-11-16-354-working-tree-obligations-plan.md) passed SAR and Opus 5.5 high XPR in round two. The report is implemented on `codex/354-working-tree-report`, head `37121ba4783119839313da107a3c1e61d0d0a1e8`, tree `6c7ea2f986f1dc9180a760459418fda995f4dfae`, from trunk `8799c5a445dd4b51d499132e9a314b64796ae918`.

The locked local run passed 90 tests across the new report suite, snapshot tests, and path-map tests. Ruff check and format check passed across `tools/ci`. The initial test suite failed before implementation because the report module was absent. After implementation, a synthetic fixture initially expected `unqualified-base` even though it lacked the evidence anchor and could not generate a snapshot. The corrected control verifies `snapshot-unavailable` there and verifies `unqualified-base` separately on a repository with the anchor.

The [CLI probe](../attachments/2026-11-16-354-local-report-probe.json) matched the exact 30 archived node IDs on the original evidence anchor and on a scratch commit with the exact delivery tree. Clean, additional-path, and executable-edit controls returned explicit unavailability with zero IDs. The probe checked HEAD, index tree, Git status, and candidate file bytes before and after each run.

The positive contract is pinned mapped obligations for the admitted comment-append profile. Candidate inventory and impact completeness are unqualified. The story remains in Develop. Hosted validation, independent implementation review and verified delivery remain required. #355 remains blocked by #354.
