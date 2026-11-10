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
