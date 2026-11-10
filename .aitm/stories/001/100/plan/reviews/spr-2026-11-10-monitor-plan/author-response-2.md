# Author response to SPR round 2

Revised plan SHA-256 `57b0fc3fdfdfb4bfc0d8ae90558ba2cee4effe9b22fa85ba412e4bd856fa7e37`.

1. **Cutover crash windows.** M16 verifies the rollback bundle against the stopped checkpoint under the original guard. A newer legacy write requires a matching replacement or cutover refusal. The persisted pre-write fence and guarded ledger head detect durable monitor writes independently of ACK or an optional marker. Uncertainty cannot authorize legacy restore.
2. **Read-only snapshot identity.** M13 now issues an authenticated, versioned token binding the fenced publication, UTC interval and exact rate evidence. Separate processes reopen the underlying inputs and preserve the old result or return unavailable. Tests distinguish windows and rates over one publication.

Both changes have explicit failure and restart cases.
