# #497 pickup review

Independent Grok 4.7 Build Fast review of the pinned C110 pickup at integration base `7f5b3fb62a83f3f04fea6c5a5ceb1bdaeb04ef32`.

PASS

The #497 pickup matches the accepted #471 C110 scope on every checked obligation. No actionable gap.

- The only authored file is `docs/architecture/legacy-sdlc/policy-decisions.md`, with scope taken from `0945941c6c024b6dd621202b2456696ae1df0154`.
- Sibling admission is #494 at `3e08d0b48e884445edee9217b8db9b64cce67afc`, #495 at `053a0516b744d898053cee0e0b86c95f6ec605bc`, and #496 at `7f5b3fb62a83f3f04fea6c5a5ceb1bdaeb04ef32`, and that last commit is the integration base. The legacy pins remain commit `c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905` and tree `844ae26bb169e8618e45fc3b1aedb57f44896fe0`.
- All eight crosswalk decision sets are in scope, including remaining provider and migration questions. Each unresolved rule keeps applicable behavior, source or explicit uncertainty, accountable owner, and earliest pickup gate.
- Typed fixtures cover acceptance and refusal for every group, with input, decision, and reason, and keep migration, hosted-provider, and runtime proof obligations separate as downstream policy outcomes.
- Adopted obligations bind to the reviewed profile. Items that still need project policy or host qualification stay visible. A missing profile result holds at its named gate, and the plan admits no choice that needs a fresh policy approval.
- Draft removal waits on exact-candidate hosted repository CI, with the Core path-filter fallback comparing `packages/aitm-core/`, `pyproject.toml`, `uv.lock`, and `.github/workflows/core-ci.yml` to the latest passing hosted Core baseline and re-checking when any Core input changes. After draft removal, qualification is a fresh Grok 4.7 source SAR on the #497 story PR and a separate fresh Grok 4.7 source SAR on the final trunk PR, each with the trusted verifier and exact literal-target proof, and sign-off waits until the full four-document slice is in trunk.
