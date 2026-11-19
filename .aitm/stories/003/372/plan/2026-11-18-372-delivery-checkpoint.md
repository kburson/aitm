# #372 delivery checkpoint

- [#377](../../377/retro/2026-11-18-377-delivery.md) is delivered and closed. The required Python jobs run on Ubuntu 24.04 with CPython 3.13.9. The existing exact-base, coverage, child-process, and attestation gate passed before merge. The Ubuntu trunk push also passed its required checks.
- [#373](../../373/retro/2026-11-18-373-delivery.md) passed independent review, the Ubuntu PR run, the trusted verifier, and post-merge verification. [PR #380](https://github.com/kburson/aitm/pull/380) delivered the physical custody proof.
- [#374](https://github.com/kburson/aitm/issues/374) needs an explicit product decision about externally launched Grok. The service supervisor can authenticate and stop a child it owns. The current Grok marker path also verifies an external process's incarnation and executable in both admission and the hook. A service PID file cannot authenticate that external ancestor. Keeping that workflow requires a separate platform-backed process identity path. Requiring a managed launch changes which Grok sessions can mark scope.
- [#375](../../375/retro/2026-11-18-375-acl-verification.md) passed verification on the existing trunk ACL implementation. It preserves the ancestor-only stock Darwin ACL, refuses grants and inconclusive reads, and retains the existing control roots.
- [#376](https://github.com/kburson/aitm/issues/376) retains the recorded sequencing constraint for the local launcher. [PR #369](https://github.com/kburson/aitm/pull/369) is still open.

The epic remains open while the supervisor, ACL policy, and launcher work are pending.
