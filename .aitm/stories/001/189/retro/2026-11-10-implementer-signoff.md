# #189 implementer retrospective and sign-off

Signed by Codex, assigned #189 implementer, at `2026-11-11T04:05:03Z` for attempt 1, candidate 1, on 2026-11-10 America/Chicago. Delivered verdict is pass, with high confidence in the reviewed #181 A04 scope.

I verified that [PR #212](https://github.com/kburson/aitm/pull/212) landed on trunk at [`f7646bc4da35173e9b0e468e4810b4e9265b0f47`](https://github.com/kburson/aitm/commit/f7646bc4da35173e9b0e468e4810b4e9265b0f47) at `2026-11-11T04:04:09Z`. The merge parents are `e4701f2e89d34f93f13d717199254b66aa3f0457` and `ae937d4e8aaba9813b3ac9b57a36d7baa2b8f0e0`, in that order. The merge tree `2f4a860a0058ede02d48b4d9a048787553f9c720` matches the independently reviewed and signed hosted candidate. The first-parent change contains only the two authorized usage files.

The delivered projector selects one fixed report, checks the named operator's exact receipt registration and the independent source and sanitized payload digests, and uses A01's ancestry for exact direct and inclusive USD totals. The tests show that a report switch, revision conflict or missing price affects Cost according to its own evidence, and that timing-only gaps leave Cost unchanged. The exact candidate passed eight usage tests, all 29 dashboard tests, Ruff lint and format, and the delivered verifier for [hosted CI attempt 1](https://github.com/kburson/aitm/actions/runs/42955953124/attempts/1). The independent source review accepted both files.

The first pickup draft treated a separately declared export digest as optional. Independent pickup review caught the gap. I corrected the draft before implementation and added the A01-admitted reference-only regression. My first rollup fixture gave one descendant two parents. A01 correctly held that edge, so I repaired the fixture and asserted the expected graph before testing the rollup. In future receipt work, test a source that passes intake yet fails the measure's assurance rule, and assert the fixture's admitted ancestry before exercising aggregates.

Implementer checkpoint bounds are partial. I recorded planning activity at `03:44:03–03:46:03Z` and `03:49:04–03:49:16Z`, and implementation and local verification at `03:50:55–03:56:02Z`, all on 2026-11-11 UTC. These are observed checkpoints and exclude waiting between turns. Full engagement, review time and calibrated Actual remain Unknown.

I sign off on the exact delivered source for #189. [Delivery checklist](../plan/delivery-checklist.md) · [Independent source acceptance](../plan/post-ci-source-review.md)
