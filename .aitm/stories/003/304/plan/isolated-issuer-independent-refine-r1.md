[22:36:06]
REFINE_304: PASS

This pass is for the bounded design only. Nothing below is discharged at Refine. The independent JIT that comes next must meet all of these obligations, or yield a named held mode instead.

**Viability.** #303 is closed and gives the issuer a place to plug in. `_LiveProfile` carries `root`, `lease`, `generation`, `installations` and the `current` checker. `_require_live_source` refuses unless the lease matches, the root and directory are pinned, the tuple is supported, `source_key_id` is present, both SourceRefs validate, `current(installation) is True` and the profile is unchanged after the check. Claude is absent from `_TARGETS`. The issuer only has to fill these slots with real proof, so it is a bounded private addition.

**Size.** 3.5h under the 4h cap is viable only if the sole real positive run is Grok CLI on macOS arm64. That run uses 1.0.77 build 50ca579fa996, whose digest matches #115, with an owned launch. The denial and revoke controls run hosted with the real issuer and injected host evidence. The supplied evidence does not support counting anything more in the estimate:
- There is no evidence for any Codex surface.
- There is no authenticated Linux Grok carrier (#115).
- There is no Linux process-identity primitive. The only one shown is macOS libproc.

**Binding JIT obligations**

1. **Mode scope.** JIT must name macOS Grok CLI as the one real-run positive mode. Codex desktop macOS, Codex CLI Linux and Grok Linux stay closed unless JIT re-sizes them within the cap. Each one closed needs a named held mode and the proof it still requires. Docker's Linux arm64 server is only a test host. It is not the R2 Linux host, and nothing should count as passed without a run.
2. **Executable identity.** `install._process_identity` returns `proc_pidpath` followed by `resolve(strict=True)`. It does not prove which file was opened, and it does not bind the result to a digest. JIT must name the source that binds the launched process image to the digested file. For example, compare the text vnode's dev/ino with an fstat of the descriptor that was hashed, and recheck after exit. Otherwise it must use a private copied binary executed from runner-owned custody. With no `fexecve`, hashing by path and then launching by path does not count as proof.
3. **Build binding.** `_LiveSourceTuple.build` comes from the caller-supplied `request.client_version`. The issuer must build `_InstallationProof.source` and `.executable` from the authenticated executable identity, never from the approval. A tuple that matches only by its version string must be refused.
4. **Producer corroboration.** For Grok macOS, JIT must name the native `hook_execution` → `turn_completed` join under a one-use runner nonce and a fresh private capture root. That root must be tied to the owner, writer and generation. If JIT uses descriptor provenance (`PROC_PIDLISTFDS` / `PROC_PIDFDVNODEPATHINFO`) instead, it must show that this proves the enrolled carrier was written by that process, not merely held open by it.
5. **Currentness position.** The supplied code shows `current(installation)` only inside `_require_live_source`. JIT must cite the exact reserve, commit and retry call sites and show that each runs inside the writer transaction with a fresh, synchronized currentness read. It must test revoke-before-commit and revoke-before-retry. If the checker is unavailable or raises, the result must be a refusal with an exclusion decision. Today `RuntimeError` and other exception types outside the caught set bypass the decision path.
6. **Routing and privacy.** JIT must name the files and functions involved and the single controlled-run route that installs the isolated profile. It must show that normal constructors and installed service entry points cannot reach it. Private evidence and raw transcripts stay in runner custody and stay out of hosted artifacts.

The gates stay in place: a real controlled positive run before delivery, signed hosted Test, independent source review, merge and Close. Final native signed receipts and catalogs remain with #128 and #129. Production stays without an enabling catalog.
