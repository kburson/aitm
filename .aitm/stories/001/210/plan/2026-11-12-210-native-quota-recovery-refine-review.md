[09:06:49]
PASS

I checked the amended proposal against my four material findings and the smaller items. Every one is resolved, and none needs new parser behaviour.

**Finding 1: the cutoff excludes earlier quota rows**
- In `codex.py:545-546`, `eligible(frame)` returns false when `frame.pre_cutoff` is set.
- `rate_limits` (`codex.py:1121-1123`) checks that before it reads the account, the limit ID or any window. So a pre-cutoff row adds no quota and no gap diagnostic.
- `gap` (`codex.py:548-549`) has the same guard, so pre-cutoff rows can't produce native diagnostics by any route.
- The replay matches the code: 16 pre-cutoff quota rows, 1 eligible row (155), 1 window and empty `native_diagnostics`. That includes the old diagnosis rows (114/119/123) and the old later-usage rows (142/146).
- In the fresh run, the cutoff is set after the new first account check. Row 155 also falls before it, so every quota row that gets judged sits between two matched account checks.
- This is the "parser-level row limit" I asked for, and it is existing behaviour, so it isn't new scope.

**Finding 1: accounting is preserved**
- Pre-cutoff rows stay structural and numeric baseline under the existing scanner rules. Only eligibility changes.
- The earlier replay with no cutoff showed identical usage reconciliation. The cutoff only marks rows as pre-cutoff; it doesn't change how usage is parsed.
- The cutoff replay output doesn't report reconciliation itself. That's acceptable because the reconciled changed-counter gate still applies to the fresh run: if accounting breaks, the run refuses rather than passing.

**Findings 2–4**
- **Second finding (control outside the check):** the second check runs before the positive is read, and the third runs after the control turn and before the control is read. All three must match each other and the creator, or the run refuses.
- **Third finding (one cause):** the control must be self-rooted, carry no native diagnostics under the same binding, show the later accounting and cursor, and be refused only because of later usage. The hold stays intact.
- **Fourth finding (delivery):** the binding is passed in-process to a writer the driver hosts. There is no CLI flag, environment variable, file, registry field or subprocess.

**Smaller items**
All are covered:
- Restart drops the binding, so a retry needs a new cutoff and fresh proof.
- One unchanged binding across each scan and rescan.
- The account reference is derived as `pseudonymize("codex-account", backend_id)` and validated with the same service key.
- No production reference, and quota data stays out of Git and production.
- The switch-and-switch-back risk is recorded, and auth changes are banned during the run.
- The 1.60 agent-hour budget is stated.

**Conditions, all already within the proposal's wording**
1. Write a private copy of the `_AccountAuthority` shape. Don't import it from the legacy `service.py`.
2. If the binding or the writer changes between scan and rescan, throw away the result and clear the witness sink. "Changed evidence is unavailable" should cover this; the tests should prove it.
3. The cutoff value is part of the binding. Moving the cutoff therefore counts as a changed binding and makes the read unavailable.
4. The new run must report the reconciled changed counter under the cutoff on its own. The cutoff replay doesn't establish it.

All approved gates are unchanged: exact self-root, fixed committed prefix, reconciled changed counter, no diagnostics, ownership, typed queue, original hold and checkpoint, the independent JIT, the signed hosted workflow and delivery review. Epic #2, C01 and cutover stay excluded.
