# Story #264 Plan same-provider review, round 3

**Decision — ACCEPT** the exact Plan revision identified below. SPR R1-F004 is resolved. No required Plan revisions remain.

## Review evidence

- Read physical lines 1–121 in full, including blank lines, of `.aitm/stories/002/264/plan/dependency-maps-implementation-plan.md` in the isolated review worktree. Supplied candidate commit `e9347ea43609adde86483b16d103c66df4fdf15e`. Independently computed raw SHA-256 `b82e504caa40e83ee3d7384bfd214678eb97aced688f06ec99b521c596dfd012` and rechecked it at submission.
- Reread [SPR round 2](264-plan-spr-2.md) physical lines 1–38. Rechecked the cited accepted Design digest `50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7`.
- Compared the revision with the previous complete retrieval. Reversing the four changed lines reproduced the exact round 2 SHA-256 `01d990bf16e400a6de2e56a5d88467b76c4aa3b56583920e913101f92e71aa5f`. The changed physical lines are 43, 62, 113 and 114.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 15:18:06 UTC and was submitted 2026-11-12 15:18:51 UTC.

## Disposition

- **SPR R1-F004 resolved.** Line 114 withdraws the entire prior graph, text, audit and detail surface as soon as the project or visibility context changes, until a snapshot is admitted for the new context. Only the internal selection key survives the pending interval. A story must be visible in the admitted snapshot before selection is restored. Line 113 requires a pending-transition assertion covering prior graph, text, audit, links and details before the refresh completes. Same-context authorized fallback and the hosted audience rule at line 120 remain in force.
- **Reader integration preserved.** Line 43 makes the dependency field capture opt-in. Existing callers retain their current canonical path and header field behavior. The dependency adapter still applies the existing cutoff, duplicate-key rejection and lifecycle fold.
- **Conformance preserved.** Line 62 separates simulated scan and unresolved-record input from expected directional coverage. Both adapters still exercise the production admission boundaries. Lines 66–67 and 91–92 retain shared results, synthetic failure cases and parity reruns.

The other SPR findings remain resolved, and the four native XPR round 1 findings remain addressed as recorded in round 2. The linked follow-on stays outside the accepted 13-item M6 scope and retains the separate static, local and hosted gates. This accepts the Plan text. Fixture execution, released-contract verification and item-specific JIT remain implementation pickup or qualification work. The native reviewer owns the XPR disposition.
