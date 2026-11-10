# #111 delivery · November 10, 2026

The [source PR](https://github.com/kburson/aitm/pull/130) targets trunk at `9cc3b7b9912245e2ffcfa8b24ffbfa4e32523cc6`. Candidate head `f1273a521259162219ea680737c3b4bf3f897141` and tree `11c4e3d02b8c71ed411910f82a8732283f0d2b82` contain only the host filesystem module, ledger path and guard adapter, and their tests.

Focused tests passed 86 cases and the full local package passed 547. Ruff and whitespace checks passed. The exact source accepted an absent ACL and rejected an explicit access ACL, an inherited default ACL on a mode-0700 directory, a symlink and a wrong-owner directory. The direct Linux probe used an isolated local ext4 volume, aarch64 Linux `7.0.12-linuxkit`, UID 65534 and the #102-pinned Python image. The same UID resolved the same guard under HOME and XDG overrides. The test volume was removed. [Linux spike baseline](../../102/attachments/report.md)

The canonical [hosted run](https://github.com/kburson/aitm/actions/runs/42833278554) is the next check.

The local coverage run passed 548 tests including the CLI subprocess check and measured 6,336/6,956 raw product lines. The exact hosted attempt passed all six jobs. GitHub reported tested merge `be723e6499f724aeeec24c9dc38af09181498db7` with the expected tree and ordered parents. [Passing attempt](https://github.com/kburson/aitm/actions/runs/42833278554/attempts/1)
