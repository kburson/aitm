# Story #457 delivery report

The delivered scope is session-owned capture, exact recovery, immutable attribution, and protected story publication. The live agent holds the selected story, and the caller records or reconciles only its own and its explicitly supervised turns. [Accepted design](../design/2026-11-25-session-owned-turn-capture.md).

| Scope | Qualification |
| --- | --- |
| Codex Desktop composer | Owner and child callbacks arrived and retained both terminal observations. The pending callbacks replayed after switching to #458 in fresh processes. Both complete receipts stayed byte-identical under #457. |
| Codex app-tool forwarding | Native owner and child turns completed. No owner start reached the wrapper. This route has exact retained-record recovery coverage. |
| Supervised launches | Automatic and exact delayed recovery observed on Codex headless, Claude Code and Grok Build on macOS. The bounded Codex launch enrolled a review role. |
| Sealed cross-provider review | A sealed Claude decision was associated with the exact enrolled native usage via the existing manual broker. Automatic broker transport and Codex sealed-decision coverage retain their documented gaps. |
| Planning publication | One real #457 receipt was written to protected planning and read back. Identical replay made no remote change. Concurrent writers, lost acknowledgements, conflicts, and privacy also have fixture coverage. |

[Desktop evidence](457-desktop-forwarded-route.md) · [Native routes and overhead](457-route-readback.md) · [Protected publication](457-remote-publication.json) · [Sealed-review qualification](457-aipr-qualification.json).

Agent-owned retry and publication at normal story closeout are tracked in [Spike #461](https://github.com/kburson/aitm/issues/461). Use a nonblocking capture wrapper so telemetry errors cannot cause an agent turn to repeat. The scratch hook qualification applied only to the disposable project.

## Exact-source review

Claude Sonnet 5.5 at medium effort reviewed candidate `1c2df261c19059f653733f2f378743249f32621d`, tree `4c377b61362ec7151c52bc9e60038373f2128c97`, against `trunk` at `1956fecf716e06236a9741afc0a3e49643835e1e`. Verdict **Approve**, with no blockers. Findings recorded on the PR cover terminal hook exit 2, replay with late optional rate evidence, and conflicting terminal callback types. The reviewer inspected the source and tests. Hosted CI and the implementer's local test run are separate validation. The first Claude launch stopped before inference because bare mode did not read the existing subscription credentials. The single restricted-mode recovery succeeded.

[Review and inline findings](https://github.com/kburson/aitm/pull/460#pullrequestreview-6066759346) · [Hosted CI](https://github.com/kburson/aitm/actions/runs/45700767103) · [Three-platform effort checks](https://github.com/kburson/aitm/actions/runs/45700766851).

## Verified delivery

The local package suite on the exact reviewed source passed 1,695 tests with one skipped. All nine hosted checks on the exact candidate passed. [PR #460](https://github.com/kburson/aitm/pull/460) merged normally into `trunk` at `87bc3d8a2875884014b59281117f68b9d63fabee` at 2026-11-26T00:09:28Z. Remote readback and Git object inspection verified the ordered base and reviewed-head parents and the exact reviewed tree.
