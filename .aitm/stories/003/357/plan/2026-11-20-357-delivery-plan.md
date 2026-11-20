# #357 Delivery plan

**Goal**

Build and independently review the exact category inventory.

**Scope**

[Refined story](../story.md) and [epic delivery plan](../../356/plan/2026-11-20-356-delivery-plan.md).

## Execute the spike

- [x] Pin trunk commit/tree, inventory every tracked pytest root and capture two plugin-observed local collections with exact IDs. Retain the import-path witness for the opt-in Darwin profile.
- [x] Compare the current family set against #285. Inspect added and changed modules and trace parametrization, autouse and shared fixtures, subprocess boundaries, host capabilities and provider dependencies. A single witnessed family rule may cover multiple IDs when their boundary and cost agree. Record overrides individually.
- [x] Collect matching Ubuntu profile evidence before claiming platform parity. Report any unavailable collection profile, skip or missing ID explicitly. Keep opt-in native IDs in the register.
- [x] Establish a repeatable timing baseline with isolated runs. Record setup, call and teardown separately, along with cold/warm effects. Start with a provisional 100 ms median total-phase cutoff over three valid observations for unit cases only. Reconsider it against the measured distribution before publishing and mark unstable or unmeasured placements. Historical durations are leads.
- [x] Reconcile the register against every captured ID with a duplicate check and exact set difference. Verify source/fixture witnesses, exception reasons and timing provenance.
- [ ] Have an independent reviewer reproduce collection, check mixed families and boundary cases, and accept the exact finding before releasing dependents.

## Classification rules to validate

1. **Systems integration** observes a real host facility, installed environment, external service, or end-to-end process lifecycle as part of what the test proves.
2. **Local integration** composes real components or persistence in a bounded local fixture. A mocked host or provider label does not establish native execution. A subprocess that only isolates a local reusable fixture does not on its own make a systems test.
3. **Fast unit / slow unit** isolate a behavior without requiring real component integration. Separate these with the measured cost rule, including fixture cost.
4. **Exception** gives an exact ID and reason when the boundary or evidence cannot support a placement. Distinguish genuinely outside the taxonomy from an unresolved placement. Keep runner capability and isolation flags independent of the category.

The findings register should carry profile, exact ID, category or exception, source/fixture witness, boundary rationale, timing sample or explicit gap, and runner/isolation notes. [Collection and first classifications](2026-11-20-357-collection-checkpoint.md).

[Classification findings](2026-11-20-357-classification-findings.md).
