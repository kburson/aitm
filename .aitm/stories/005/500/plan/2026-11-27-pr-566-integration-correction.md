# Evidence-only binding integration correction

The first [aggregate source SAR](../../../004/475/plan/2026-11-27-pr-560-16560373-source-sar.md)
found that C16 could acquire evidence authority while C17 could not release it.
[Draft PR #566](https://github.com/kburson/aitm/pull/566) targets the verified #565
integration landing `16560373b2b7056117627d2c23a0f6f5487cd472` from provisioning
head `805c5428650215269cc3ce9bce04ff1c76b70932`.

For the exact holder, `unbind` must close the evidence generation without importing
authored input or updating the planning ref. Wrong worktree or stale generation
must fail. `sync` and `unbind` with explicit authored paths must remain refused.
A fresh planning holder must be able to claim the next generation after release.

#500 stays In review. The correction and the revised aggregate each require
their own exact hosted checks, independent source SAR, trusted verifier, branch
gates, and verified landing.
