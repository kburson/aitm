# #111 M01 independent design, plan and JIT review

Submitted UTC `2026-11-10T14:14:57Z`.

Verdict **PASS** for the exact compact #111 design, plan and pickup. No required findings.

Independent declared-manual Codex Desktop reviewer, OpenAI GPT-6.1 Sol, high. Provider-qualified reviewer fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287`.

- Fresh full read of `111-jit.md` lines 1–9, SHA-256 `ae03d94bb3e42d810c4b2074a73a0a5645950201d8e3072c078ea761c5a4bee8`. Compared the accepted #100 plan SHA-256 `8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21`, M01 lines 87–94, its host design and the #102 spike boundary. M01 has no implementation predecessor. Independently verified #103 closed and current trunk `9cc3b7b9912245e2ffcfa8b24ffbfa4e32523cc6` with successful trunk run `42830542706`. [Trunk check](https://github.com/kburson/aitm/actions/runs/42830542706)
- M01 owns only the new host boundary and tests and scoped ledger path/guard integration. The delivered code uses `ledger._check_acl` across backup, export, install and scopes, and `ledger._control_root` as the guard seam. The accepted preservation requirement covers those callable seams and their ledger error behavior, plus Darwin's existing ancestry ACL exception and exact physical guard suffix. Keep Linux ACL absence distinct from an unavailable or unreadable capability and retain owner, mode, link, ancestry, inode and pinned-descriptor checks. Use the supplied account UID for a stable Linux guard independent of HOME and XDG.
- Read the three-line Linux probe receipt, SHA-256 `5baef7759c374eda99e9c537401335a451e722a1c4afbc93c914e58c78ccb503`. It identifies aarch64, UID 65534, local ext4 and real access/default absence and inheritance distinctions. The JIT requires repeating the proof through the candidate boundary on the exact #102 pinned image, with only private ephemeral data and no provider credentials. This proof stays scoped to that Linux filesystem/architecture, with native supervision and provider qualification deferred to #129.
- The 2.5 active-agent-hour estimate is within the four-hour cap. Red behavioral tests, the ledger suite, applicable exact macOS CI, both unrounded raw line floors, sanitized Linux proof, independent source review and verified delivery remain gates. Installed production runtime and other stories remain outside this pickup.

No repository or GitHub mutations were performed.
