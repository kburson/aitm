# #193 Design, Plan and JIT

The [accepted #181 design](https://github.com/kburson/aitm/blob/b99085f44c8c1f0a5acf5b1fbae02e834f4416fa/.aitm/stories/001/181/design/story-timing-dashboard-design.md) and [B02 plan](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L104) govern #193. Parent plan SHA-256 `147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80`, B02 section SHA-256 `834894299283f0fe9988e868ecbd95520ed1f1b1c5fd57f72f646106d086fa81`.

## Design

Own only `tools/story_dashboard/README.md` on trunk and scoped #193/#181 qualification evidence on planning. The quick start gives commands for the delivered A05 snapshot and B01 renderer, Python and complete Git inputs, expected local output and validation digests, opening offline, verifying filters and refreshing with new pinned inputs. Preserve timing provenance and coverage in the guide. Use the historical parity pin and the exact post-A06 capture pin. Keep outputs outside the tracked checkout and record no private payloads. The parent’s production integration remains a separate open scope.

## Plan

1. In a separate clean checkout of the delivered tool, resolve both fixed planning objects and exact as-of values. Run snapshot and render commands from the guide. Compare the old seed JSON from two clean runs, verify snapshot digest binding, inspect the new receipt effect, and retain evidence with only safe paths and digests.
2. Open each HTML file offline in an isolated browser. Exercise epic, state and coverage filters, child and epic details, timing and usage evidence-through, #111 scoped elapsed and Unknown Cost. Verify refresh from the later pin and check that no automatic requests or raw/private payloads escape.
3. Publish the reviewed quick start and sanitized qualification evidence. Deliver with exact local verification, signed hosted checks, independent source review, verified merge and implementing-agent sign-off. Close and verify #193.

## JIT

The verified prerequisites #191 (https://github.com/kburson/aitm/pull/220, merge `aa7dff45156919bcbe34d0489335949259bc584a`), #192 (https://github.com/kburson/aitm/pull/221, merge `fec3d8f685fd1d133bb9797d47c02552805e6bc1`) are Closed Completed, recorded as Done on planning `879a62c0df400ca602d52e867d44c7430d3185fe`, and their exact merges are ancestors of trunk. Clean branch `codex/aitm-193-dashboard-handoff` is bound to current base `fec3d8f685fd1d133bb9797d47c02552805e6bc1`. A read-only inventory of #100 and #133 worktrees, tracked diffs and open PR paths confirms no overlap. Scoped source paths are `tools/story_dashboard/README.md`.

The coordinating Codex agent owns implementation at 2.25 agent-hours including verification and review, within the four-hour limit. Owner authorization covers this child. Record independent acceptance and Develop before tracked writes. Recheck scope and exact base before merge and retain superseded evidence if they change.

The verified #191 pilot publication and #192 browser artifacts are the downstream qualification inputs. Deliver the local dashboard handoff and retain the separate slice C integration checkpoint on #181.
