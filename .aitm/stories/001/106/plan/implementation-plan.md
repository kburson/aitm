# #106 implementation plan · CI3

> For the authorized source pickup, use test-driven development and independent source review. A fresh JIT and the delivered #105 verifier precede development.

**Goal** Run predictable maintained file quality checks and expose future TypeScript applicability without losing any existing gate.

**Spec** [Leaf design](../design/design.md) · [Accepted parent plan](../../103/plan/implementation-plan.md#ci3--lint-repository-files-and-define-the-typescript-lane).

**Estimate** 2.5 implementation agent-hours. The exact file baseline, package applicability and tool pins must be confirmed at pickup.

- [ ] Record the exact trusted target file inventory and baseline dispositions. Pin the Markdown and YAML tools and their locks under `tools/ci/file-lint/`. Reuse the pinned actionlint. Record an exact exception list and reason for each otherwise maintained historical or fixture path.
- [ ] Add meaningful failure fixtures before implementing `tools/ci/file_checks.py`. Exercise duplicate-key/malformed JSON, declared schema mismatch, bad YAML, invalid workflow semantics, a Markdown rule, exact fixture exclusion, and a future product TypeScript package missing required tools. Check the absence case emits an explicit not-applicable result.
- [ ] Independently review the exact additive workflow and policy diff and record owner disposition before the push. Add the portable Linux file job and make it required alongside every existing lane through the single aggregate predicate and the reviewed control change recognized by the delivered trusted verifier. Prove the actual gate refuses a missing or skipped file job with otherwise green evidence. Include the new executable in the 90% helper denominator and run the full applicable tests. Document lock/command choices and the future ESLint, `tsc --noEmit`, Vitest and unrounded 90% V8 line floor.
- [ ] Verify actual failure and corrected exact canonical PR evidence with the delivered #105 verifier and a manual readback for #103 parent acceptance. Obtain independent source review, verify protected delivery, write the implementing-agent retrospective, and close #106 immediately when its own final gate passes.
