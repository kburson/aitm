# Private input capture implementation plan for #30

**Goal.** Retain a copied verification source and a reproducible identity for the exact tracked candidate and declared extras.

**Architecture.** Resolve a current C16 implementation binding and literal Git branch. Read tracked inputs from the pinned commit tree and copy explicitly declared regular extras through contained paths. Qualify the resulting private directory and its mode and content manifest again before exposing it.

**Spec.** [Accepted C33 leaf](../story.md) · [Accepted #594 proof plan](https://github.com/kburson/aitm/blob/822db73049ca414caf0abe30e485c1a6ffc3c609/.aitm/stories/005/594/plan/2026-11-28-594-findings-scope-proof-plan.md) · [Exact #41 delivery](../../41/retro/2026-11-28-41-delivery.md).

The native rank is 40. The delivered C07 and C16 prerequisites `8d83fccae4fb101a9740257711588f46575c5b45` and `0d626df2d07572e2d925e8340485485b3b637212` are ancestors of verified integration base `0980f174461015f5542ebb4e810cd7b52148393a`, tree `60ccb57dbb8690629a4c9fc33d6e6f5f9347b252`.

1. In `models/verification.py`, define captured entries and a canonical manifest that binds the current implementation holder, exact Git source, committed policy, declarations, and sorted paths, mode and content hashes. Expose its digest and exact candidate as typed C32 inputs for downstream callers.
2. In `verification/capture.py`, create a private export outside every registered worktree. Pin the literal candidate ref, read tracked blob bytes from its tree, reject unsafe and nonregular paths, and expand only declared extra inputs. Enforce output separation and stable extra bytes and membership. Use new files with read-only modes and retain the immutable manifest. Clean up any unpublished partial export.
3. Recheck applicability by verifying current holder, source, policy, extras and exported bytes. This check is read-only so a downstream caller can use it while holding its own launch lock. Later edits cannot change the copy and can make its authority stale. These are captured-export controls. OS containment, the prepared environment and execution remain with their assigned owners.
4. Add one installed Git case for pinned tracked bytes, copied extras, source drift, extra drift, overlap and path refusal. Add focused deterministic manifest tests where they qualify a distinct boundary. Starting fresh hosted collections are Core 1,113 unit and 94 integration, and usage 1,644 unit and 142 integration. Retain both 92% unit floors and the strict independent integration limits.

Use the established draft, hosted qualification, trusted verifier and independent post-readiness source acceptance sequence before verified landing. This pickup is manual bootstrap evidence. Runtime transition and implementation clock are both false.
