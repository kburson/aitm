# #91 U07 · As-of export and C44 compatibility proof · Late retrospective

Written and signed on November 9, 2026 (America/Chicago), after the recorded closure. I implemented U07 as Codex task `/root/implement_u07`. [Story and closure](../story.md) · [Planning events](../events.jsonl).

## Design, plan and delivery

The reviewed design and plan called for deterministic exports at a fixed ledger sequence and a disposable C44 receiver. I implemented the lease-free export command, exact observation and scope provenance, a versioned rate basis, and an allowlisted JSONL and manifest pair. The SQLite fixture proved that a withheld observation could finalize after restart and watermark advance, and that corrections could reconcile while preserving the original accepted bytes. The fixed-cutoff export stayed byte-identical after later ledger changes. [Design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Source review](../plan/source-review.md).

The accepted leaf head was `304a52aab095a4c7b30396222082b6a0f06ec958`. It entered the independently reviewed #83 integration head `00ccef89e1e0bd541981b4a367d005f699c63769`, delivered in protected PR #97. The later PR #98 for #88 repaired the Codex Desktop marker carrier. PR #99 for #87 repaired the Claude startup scanner. The protected PR #99 merge `f80f22645e2008c4cac9dc6e4003640bba976b5f` was the release used for #96's observed Mac activation, which included a byte-identical replay of 42 rows at cutoff 409. [Protected source delivery](../../83/attachments/source-delivery.md) · [Observed activation](../../96/attachments/activation-summary.md).

## What worked and what I missed

The initial tests covered replay, privacy, and receiver restart. Independent review exposed three gaps in my first candidate. A staging-name substitution could publish a competitor's directory, an exact retry could report success after a failed parent-directory sync, and a new rate or scope could conceal changes to an immutable observation. I added regressions at the real Darwin rename boundary and the SQLite transaction boundary, then repaired all three within the planned scope. The repaired head passed 26 focused tests, 386 locked package tests, static checks and an isolated wheel replay. The independent agent's exact-head specification and quality reviews were recorded off-platform. GitHub listed zero CI checks and zero submitted native reviews on PRs #97–#99. [Exact source review and test evidence](../plan/source-review.md) · [PR #97](https://github.com/kburson/aitm/pull/97) · [PR #98](https://github.com/kburson/aitm/pull/98) · [PR #99](https://github.com/kburson/aitm/pull/99).

## Lesson, confidence and timing

Test crash recovery through exact replay, including a sync failure after a successful rename. In an immutable receiver, verify observation, scope and price independently so changing one cannot hide a contradiction in another. **Confidence 4/5.** The local tests, independent review and observed export replay support the producer and fixture contracts. The fixture trusts the producer's cutoff and live C44 adoption requires its own proof. [Source review](../plan/source-review.md) · [Observed activation](../../96/attachments/activation-summary.md).

The plan allocated 3.5 agent-hours. Recorded wall-clock intervals were 9m 19s to the first local candidate and 4m 26s for the repair. The planning record entered Review at 13:29 CST and Done at 17:17 CST. Total active agent time, including review, is Unknown. [Estimate](../plan/implementation-plan.md) · [Planning events](../events.jsonl).

**Signed November 9, 2026 (America/Chicago)** — Codex `/root/implement_u07`, original U07 implementer. I sign this post-closure author assessment against reviewed leaf source `304a52aab095a4c7b30396222082b6a0f06ec958` and the recorded #83 delivery and #96 activation evidence. [Source review](../plan/source-review.md) · [Source delivery](../../83/attachments/source-delivery.md) · [Activation](../../96/attachments/activation-summary.md).
