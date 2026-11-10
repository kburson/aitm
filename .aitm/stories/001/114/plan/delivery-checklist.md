# #114 delivery · November 10, 2026

## Attempt 1

Codex is the implementing agent and closure owner. [Accepted pickup](jit.md), [three review rounds](jit-review.md) and [verified carrier split](linux-carrier-split.json). Predecessor #113 is closed and Done. Target trunk, exact base `dc037364ba617b97244c93670d12358d0b5cbba7`, branch `codex/aitm-114-provider-adapters`. The untouched base passed 220 provider tests and [trunk CI](https://github.com/kburson/aitm/actions/runs/42843355312).

- [x] Review pickup and verify the Linux split and pinned base.
- [x] Record local validation and open the exact PR for Test.
- [ ] Verify all six hosted jobs and obtain independent source review.
- [ ] Verify the delivered tree, publish the signed retrospective and close as Done.

### Test checkpoint

[PR #136](https://github.com/kburson/aitm/pull/136) targets trunk base `dc037364ba617b97244c93670d12358d0b5cbba7`. GitHub read back candidate head `ee74b3f084798cf80404cba3877ba34e6aa55dcd`, with local tree `212a5bc2e6c40154e1016de1b06e50616802b4a0`. Hosted validation is pending.

The initial 16 bridge cases failed on the missing interface, then passed on the implemented path. Two additional restart cases caught cursor advances that would discard an unfinished Codex turn or Claude tool-to-request link. They failed before the hold and passed after it. The adapter keeps unsettled deltas at their previous checkpoint for replay. The actual durable write of cursor plus accepted frontier belongs to the later claim owner. Tests retain the existing #88/#96 native evidence as the source for sanitized fixture shape. Archive copies, unqualified tuples and replay variants are deterministic derivatives.

Final local verification passed 238 focused provider tests, 589 locked product and CLI tests and 182 CI helper tests. Product raw lines were 6,599/7,219 and helper raw lines 778/821. Both unrounded floors, Ruff and whitespace passed. The source bridge leaves the Linux carrier tuples disabled.
