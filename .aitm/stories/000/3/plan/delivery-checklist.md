# #3 Delivery checklist

Attempt 1. Implementer and closure owner are this Codex delivery agent. [Accepted pickup](2026-11-27-pickup.md) · [Grok 4.7 pickup review](2026-11-27-pickup-review.md) · [#83 activation receipt](../../83/attachments/activation-receipt.json).

- [x] Opened [draft PR #526](https://github.com/kburson/aitm/pull/526) from `codex/core-3-foundation` to `codex/core-470-integration`.
- [x] Verified base `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67`, head `c71dcc263505bb7b9f3ca19c3750ad1c3f15c2e2` and clean source tree `1955953ea2569f3a97bb288f90ae17b59cd1ac70`.
- [x] Ran locked local package tests and Ruff under Python 3.13.9 and uv 0.10.6. Four Core tests passed, including the installed wheel and unit isolation probes. The pre-implementation run failed on the missing package and test isolation files.
- [ ] Verify hosted Core CI for the exact candidate. The existing CI workflow exercises the usage package and tooling. The accepted pickup holds draft removal for a hosted run that exercises Core on the exact base and head.
- [ ] Remove the draft state after passing hosted evidence. Obtain Grok 4.7 source SAR against the passing candidate.
- [ ] Verify merge to the integration branch, publish delivery mapping, sign-off and Agent Cost, and close the issue and Project item.
