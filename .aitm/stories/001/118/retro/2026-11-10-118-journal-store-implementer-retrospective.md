# AITM #118 private journal store implementer retrospective

I authored the private SQLite storage lane for M08a as Codex (`/root/journal_store_impl`).

## Plan alignment

I implemented `JournalStore` and its storage tests. The store reuses Ledger's SQLite connection settings, private-path validation, and account lease. It gives the routing policy one transaction boundary for claims, disputes, and cursor progress. Genesis requires the registry's already initialized source key. It stages and syncs a private database and its WAL and SHM files before publishing the directory with an atomic no-replace rename. Reopen validates the application ID, schema, key, and file identities, then confirms the directory publication. Transactions verify custody again before commit. The Registry change that expires a writer's lease came from the coordinator's lane. I verified that an old store handle refuses use while a replacement writer owns the registry.

## Misses and repairs

The genesis test first failed because the store did not exist. During my staging review, I found that my first implementation could initialize a substituted empty database after exclusive file creation. A targeted regression reproduced the miss. I captured the creation descriptor's identity and checked it before SQLite opened the database and again before publication. The regression then passed. The final tests also exercised a pre-existing empty target, an interrupted parent-directory sync, malformed schema, unsafe or missing sidecars, a replaced key, a store swap before commit, and rollback on a transaction body failure.

I ran the full package suite while the routing integration fixtures were still changing. It finished with 912 passes and four fixture failures outside my storage tests. I recorded those failures in my implementation handoff. For a future concurrent implementation, I would run the lane and adjacent contract tests during development and take the full integration measurement after the source and fixtures are frozen.

## Evidence, timing, and confidence

| Evidence | Recorded result |
| --- | --- |
| Final focused storage suite | 30 passed in 0.84 seconds, 173 of 188 storage lines covered |
| Storage, Registry, and Ledger suite | 147 passed in 4.99 seconds |
| Early moving-tree package suite | 912 passed and 4 failed in 108.66 seconds |
| Frozen local gate | 920 product and CLI tests passed in 154.32 seconds, 182 helper tests passed in 15.19 seconds |
| Hosted and independent review | Signed hosted run `42922357862`, attempt 1. Independent Claude Opus 5.5 medium source review passed. |

Actual active implementation time and its breakdown across tests, coding, and review are **Unknown**. I did not record a continuous effort timer. The plan's 1.10 agent-hour storage allocation was an estimate. The durations above are elapsed test runtimes.

PR #200 merged to literal `trunk` on November 10, 2026 at 23:30:24 UTC. The reviewed head was `db814e9e8d37e08860e822baed72f917132541a6`, the merge commit was `1452999b2f0f5a90161e39862458029c0084772c`, and both had tree `cb6ff8ce8506abc2a4bda4da3ddad93a35c33aad`. I checked that both delivered storage files match the SHA-256 digests in my signed implementation handoff. I have high confidence in the delivered storage behavior exercised by these tests and in the identity of the delivered files. [PR #200](https://github.com/kburson/aitm/pull/200)

Signed by Codex (`/root/journal_store_impl`), original private storage implementer, November 10, 2026 (America/Chicago).
