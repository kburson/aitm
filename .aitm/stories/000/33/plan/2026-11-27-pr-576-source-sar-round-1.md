# First exact sar for #576

The coordinator reproduced the findings and revised the candidate. Packet SHA-256 `1a02d364817b0e93ec925a76270960ff7e9483861f7011b59d244395ba5ec072`.

CHANGES REQUIRED
c49b535d522f7fca1b8e5c6038b1783993e1c012 765ed43dc126d2580597a2ff36a46878f943af2e 7b972795c957c2d0e7b5024c16597f74598954ce 4c1a6a4452574f8b0e1c447e4872b20cd4dc523a

Accepted originals stay immutable: nofollow reads, one manifest, draft/blocked/round-cap refused before anchors, fingerprints kept, `started_at` and extra handle fields ignored, revision `b…` held apart from finalization `c…`, and reviewer inputs git-blob-bound to C24 replay. Those parts hold. Two timing bindings do not.

1. Ambiguous claims become a predecessor start. `derive_anchor` uses `prior-submit` whenever `len(matches) != 1` and a predecessor exists. Two in-window claims for the same role, host, fingerprint, and turn are not one exact claim. Counterexample: round 2 submitted at 00:05, predecessor at 00:01, claims at 00:02 and 00:03, both `turn=2`. Result basis is `prior-submit` at 00:01. Required basis is `unknown` with no invented start.

2. An exact turn claim is dropped when it precedes the other participant’s submission. The `previous <= claimed_at` filter runs before the unique-claim return. Counterexample: author claim `turn=1` at 00:01:00, author submit 00:04:00, reviewer predecessor submit 00:03:00. The claim matches role, host, fingerprint, and turn, yet the anchor is `prior-submit` at 00:03:00. Exact-turn claim evidence must win over the proxy.

3. Prior-submit confirmation ignores the retained public source. The anchor stores `predecessor.source` path and digest. `_bind_turn` instead expects `{other-role}-response-{index}.md` and never compares `anchor.source.digest`. Counterexample: native predecessor `native/review-c58-author-response-1.md` digest `sha256:aa…`, portable `start_basis=prior-submit` and `start_source=author-response-1.md`. Binding succeeds. The same turn with `start_source` equal to the native path and digest fails. Hashes are not checked.

`test_native_mapping` covers the happy claim, a later prior-submit, distinct finalization, and byte custody only. It does not catch these cases. The hosted receipt’s candidate tree and synthetic merge match this source head; that does not correct the adapter.

REVIEW COMPLETE
