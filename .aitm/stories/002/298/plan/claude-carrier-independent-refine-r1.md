[18:15:37]
# REFINE_298: HOLD

This review used only the Refine note, the native receipt, the R2 design and activation notes, the code excerpts and the graph readbacks you supplied. I did not recompute the `dc78…ae05` digest because this session had no file access. The code excerpts are not contiguous: `_finish_boundary` is cut off partway, and `_native_delta` and `set_permission` are missing. My findings are limited to the logic that is shown.

## Findings

**F1. Blocking. Under the current origin rule, the first request after an arm comes out UNKNOWN every time.**
- `_verify_next` sets the epoch at the earliest qualified boundary after `frontier.last_ordinal`.
- The epoch landed at assistant row 32, not at API row 31. So none of the rows after the frontier and before 32 qualified as a boundary: the resume bootstrap, the user row and the API request row.
- When an epoch falls inside a span (`start < epoch.ordinal < end`), `span_disposition` returns UNKNOWN. That happens through the `enabled is not epoch.enabled` check.
- So [31,33) is UNKNOWN because of how the code works, not by chance. Re-running the R2 sequence would give the same result.
- Neither in-scope path has evidence behind it:
  - Path (1): nothing in the supplied code places an epoch before the verified boundary.
  - Path (2): the run itself shows that none of the row types it produced count as a boundary.

**F2. Blocking. The receipt cannot show that the arm really came before the request.**
- It does not record `frontier.last_ordinal`, the checkpoint offset, or when process 2 was launched relative to the arm.
- It gives no disposition for rows [22,31).
- The code only bounds the frontier at `last_ordinal < 32`. Eligibility needs `< 31`, recorded against process 2's dispatch.

**F3. Blocking. The diagnostics and claims are not tied to anything.**
- The receipt shows two pending candidates, one coverage gap and four unreconciled-usage diagnostics. None of them is linked to a span or an obligation.
- The R2 JIT clause names three unreconciled-usage instances, and the 3 → 4 change is not explained.
- The Refine must show which spans the two candidates cover. If either one stands on [31,33) or on row 32 alone, that is an assistant-anchor reclassification in practice.

**F4. Blocking. Path (2) does not fit the accepted gates.**
- R2 fixes the workload at three invocations. The first turn after arming is an admitted turn with one prompt, one request, one terminal result and one quota event.
- The cold-read target is the enrollment claim plus the measured claim.
- Path (2) swaps that for a non-billable control boundary plus two measured runs. That is a four-process experiment built differently, so it needs an amendment to the R2 Design, not a Refine interpretation.

**F5. Estimate: honest, but it cannot be approved.**
- The parts add up: 1.15 + 1.25 + 1.1 + 0.5 = 4.0, and the note says plainly that the figure is conditional.
- It depends on a feasibility result that has no bound yet.
- Some work is not budgeted:
  - designing how the five diagnostic instances are generated and closed;
  - roughly 17 negative controls squeezed into 1.1 hours;
  - a fixture that must reproduce the native UNKNOWN shape, not just the eligible one;
  - native re-runs.
- The accepted story bound was not supplied, so I can't check whether 4.0 fits it. Expect the estimate to go up, and re-size it after feasibility is settled.

**F6. Compliant, not blocking.**
- The origin rule is kept. Enrollment is not reclassified using the later assistant row, the counters, the input footprint or a hand-set position.
- No coverage masking and no generic diagnostic filtering.
- R3 work stays with #295. No report or export changes. Epic #2, C01 and cutover stay out.
- Graph readbacks match the activation conditions:
  - #298 is blocked by {210 (closed)} and blocks {295}.
  - #295 is blocked by {210, 298}.
  - #119's prerequisites are exactly {118, 199, 201, 202, 203, 209, 210, 295}.
- The readback is incomplete: you didn't supply #295's outgoing edges ({119}), #298's parent (#100), or proof that #298 has no link to #2.

## Can a bounded existing-origin experiment reach JIT?

Not on the evidence so far. There is only one route through existing public authority that could work:

> `capture_frontier` → a **non-billable** native row on pinned 2.1.318 that `_native_delta` treats as a qualified boundary → `verify_boundary` → `set_permission` → two measured processes, each a fresh resume → public `RoutingJournal.prepare` / `reserve_batch` / `cursor_for`.

Before any native run, this needs a read-only, time-boxed check (I suggest at most 1 agent-hour) of `_native_delta` and the pinned 2.1.318 transcript row format:

- **If a non-billable row type qualifies:** take it to an R2 Design amendment per F4, with F2 and F3 closed in the receipt schema.
- **If none qualifies:** path (2) cannot work on the existing origin, and path (1) has no seam in the supplied code. Further experiments cannot unblock this Refine.

## What would need independent parent scope re-acceptance

1. **Any new origin authority.** For example, committing the epoch at `frontier.last_ordinal + 1` or at the start of the request, or any "prospective origin" authority not tied to the first verified qualified boundary.
2. **Any change to what counts as acceptance.** For example, delivering with one eligible claim plus a permanent hold on enrollment, or dropping "exactly two distinct admitted complete claims". Either would change #295's ordinary-prefix positive control and the activation conditions.
3. **Any split, or re-sizing past the accepted bound**, because that changes the graph.

A four-process workload by itself needs only an independent R2 Design re-review. It becomes a parent scope matter only if it pulls in items 1–3 or changes what the carrier and #295 each own.

#298 stays in Refine. #295's gates are unchanged, and there is no JIT or delivery.
