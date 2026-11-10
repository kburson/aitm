# #105 pickup · Verify canonical PR evidence

Use the reviewed [leaf plan](implementation-plan.md) and [binding amendment](../../104/design/github-tested-merge-binding-replan.md). The owner authorized ordinary Full-Auto delivery including the reviewed public attestation workflow. Work on `codex/aitm-105-ci-verifier` in a fresh dedicated worktree, from exact trunk `58fb8ba98c52c1409f85c58d24dd7da86a583c0a`. Recheck live trunk and #104 Done before Develop. Its exact signed production run establishes the trusted CI1 baseline.

Implement the read-only verifier, meaningful cases and the required helper scope. Use the exact production archive fixture from [CI1](https://github.com/kburson/aitm/actions/runs/42819951099/attempts/1) and the delivered policy. Validate wrong source, event, workflow, invocation, identity, freshness and job state independently. Preserve the 90% floor. Use manual exact CI readback for the verifier's own protected PR and independent source review after hosted validation.

The unmerged docs-only [proof PR #108](https://github.com/kburson/aitm/pull/108) and exact refs are handed off after #104 closes. Within the reviewed Full-Auto scope, retarget that proof to trunk, update its disposable head against the delivered verifier merge and confirm a fresh exact pass with the trusted copy. Retain the evidence, close the proof unmerged, and remove only the two named proof refs when safe. Sign off and close #105 at its last gate. The 3.5 active-hour estimate remains separate from hosted queue time.

#104 is verified Done and closed on planning `feddc9f`. The handed-off proof currently has base `afbaf6e93ab1ad57a312b06a75b0d09029b9409a`, head `f780f875986e95bd654c0553c574c336f728a4fa`, and signed run `42821747864/attempts/1`.
