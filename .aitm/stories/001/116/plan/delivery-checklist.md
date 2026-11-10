# #116 manual delivery checklist

## Development checkpoint

Codex owns integration and closure. Branch `codex/aitm-116-monitor-registry` targets trunk at `9b12927da1a368f254537277f7fdc7139f90cc44`. #114 is closed and Done. The pinned base passed all 592 locked package tests. [Reviewed pickup](jit.md) · [Independent review](jit-review.md).

The estimate is M, 4.0 agent-hours, with an explicit two-hour checkpoint. Existing-ledger and newly initialized registration recheck under the writer guard before publishing. Legacy anchor staging and publication share the legacy inbox lock. Opening an existing private inbox is read-only. [Manual checklist](../../../../manual-delivery-checklist.md).

The separate #115 quality hold remains in its own Test record. #116 has no #115 dependency and follows the same required exact hosted quality gate.
