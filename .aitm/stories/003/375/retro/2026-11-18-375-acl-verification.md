# #375 ACL verification

**PASS on the existing trunk implementation.** Verified commit `ac756be7ce8b94ec76d84a430991e566cf23da12`, tree `d87bedbdb5e79c8e70a64e8642e92d6e526aa848`, with CPython 3.13.9. The [exact hosted Ubuntu trunk run](https://github.com/kburson/aitm/actions/runs/44451723759/attempts/1) passed its required jobs. This story changes planning and records verification evidence.

| Platform | Fresh focused checks |
| --- | --- |
| macOS | 22 host-filesystem and opt-in native ACL tests passed. Five selected ledger and backup ACL tests passed. |
| Ubuntu 24.04.5 LTS, non-root | 19 host-filesystem tests and five selected ledger and backup ACL tests passed from a Git archive of the exact trunk commit. |

The host-filesystem run covered missing and present Linux access and default ACLs, descriptor checks, unsupported or unreadable ACL inspection, and account-derived control roots. The custody tests covered private state and backup refusal. On Ubuntu, the grant fixtures applied real kernel ACL xattrs. The Darwin runs checked ACL-free and deny-delete cases and exercised the native grant refusal on a private file and an ancestor.

## Darwin ENOENT

On a private ACL-free mode-0600 file, Darwin libc returned a null ACL with `ENOENT` through both `acl_get_link_np` and `acl_get_fd_np`. The ledger accepted the existing path, and the ACL helper accepted its open descriptor. A separate missing path produced the same native result, and strict ledger validation refused it.

In four injected timing cases, a test temporarily renamed the leaf or ancestor out of the way immediately before calling the real Darwin ACL reader. The probe left the path missing or put a distinct inode in its place before returning to ledger validation. The ledger refused all four cases at the lookup or identity recheck. Separate fault injection with `EACCES` and failed ACL text conversion exercised both the path and descriptor readers. The unavailable Darwin reader also refused validation.

The [linked plan](../../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md#acl) now describes the verified contract. The production behavior already meets the revised story.
