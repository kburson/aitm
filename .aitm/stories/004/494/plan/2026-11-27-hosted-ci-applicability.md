# #494 hosted CI applicability

PR #535 is a single Markdown-file change at docs/architecture/legacy-sdlc/guard-facts.md. The delivered Core CI trigger covers packages/aitm-core/**, pyproject.toml, and uv.lock. Repository CI is the applicable hosted workflow for this documentation path. The synthetic candidate  and merged trunk receipt  have identical Core package, root inputs and Core CI workflow bytes. The most recent matching hosted Core run is #529 run 45979825833, with 99 tests and Ruff. The installed local suite passed 99 tests for #535's checkout.

Require fresh passing signed repository CI for the exact docs candidate. Re-evaluate Core applicability if any source, root inputs or workflow bytes change. Keep all normal draft, exact-tree SAR, verifier and delivery gates. The same applicability test covers later documentation-only leaves.
