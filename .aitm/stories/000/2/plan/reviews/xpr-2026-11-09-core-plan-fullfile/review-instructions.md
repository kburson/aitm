# Task-scoped native review instructions

Owner authorization, 2026-11-09: run a separate full-file validation of the core design, then a separate validation of its implementation plan; Astra-6/ExtraHigh author and Opus 5.5/high reviewer; publish results and stop before implementation. This validation is independent of previous accepted reviews whose later rounds used targeted rereads. Preserve those historical reviews.

## Mandatory reading procedure — EVERY round, including the acceptance round

Before evaluating or submitting each pending response, freshly read the ENTIRE current file under review from line 1 through EOF in this round using Read. Use contiguous chunks of at most 30 lines to avoid truncated outputs. Continue until the tool displays EOF; inspect output for truncation and retrieve any omitted range. Prior conversation context, prior-round reads, a diff, search hits, or selected changed sections do not satisfy this requirement. If the file changes in an author turn, restart at line 1 in the next round. This is the owner's explicit requirement and a condition of this separate validation.

In the body of every reviewer response record a Fresh full-file reread subsection listing the actual contiguous ranges, observed line count and the native input artifact digest, and state whether any output was truncated and how it was recovered. Do not submit acceptance before finishing the reread. Author will independently audit tool results before finalization; do not infer proof from the instruction itself.

## Review scope and decision hierarchy

Read .aitm/README.md, .aitm/stories/000/1/draft.md, .aitm/stories/000/1/design/architecture.md, .aitm/stories/000/1/plan/master-plan.md, .aitm/stories/000/2/draft.md, and .aitm/drafts/2026-11/20261108-1310-peer-review/draft.md as context. Explicit owner/user and agreed decisions outrank provisional calls. Preserve unresolved choices; do not silently choose global review policy. Review the full current FUR for correctness, internal consistency, alignment with accepted parent/owner scope, implementability and acceptance coverage. Do not limit the review to historical findings. In later rounds also read every preceding reviewer/author response and verify all dispositions.

For core design, assess its contracts independently; the implementation plan is downstream and must adapt to accepted design changes. For plan validation, assess full traceability to the accepted design, leaf size <=4 agent-hours, ordering and shared-file dependencies, independent work, touched areas, executable tests and acceptance evidence, recovery/migration/release checkpoints. Do not implement code, change other documents, close issues or decide unresolved owner choices. Each validation has a five-round cap; unresolved required findings are not acceptance.

## Protocol boundaries

Follow the generated native invitation, registered peer-review skill and exact next-action commands. No Git commands. No writes except the exact pending reviewer response body and package-owned transition. Do not edit FUR, instructions, setup, protected response metadata or other files. Use only the package-generated join and submit commands; no permission changes, direct launcher construction or identity overrides. Keep chat terse and put complete findings, stable IDs, severity/requiredness and rationale in the response. These instructions are immutable task context set before startup, not a change to global policy.

## This worktree: separate implementation-plan validation

The FUR is .aitm/stories/000/2/plan/core-implementation-plan.md. Read the complete current accepted core design at .aitm/stories/000/2/design/core-design.md as context. Design full-file validation published at3702cfde855e7a2345e12439f19cc2ee9ebe7291; its five required findings were resolved in three rounds. The plan was prepared against those new contracts before this review: read .aitm/stories/000/2/plan/reviews/xpr-2026-11-09-core-plan-fullfile/preparation/provenance.md. Initial plan candidate contains75 leaves/242.5 h. Do not assume this decomposition is correct or accepted; independently check all current file content, tests, size, dependencies, source/producer contracts and qualification coverage against the design. Findings may concern any existing or prepared section. Distinguish author preparation from findings you raise.

Use fresh contiguous Read chunks <=30 lines for the entire FUR in EVERY round, including acceptance. Check for >2000-character lines with Grep; do not treat truncated lines as fully read. Current physical line maximum was bounded before start. Report any inability to retrieve complete bytes instead of claiming the procedure passed. No Git or other writes. Preserve the old accepted reviews and keep global policy choices open.
