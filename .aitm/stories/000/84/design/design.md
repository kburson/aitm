# Package and private durable ledger design

[Reviewed parent design](../../83/design/usage-capture-design.md) at raw SHA-256 `d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee`. The scope below implements U01 for #84.

Own the standalone package, closed typed envelopes and private ledger. Initialization creates a UUID-bound schema and key. Open validates schema, project and key before writing. Use a stable, nonblocking process-held file lease and permit readers to obtain snapshots while the writer is active. Commit accepted record revisions and the cursor and provider checkpoint in one transaction. Preserve immutable-key conflict and prior history.

The collector is maintained for the life of AITM. This leaf contributes the scoped deliverable in the parent plan. Work belongs to #83.
