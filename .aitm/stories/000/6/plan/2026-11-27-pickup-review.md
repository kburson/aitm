# #6 Pickup review

Grok 4.7 Build Fast. The revised pickup pins both delivered dependencies, records typed state and deliverable fields, and leaves producer actions and reciprocal writes with their owners.

**PASS**

The revised `core.deliverable.added` paragraph closes the only prior finding.

- **Identity:** stable `deliverable_id`, with an immutable repository-relative `path` and an immutable `source_snapshot`.
- **Digest requiredness:** `raw_digest` is a mandatory raw SHA-256. `canonical_digest` is an optional canonical SHA-256, and only for canonicalizable content.
- **Producer versus fold:** C45 owns `aitm deliverable add` and records the fact. C54 only validates and folds that persisted fact, keyed by `deliverable_id`, keeping the original binding and rejecting a conflicting reuse. Deliverable validation and target mutation stay with their producers.

Reviewed plan SHA-256 1042498abec87fabae0f549cc55150c07ff3e7ef83bd059bd805d496d51406d9.
