# #203 independent Refine review round 2

Claude Opus 5.5 high. Reviewed split SHA-256 `0158b267bcfcee8989639d7aa89a84bdf4e1687849ec449abfab07fe198a6cbf` on November 10, 2026 America/Chicago.

# PASS

This PASS covers the amended split and the native graph only, as pasted (`0158b267…`). I did not recompute the hash. It does not authorize code, Develop, any JIT, or any settlement behaviour.

## B1–B4

| Item | Status | Where it is now owned |
| --- | --- | --- |
| **B1** Effective hold transition | Resolved | M08b4c owns it. The v4 journal outcome decides the effective hold, and the ScopeView is derived from that committed outcome under the existing fence. There is no two-file commit. The ScopeState snapshot stays as historical evidence. Crash behaviour before and after commit is specified, and a mismatched hold or route is rejected before release. |
| **B2** #115 contradiction check | Resolved | M08b4b runs the real #115 reader against existing durable claims. It proves that claims and progress don't change, and it records the Grok admission dependency and the fact that no admitted Grok claim can be seeded today. |
| **B3** Keep-unsettled behaviours | Resolved | M08b4b has executable negatives for quota-only, same-code generic, mixed, OVERLAP_UNVERIFIED and aggregate inputs, plus the copied-scope causal-revision refusal. "Before #204" matches "before M08b5", because #204 is M08b5. All three leaves keep the rule that publication stays with M09 and the journal sends no project ACK. |
| **B4** #203's native record | Resolved | #203's GitHub title and body, planning title, scope and `plan-origin` are re-scoped to M08b4a. The new issues and their `plan-origin` records cite the same split hash. |

## Retained conditions

1. **Backlog, own Refine and JIT, Rank: carried.** Fractional ranks must be checked before they are assigned and read back afterwards.
2. **No early release: carried in substance.** M08b4b moves no cursor, makes no hold effective and settles nothing. M08b4c makes each settlement one atomic JournalChange. The text no longer says that M08b4c *extends `record_disposition`*. See binding condition 1 below.
3. **Re-check at adjudication: carried.** A stale proposal stays held, which is at least as strict as falling back to GAP or held.
4. **Holds created before M08b4a: carried.** A legacy hold or v1 resolution without the new witness gives no target authority. Any reproof path needs its own accepted evidence.
5. **Fixtures: carried.** Rows must be monotonic, go through the public `read_source`, and use no backdated or zero-delta counter. A genuine later-usage case is required. The new preflight meets this: the follow-up rows are stamped with the returned `next_when`, the usage deltas are positive, and it doesn't use `_capture_position` or `_native_cursor`.
6. **Unchanged state: carried with a refinement.** The private scope artifact may only gain proof records. Existing entries stay byte-equivalent, and the effective holds, routing view, journal bytes and cursors are compared before and after issuance and replay. This is accurate, since M08b4a has to persist its proof somewhere.
7. **Graph read-back: carried.** It happens before Develop and before closing any of the three leaves.

**Graph:** 202 → 203 → b → c → 204 → 119. Each leaf directly blocks #119, the 203 → 204 edge is kept, #204 keeps its own #119 gate, and all three leaves stay #100 children. There is no cycle.

## The proof-only EOF read vs. a settled EOF frontier

These are two separate facts:

- **What the preflight proves (proof-only).** A terminal receipt at end of file passes `verify_boundary`: it is eligible, its ordinal 42 is at or after the hold end 34, and the original target and prefix are byte-stable. The legacy `dispose` still refuses. That is enough to authenticate the receipt and join it to the older span `[27,34)`.
- **What it does not prove (settled frontier).** The same read has no cursor and carries BOUNDARY_UNVERIFIED. Adding usage afterwards produces a cursor only because real usage now exists after the receipt. So no fixture yet shows a terminal with **no later usage and a settled frontier**. The earlier #203 preflight seemed to show one, but that came from the backdated counter (`CUTOFF - 1s`). The amendment rightly withdraws that claim.
- **M08b4c keeps its gates.** It stays open, and the direct #119 and #204 gates stay in place, until its Refine qualifies a genuinely settled no-later-usage carrier. That carrier must use the public reader, chronological rows, and real usage before the terminal, plus a separate later-usage control. If qualifying it needs a source change, that goes through M08b4c's own JIT or an accepted bounded successor. No release may rely on the EOF read's open boundary or its missing cursor. The artifact states all of this. Treat it as binding.

## Binding conditions for later JITs (none block the split)

1. **Settlement method.** The M08b4c JIT must name the method that produces the settlement JournalChange: `record_disposition` extended, or a separate adjudication entry point. If it is not `record_disposition`, M08b4c must name which method #204 will extend for its folded intent. The M08b4b contract freeze must allow that extension without a second change for one settlement.
2. **Later-usage case outcome.** The M08b4a JIT must state the exact expected result of this case. It disproves "no later usage". It does not invalidate the receipt. The cursor it produces must never count as settlement evidence for the older span.
3. **Consumers of the effective view.** The M08b4c JIT must list every consumer of `view()` and `_timeline`/`prior.held`, and show that admitted routing reads only the derived view. It must also cover `expire()` or legacy `dispose` changing the ScopeState hold before or after the journal adjudicates. Any change before adjudication makes "unchanged hold" fail, so the proposal stays held.
4. **Schema review in M08b4c.** If M08b4c adds private journal or scope schema beyond v4, the #199 schema-review rule applies: admission from the old version, atomic change and retry, old rows, historic views, and unknown formats.
5. **Rank fallback.** If Project 24 does not support 228.1 or 228.2, or either is taken, stop and resubmit. Do not renumber any other item.
6. **Provenance.** #203's amended `plan-origin` keeps the lineage to #199's split (`1c97ab7d…`) and the parent plan (`8899a4d1…`) and adds this hash. It does not replace them.
7. **Quota.** No quota coverage refinement is delivered in this chain. Adding one later needs its own accepted story, with a direct #119 blocker created before any predecessor closes.
8. **Preflight assertions.** The M08b4a positive keeps the source, stream and session equality checks from the earlier preflight. The new preflight leaves them out.
