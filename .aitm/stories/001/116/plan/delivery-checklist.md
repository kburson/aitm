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
