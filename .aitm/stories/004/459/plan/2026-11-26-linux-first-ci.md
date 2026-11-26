# #459 Linux-first delivery direction

The owner directed Linux as the default CI gate, limited macOS and Windows
checks to changes that require their behavior, and directed #459 delivery
without waiting for hosted macOS. That direction supersedes the prior
portability hold for this story. The approved Core exporter scope and
the unchanged receiver fixture remain the basis for qualification.

[PR #463](https://github.com/kburson/aitm/pull/463) carries the implementation and the revised policy.
Its ordinary Ubuntu gate and Ubuntu installed-wheel suite must pass.
Windows runs a small installed CLI and byte-preservation lane for the changed
CLI boundary. The native macOS job only selects native filesystem changes.
The existing local Mac wheel and native tests are supplemental evidence.
The user-facing rationale is in [Platform requirements](https://github.com/kburson/aitm/blob/ffc99fd72e81eac2acdb50f63b12ce128275a690/docs/platform-requirements.md).

Verify the same head and base, independently review the CI and docs delta, and
authenticate the signed Ubuntu result before merging. Run the #461 proof with
the delivered wheel and verify the final story, PR link and Project status.
