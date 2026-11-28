# Tool-assisted attempt for #576

The CLI omitted some inline input and the reviewer invoked a tool. This attempt did not qualify. Packet SHA-256 `8fb4c63abb8c1358a07b824a16687d85ba1971c94d13b2a6009ba1c86e416d78`.

The omitted packet lines are part of the review record. I will read only that span and then judge the pinned change from the packet.

PASS
c49b535d522f7fca1b8e5c6038b1783993e1c012 ebef35e0cf6d0cba02d92827e1f80ccd27aebe1f 481e018d7472d386f1045d2cfa87aad45711a415 eeb42add68dc5d2dc4de3f2de0f2cb2bc84c9d70

C58 binds accepted public native bundles to C24 replay and C57 closure. No blocking defect in custody, acceptance, blob lineage, revision versus finalization, identity, or claim timing. Live capsules and working-time aggregates stay in C25.

Originals stay immutable. `validate_bundle` only reads them (`O_NOFOLLOW`, regular non-executable files) and appends those bytes. The integration test compares the tree before and after. Manifest status must be `accepted`, `commit_mode` `normal`, and assurance `unavailable`. Draft, blocked, and round-cap manifests fail in `_manifest` before `derive_anchor`. Responses must match the manifest digest and protected frontmatter. `started_at` and other extra fields are ignored, so registration timestamps and private handles are not promoted. Derived identity is `native-fingerprint` plus the public session fingerprint.

Reviewer inputs follow `artifact_history[round-1]`. Each reviewer digest is the C24 input digest, and `_git_blob_matches` checks those replayed bytes against the git blob id. Non-final author output is that history entry and becomes the next reviewer input, so it is blob-bound on the next round. The final round cannot carry an outgoing artifact. `native_revision_commit` must be the last history commit, and a present `native_finalization_commit` must differ from it.

`derive_anchor` keeps one in-window claim only when role, host, fingerprint, and turn match. Two `turn=2` claims at 00:02 and 00:03 with a 00:01 predecessor and a 00:05 submit yield `unknown`, not `prior-submit`. An author `turn=1` claim at 00:01 still wins when the reviewer submitted at 00:03 and the author at 00:04. A null turn cannot start round 2. Prior-submit stores the predecessor path and digest. The native path requires that digest. A legacy alias is accepted only through the predecessor header’s `native_source` and `native_source_digest`. A conflicting alias hash is refused.

The hosted receipt binds this head, synthetic merge `481e018d7472d386f1045d2cfa87aad45711a415`, and tree `eeb42add68dc5d2dc4de3f2de0f2cb2bc84c9d70`. Core CI run 46109441335 and repository CI run 46109441304 passed. Collections are 986/81/1067 and 1644/142/1786. The exact-base verifier tested that merge at 2026-11-28T04:56:33Z, before `ready_for_review` at 04:56:34Z.

REVIEW COMPLETE
