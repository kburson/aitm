# #370 hosted integration decision

**Proceed with advisory shadow qualification. Hold promotion to the required PR gate.** #371 and #383 delivered the portable analysis and read-only probe on the Linux reference and macOS cross-check. #370 stays open for [#385](https://github.com/kburson/aitm/issues/385), its next story.

## Evidence reviewed

- #371 established that the Python file graph can share source across platforms. It also identified unresolved and dynamic imports and pytest collection as limits on safe narrowing. [Accepted spike](../../371/plan/2026-11-19-371-portable-python-tia-findings.md)
- #383 bound the staged index, HEAD, and PR tested tree and reproduced the same assignment for all three on each host. The real hook edit fell back to all 1,776 Ubuntu obligations, which passed, and matched all 1,771 macOS collected IDs. The exact GitHub PR test merge also matched the hosted product inventory. The controlled fixture selected nine of 16 tests and caught the same direct and transitive failures as the full suite. These results establish exact-tree handling, conservative fallback, and bounded graph behavior. They leave representative hosted narrowing and timing unqualified. [Qualification](../../383/plan/2026-11-19-383-qualification.md)
- PR #384's authenticated run and the successful trunk run cover delivery of the probe. Trunk `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9` has reviewed tree `875bb2e29df63abaa39c874215658bf3f9c9f6c8`. The probe's PR receipt checks Git object identity and carries local advisory provenance. The required workflow, path map, policy and verifier use the existing hosted contract. [Trunk sign-off](../../383/retro/2026-11-19-383-delivery.md) · [Authenticated PR receipt](../../383/plan/trusted-pr-384.json)

## Next story

[#385](https://github.com/kburson/aitm/issues/385) will compare the graph assignment, current path-map decision, and full outcomes on the same hosted Ubuntu PR trees. It will record test identities, witnesses, fallback and refusal behavior, and timing across representative repository changes and seeded cases. The story calls for zero missed failures in the declared matrix and at least one useful, explainable narrowing on real repository code. The existing hosted gate and #355 retain their authority. Any promotion requires a separate decision on #385's evidence.

#385 completed the experiment. The [suite-level plan](2026-11-19-370-suite-level-selection.md) supersedes this handoff and keeps the promotion hold.
