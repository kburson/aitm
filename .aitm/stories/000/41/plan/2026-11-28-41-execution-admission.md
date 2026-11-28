# Single-use execution admission implementation plan for #41

**Goal.** Admit one execution against the exact attempt and source, order a stop against launch, and retain diagnostic results before deciding whether they can be effective.

**Architecture.** Use ordinary C09 operations for preparation, admission and the single-use launch claim. Use the current C16 clone-local binding and an authoritative C31 preflight before each launch-capable mutation. Retain cancellation and result observations as exact execution-scoped writes, then invoke the installed preflight with retained activity before exposing a successful result.

**Spec.** [Accepted C32 leaf](../story.md) · [Accepted #594 proof plan](https://github.com/kburson/aitm/blob/822db73049ca414caf0abe30e485c1a6ffc3c609/.aitm/stories/005/594/plan/2026-11-28-594-findings-scope-proof-plan.md) · [Exact #40 delivery](../../40/retro/2026-11-28-40-delivery.md).

The native rank is 30. #17, #21 and #40 are Closed/Completed. Their landed commits `30552dd22c88167887da6b89f0d4b453aba77a37`, `0d626df2d07572e2d925e8340485485b3b637212`, and `318f6d116ef4260c1723f94d4078ee7903231425` are ancestors of the verified integration base `318f6d116ef4260c1723f94d4078ee7903231425`, tree `488541686f04aa82465ac83fe2fdc5fe4377bc0f`.

## Decisions and proof

1. Add a typed optional execution candidate to the C55 receipt. The existing source remains the attempt and binding baseline throughout every phase. The new field pins the exact live branch commit and tree and the optional capture manifest digest. Preserve prior receipts, and have the reducer reject changing, removing or adding the candidate across phases. A captured-input caller must supply a qualified exact-input check at dispatch and result readback. C33 owns capture and C35 owns actual verification execution, platform lanes, output handling and containment.
2. Build the installed coordinator in `execution/admission.py`. Validate the current exact binding, source, request, authority ref and attempt generation. Write prepared and admitted facts under one exact planning CAS. Require verified shared publication or the anchored local-only CAS. Check the same address and request on every later read. A stale or offline shared clone gains no start authority.
3. Put transport-neutral launch and retained-result handling in `execution/executor.py`. Use the existing clone-local binding lock for the final cancellation check and process creation. Commit the single-use launch claim before any external effect and check freshly observed authority immediately before invoking the executor. Never launch again after an ambiguous claim or result. Record exact cancellation and diagnostic observations without moving workflow or clock state. A successful result is effective only after the installed C31 check has consumed retained result and activity observations.
4. Add failing proofs before each implementation step. Use one installed Git case for both stop/admission outcomes, the stopped stale/offline clone, and the local-only path. Use deterministic cases for legacy/new receipt decoding, incompatible candidate/manifest and repeats, cooperative cancellation ordering, ambiguous launch/result observation, and effective result versus overrun. Reserve real subprocess and containment proof for the accepted C35 owner. Preserve both hosted Linux 92% unit floors and strict per-package integration limits. Starting collections are Core 1,111 unit and 93 integration, and usage 1,644 unit and 142 integration.

Run affected C55, C09, C16 and C31 tests plus Ruff. Keep any PR draft until both exact hosted qualifications and the trusted verifier pass. Require the complete exact independent post-readiness Grok review, trusted reviewed-tree verification, branch checks and Git/GitHub landing readback before close.

This pickup is manual bootstrap evidence. Runtime transition and implementation clock are both false.
