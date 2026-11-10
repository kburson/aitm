# #116 manual delivery checklist

## Development checkpoint

Codex owns integration and closure. Branch `codex/aitm-116-monitor-registry` targets trunk at `9b12927da1a368f254537277f7fdc7139f90cc44`. #114 is closed and Done. The pinned base passed all 592 locked package tests. [Reviewed pickup](jit.md) · [Independent review](jit-review.md).

The estimate is M, 4.0 agent-hours, with an explicit two-hour checkpoint. Existing-ledger and newly initialized registration recheck under the writer guard before publishing. Legacy anchor staging and publication share the legacy inbox lock. Opening an existing private inbox is read-only. [Manual checklist](../../../../manual-delivery-checklist.md).

The separate #115 quality hold remains in its own Test record. #116 has no #115 dependency and follows the same required exact hosted quality gate.

### Local implementation checkpoint

Project 24 readback confirmed rank 200, size M, estimate 4 agent-hours, start November 10 and Dev. The locally committed implementation is `d8083f549cc48d097c9666e7a45c61ece66e9313`, tree `faa7e6c3943c0dfd7b142695dcd78a2dd71d0972`, on the reviewed #114 base. Focused verification passed 196 cases. The full local gate passed 634 product and CLI tests and 182 helper tests, with 7,319/8,033 product and 778/821 helper lines covered. Ruff and whitespace checks passed.

Preflight led to the private service namespace for native boundaries, identity-checked proof instances, and independent enrollment of new streams while capture is enabled. Tests cover lease-free snapshot replacement, post-commit cleanup, and exact retry after a registry or inbox directory sync failure. Codex delegated the inbox and legacy compatibility lanes to separate implementation agents and retained both signed handoffs.

The next checkpoint uses the live trunk parent for the story PR and exact hosted validation. #115 currently has a fresh run on its existing head.

### Test checkpoint

[PR #180](https://github.com/kburson/aitm/pull/180) targets trunk base `37a22922f072e39c35434ae645a1c20692b8da01` at head `91dd5852caa9519c7cee7e300ef1cb661e24b02d`, tree `4971d96e969c882fbb16c7183bb6ae9b6cfb4b87`. The final source patch on the earlier base and the rebased patch have the same stable patch ID. The direct disable regression prevents a previously unadmitted stream from acquiring a capture epoch.

Fresh local validation on the exact rebased tree passed 671 locked product and CLI tests and 182 helper tests. Product coverage was 7,844/8,615 lines and helper coverage 778/821. Ruff and whitespace passed. GitHub confirmed the exact PR parent and candidate. Hosted validation is pending.

### Review checkpoint

[Run 42872458320 attempt 1](https://github.com/kburson/aitm/actions/runs/42872458320/attempts/1) passed all six jobs. The delivered verifier authenticated tested merge `ed3f55ce1100a79d867a0fff8a48133ce1227652` with the declared ordered base and head and reviewed tree `4971d96e969c882fbb16c7183bb6ae9b6cfb4b87`. Artifact `13790103040` had archive SHA-256 `be3a37f56c8766513c4cf197b76734ade7bf7909f3386e01e8cd923ac212de6d` and subject SHA-256 `95fd65288674abbfe5b1bcdd21d8fc8d8a3e7fe07db9fcffed3a36d343c055b1`.

Authenticated raw replay kept all 629 baseline tests and added 22 monitor-control, 8 legacy compatibility and 11 registry cases, plus the fixed candidate-only CLI evidence test. Raw product and helper coverage matched the local exact tree. Independent source review is pending.

### Independent source review hold

The [first independent source review](source-review-attempt-1.md) held the exact passing candidate for historical capture fences and permanent rejection on temporarily missing proof. The replacement must persist the current native frontier for each known stream when the writer first arms the command. It then selects the first qualified native boundary after that frontier. Commands remain queued while a required native boundary is unavailable. Preserve the signed earlier CI and review hold. Return to Develop and repeat the exact hosted and source gates for the replacement.

### Capture frontier repair Test checkpoint

[PR #180](https://github.com/kburson/aitm/pull/180) targets the unchanged trunk base `37a22922f072e39c35434ae645a1c20692b8da01` at head `198b75431f5a929ffd7178b2d17e463e717d956e`, tree `8f3aeb384b7b89ae573b5c563bd05f6c30656760`. [Fresh hosted run 42875770798](https://github.com/kburson/aitm/actions/runs/42875770798) is pending.

The writer persists one authenticated native checkpoint per known stream before applying a source-wide change. It uses the earliest qualified native boundary strictly after that checkpoint. Native or locator unavailability leaves the command queued. Restart reuses the same frontiers, and a stream with proof cannot cause partial application while another stream waits. An exact queued command clears its saved frontiers only with the terminal receipt and state change. Direct proofs are bound to the matching armed change and writer instance.

The old head reproduced both failures. The focused repair passed 116 registry, control, legacy and scan tests, including a two-stream restart and physical root substitution. The locked local gate passed 676 product and CLI tests and 182 helper tests, covering 7,952/8,734 product lines and 778/821 helper lines. Ruff and whitespace checks passed.

### Capture frontier repair Review checkpoint

[Run 42875770798 attempt 1](https://github.com/kburson/aitm/actions/runs/42875770798/attempts/1) passed all six jobs. The delivered verifier authenticated tested merge `60817ecbfcb88472533ba0d8e99c4a205aa6d66c`, exact replacement head and tree, and ordered parents on unchanged trunk. Artifact `13790723844` had archive SHA-256 `0ffdf817c6dd0add5c8b005cddad1c617526d44c344886c54073dbcaab850397` and subject SHA-256 `5aae9ec044f05906887f8e8e7ecb677a24cfc187888b7b8c714c26a9662383b8`.

The verifier treats test paths as controls and requires the explicit candidate tree for these accepted test additions. The workflow, verifier, gate policy, package configuration and lock were identical to trunk. With the exact tree input, signed verification passed. Authenticated raw replay retained all 629 baseline identities, validated all 676 candidate tests and matched both local coverage results. The independent exact source re-review is pending.

### Independent capture frontier re-review hold

The [second independent source review](source-review-attempt-2.md) confirmed the repair for completed historical boundaries and transient proof retries. It held the same exact passing tree because an idle or missing previously enrolled stream can indefinitely stall every source-wide capture change on its edge. It also requested physical native ordering evidence for a request in progress when the command arms. Preserve the exact passing signed CI result and both independent holds. Return to Develop before changing the implementation. Verify the prospective, authenticated disposition of idle, missing and in-progress streams before issuing another exact candidate.

The liveness failure reproduced on the exact held source for a quiet stream and a removed stream. The [first liveness pickup review](capture-liveness-pickup-r1-review.md) held the proposed follow-up because an unfinished provider run could still wait indefinitely. It also required a single absolute physical fence rule, typed absence and proof authority, and explicit command ordering. The pickup remains under review before product edits.
