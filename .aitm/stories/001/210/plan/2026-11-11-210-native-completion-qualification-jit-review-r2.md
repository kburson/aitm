PASS

**Decision:** The amended JIT resolves all seven findings from the initial HOLD. Read against the supplied code and probe, both disputed details favour the amendment. I am not adding a new requirement. One wording point in predicate 5 is clarified below, using the existing code; it does not block the slice.

## The two disputed details

- **Anchor (finding 5).** The initial review wrongly asked for `anchor_ref is None` as the ownership test. `verify_boundary` gets the owner from `target.project_context` and then `self._anchor(...)`, so ownership comes from the boundary's registered context. In the probe, the `REQUEST` receipt at ordinal 60 has `has_registered_checkout_context: true`. A null context cannot prove an owned hold, so predicate 5 is correct to require a non-null registered owner checkout.
- **Command form (finding 7).** `is_monitor_scope` accepts only seven parts: `["aitm-usage","monitor","scope",<verb>,"--request",<abs>,"--json"]`, and the command must equal `shlex.join(parts)`. There is no `--project`. That makes predicate 7's canonical form correct. Because the first part must be the literal `aitm-usage`, an absolute launcher path would not be recognised either. So Desktop's own environment has to resolve the name, as the amendment says.

## How each initial finding is resolved

| # | Finding | Where the amendment resolves it | Code or probe evidence |
|---|---|---|---|
| 1 | Which path carries the witness, plus a differential test | Predicate 1 | Every probe phase returns `cursor: false` with only `boundary-unverified`. For Codex, `retains_prefix` is always `True`, so this early return happens only when `provider_checkpoint is None`. Predicate 1 also requires no native diagnostics before it, clears the sink on rescan or refusal, and asserts identical output with the sink on and off. |
| 2 | What may sit between the counter and `task_complete` | Predicate 2 | Nothing may sit between them. The probe gives request 60, counter 61 and close 62 (63 rows), then the `TURN` receipt at 63. The 12-turn sample shows no rows between the last counter and completion. The close must be the last committed frame, with the cursor at the capture limit. |
| 3 | Closed allowlist for the close row; missing negatives | Predicate 3 | It lists nine allowed `task_complete` keys and rejects unknown ones. A non-null error, an abort or a warning invalidates the turn. All eight requested negatives are listed, plus the second tool call and response after the receipt-linked response. |
| 4 | Whether the accounting classification is computed | Predicate 4 | `_read_usage` passes `Eligibility.ELIGIBLE`, so `record_usage` is true and `counter()` reaches `complete`. The witness requires `complete`; a missing classification, `COVERAGE_GAP` or `UNRECONCILED_USAGE` refuses. |
| 5 | `verify_boundary` reuse stays pure; the witness can't be used elsewhere | Predicate 5 | The shared private helper records nothing in `_boundaries`. It requires `REQUEST` and the exact `codex_request_boundary_reference`. A test refuses both the witness and the old `VerifiedBoundary` as next-turn authority. |
| 6 | Qualification negatives | Predicate 6 | Every requested case is listed, plus failure injection between the read and the qualification. Taking a read-only snapshot of the hold in the opt-in batch for later comparison is allowed. |
| 7 | An actionable time bound | Predicate 7 | It defines what the 0.75 h checkpoint decides and the split at 1.60 h. The Desktop attempt counts inside the 1.60 h, and the gap is recorded if no isolated environment works. |

## How to read predicate 5 (binding, not a blocker)

The code has two different "anchors":
- **The scanner frame anchor (`frame.anchor_ref`).** The existing selected rescan requires it to be `None`. That rule stays unchanged, and predicate 1 keeps the witness on that path.
- **The registered checkout context (`NativeBoundary.anchor_ref` / `project_context`).** "Both frame anchors must match the same verified registered owner checkout" applies to this one. It must be non-null and equal the owner checkout.

If the close frame carries no scope-evidence context to compare, the witness is unavailable. That fails closed, so it is safe.

## Unchanged

- Without the witness sink, collection, the provider cursor, next-turn suppression and diagnostics, release paths, CI gates and independent acceptance behave as they do on trunk.
- A genuine Desktop positive, including the later-usage control, is still required before any hold release. The synthetic fixture only establishes the code path and refusals.
- #204 and #119 stay gated. Epic #2, C01 and production cutover remain out of scope.
