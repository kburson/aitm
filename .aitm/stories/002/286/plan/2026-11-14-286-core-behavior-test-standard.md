# Core behavior-driven testing standard

Use this standard when planning, implementing, and independently reviewing a Core #2 story. Each test should demonstrate an observable outcome, a protective boundary, or a durable invariant. State the triggering condition, what a caller or maintainer can observe, and which regression the assertion would catch. Plain pytest is enough. Use the project's existing fixtures and assertion style.

## Choose a test layer

- Use a direct API or pure function test for rules that can be proven through a public contract in memory. Parameterize distinct outcomes or risks and name the examples accordingly.
- Use a real temporary Git repository for persistence, rollback, competing writers, and publication behavior. Assert the resulting tree, retained events, or public readback. Use real files when filesystem behavior is part of the contract.
- Use the installed CLI or an actual subprocess for entry point behavior, exit status, output contracts, and process isolation. Cover the user-visible result and start additional processes only when their participation is part of the behavior.
- Use adapters or fakes for external provider failure modes when the boundary is a response contract. Keep a representative native or provider check when a fake cannot prove the mechanism.

## Examples from Core's contracts

| Scenario | Observable evidence | Regression it catches |
| --- | --- | --- |
| A required guard refuses a transition in enforce mode (C28, #37) | The CLI reports the refusal, the story remains in the prior state, and the retained record distinguishes the refused operation from a successful transition. | Treating a refusal as a state change or losing its reason. |
| Rebuild the local index from the published story store (C18, #23) | A fresh checkout without the prior index reads the same story state and pending operation from retained events. | Making cached state authoritative or losing an event required for recovery. |
| A caller retries after a lost publication acknowledgment (C50, #60) | The same operation ID results in one published outcome. Reopen the persisted store and read back the event and current state. | Duplicating an external side effect or appending a second state transition. |
| A concurrent planning writer changes an overlapping story | A stale write is refused after refresh and preserves the other writer's story and event history. A disjoint-writer case can separately demonstrate permitted replay. | Overwriting someone else's work or refusing all valid concurrent work. |
| An extension adds a guard and a protected operation invokes it | The public operation obeys the guard and exposes its attributable result. Include a real failure case for an unavailable required provider. | Treating extension registration as sufficient or silently continuing when the required guard is unavailable. |

These are test-design examples from the accepted Core design. Apply them to the exact contract of each owning leaf. [Core design](../../../000/2/design/core-design.md)

## Story acceptance and independent review

For a story, link changed behaviors to named test nodes or integration commands and identify the expected protective boundary cases. Review whether each new or materially changed test would fail on a meaningful regression, whether it repeats an existing witness, and whether its test layer is the least expensive one that proves the requirement. Capture distinct case risks when parameterizing. Use timings when choosing between equivalent witnesses. Keep meaningful cases even if they contribute no unique measured coverage.

## Independent review checklist

- [ ] Identify the linked Core story, normal entry point, behavior and concrete regression each new test would catch.
- [ ] Check pass and applicable protective cases. Confirm the assertion observes the result at the right boundary.
- [ ] Check whether an existing witness already proves the same case. Preserve distinct parameter risks and retain high-fidelity witnesses for native or persistence behavior.
- [ ] When simplifying a slow fixture or consolidating cases, retain before/after timings and a regression witness demonstrating the surviving test still catches the defect.
- [ ] Record change impact, required tests, uncertainty and any applicable full fallback with the normal story validation.

Use coverage to locate behavior that merits inspection. The current #103 policy still governs validation and remains unchanged. Use the applicable full fallback for uncertain test impact. If a necessary behavior cannot yet be exercised at its real boundary, record the gap and its owner in the story evidence. Apply this guidance through the normal story plan and independent review. It adds no automated gate.

## Example review walkthrough

For the CLI refusal in enforce mode, exercise the C28 boundary. Advisory mode may advance on an eligible edge with an attributable failed guard, and an illegal edge still refuses. C78 (#81) can verify that installed `explain` reports the actual guard disposition for the pinned state. A direct guard check alone cannot prove how the installed command exits or what persisted state it leaves. Pair a cheap rule test with one representative CLI/store check when they demonstrate those distinct obligations. For the publication retry, count the actual persisted operation after reopening the fixture. Mock call counts can help diagnose errors inside the test, while the published history supplies the behavioral witness. Review a timing change alongside its retained boundary evidence when consolidating.
