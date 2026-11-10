# #111 M01 implementer retrospective · November 10, 2026

**Verdict: Delivered.** High confidence in the reviewed host filesystem boundary. Attempt 1 delivered `f1273a521259162219ea680737c3b4bf3f897141`, tree `11c4e3d02b8c71ed411910f82a8732283f0d2b82`, to `trunk` in merge `c0371cc2363c1e95892fdcad75aa20181abeba20` at `2026-11-10T14:27:25Z`. The merge receipt records the pinned base and exact candidate as ordered parents and the reviewed tree. [PR #130](https://github.com/kburson/aitm/pull/130)

- I kept the Darwin ACL classification and guard suffix, with the ledger retaining its ownership, inode and descriptor checks and `LedgerError` behavior. Linux checks access and directory default ACLs separately, admits only explicit `ENODATA` absence, and resolves the guard under the UID account home at `.local/state/aitm-usage-control`.
- The regression suite recorded 14 failures and three preservation passes on the base. After implementation, all 86 host security and ledger tests and all 547 macOS package tests passed locally. Ruff and the staged diff check passed. Independent source review passed on the first candidate. Signed hosted attempt 1 passed all six jobs and both raw line floors, with 6,336/6,956 product lines and 778/821 helper lines. [Hosted attempt](https://github.com/kburson/aitm/actions/runs/42833278554/attempts/1)
- The macOS tests supplied Linux syscall outcomes through a test double. The separate real arm64 ext4 run under UID 65534 supplied the kernel evidence for ACL absence, access and default ACL refusal, inheritance, symlinks, foreign ownership and stable UID resolution. I would keep both checks for future filesystem changes. The portable suite distinguishes error paths precisely, while the native probe checks what the kernel actually reports.

Active implementer engagement and provider cost are Unknown.

Signed by `/root/monitor_m01`, Codex Desktop implementing agent, at `2026-11-10T08:28:11-0600` (America/Chicago).
