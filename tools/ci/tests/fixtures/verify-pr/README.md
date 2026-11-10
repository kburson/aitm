# Canonical PR verification fixtures

The exact public production bootstrap archive is from
[PR #107, run 42819951099 attempt 1](https://github.com/kburson/aitm/actions/runs/42819951099/attempts/1).
Its SHA-256 is `bd0e2e77ae36c181fc4492ff9876f7bff2deb5e623029f46359ebc2258b20bc6`.
It exercises real signature verification without pretending that a merged PR
is still open or that its diagnostic base contained delivered CI policy.

The proof archive and sanitized API snapshot are from open
[PR #108, run 42821747864 attempt 1](https://github.com/kburson/aitm/actions/runs/42821747864/attempts/1).
The raw archive SHA-256 is `2069dbd8a0f92f66c660bb7c901871e23ac8f5f6908b33f88c1e352ef01f30f3`.
The API snapshot retains public identifiers and the inputs checked by the
verifier. It omits unrelated response fields. Each endpoint exercised by the
paginated transport has a list of page documents. The pinned public trusted
root is used only for offline fixture verification. Production resolves
trusted roots independently through the pinned GitHub CLI.
