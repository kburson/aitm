# #13 pickup review round 2

Standalone read-only Grok 4.7 on planning publication `59b3f6a971e1584a1367abc09ab5d2f8f5e5e990` and pickup SHA-256 `2b362aa93a0bf4f36dde2002a3aa4915f6ae4a1e6753d91c43135e62f17f47e5`.

CHANGES REQUIRED.

The continuity matrix, exclusion proof, real-versus-unit split, unchanged C07 parser, and the narrow validation-route plumbing match the accepted C08 contract. The stated plan basis does not.

The exact planning revision for this review is `59b3f6a971e1584a1367abc09ab5d2f8f5e5e990`. The pickup instead names `0945941c6c024b6dd621202b2456696ae1df0154` as the accepted plan basis. It also records the initial publication `c8e10c1e70afb8b253674b244fce6643d6e77cfb` and the integration base `18cddc2f2715cf19a2d27d8a8e78fc00c23f5f5d`. Those are different objects. The #546 parent tie to the #12 landing `8d83fccae4fb101a9740257711588f46575c5b45` and the remediation parent `d1a736f0d7ed0dee9c0bfcc3e19c58aa186b87f6` is now stated, and C06 (#11) and C07 (#12) are named Depends-on links, with C07 carried as the shared-file predecessor for `services.py`. The plan pin itself is still the wrong SHA.

What the revised text does satisfy:

- `observe_shared(anchor, observation) -> SharedFrontier` and `refresh_refs(policy) -> RefreshResult` stay the produced contracts. A receipt cannot supply the anchor or policy. Input trust, remote candidate, local writer tip, last content-valid tip, and shared frontier stay distinct.
- Rollback, sibling, deletion, and unprovable ancestry fence shared publication and keep both histories. Unpublished local divergence stays reconcilable. An invalid descendant is a retained checkpoint and not a writer base. Repair must extend that checkpoint through the existing C06 verifier; the C10 repair producer stays out. Crash CAS, corrupt or partial journal, missing-journal integrity hold, and the first-clone rollback limit are all required proofs.
- Code and planning use distinct configured remotes. Planning that shares anchored code-default ancestry is refused, as is an unknown genesis with a familiar trailer. The pin set is policy revision and effective settings, code head(s), planning revision and tree, consulted story and path versions, and fetch status. Stale last-valid policy stays local with shared effects pending. Unknown evidence and route or integrity mismatch do not authorize shared use. Cached reads do not fetch. Local-only uses the committed default.
- Fetch-view admission is under the clone-common C06 lock on the literal planning target: inventory from the code clone’s Git common directory immediately before and after ref CAS, refusal of a checked-out target, both refs retained, and a fence that keeps the checkout, index, and unsynced bytes. Reconciliation stays explicit, with no reset and no automatic index repair. Supported serialization and the detected out-of-band checkout are both required. In-flight refresh is retried outside the guard.
- Continuity and freshness decisions are unit proofs. Fetch, ref admission, recovery, and separate remote topology run against Git. The installed command proof is `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c08.py -q`, plus affected installed Core suites, the unit floor, and Ruff.
- C07 committed-policy parsing and the C90 parsing boundary stay as delivered. The current `("planning", "validate")` handler has only `--anchor`, `--repository`, and `--tip`, so it has no refresh ingress. Adding `--refresh` and a service preflight call on that existing route, while plain validation stays the same, is the accepted installed-command proof. It does not add a command or a model. Story-edited settings remain unusable, and trusted installation coordinates stay separate from the worktree. The repair stub stays fenced.

The only required change is to pin the plan basis to `59b3f6a971e1584a1367abc09ab5d2f8f5e5e990` and to keep the integration base and its stated parents labeled as the integration base.
