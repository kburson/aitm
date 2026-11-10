# #113 installed-wheel compatibility proof

Recorded November 10, 2026. CPython 3.13.9 on macOS. All state was synthetic and isolated, with a private guard root. The fixture had no provider credentials, real transcripts, installed service or production state.

- Exact delivered v1 source `338ff3382fd1757ae150fabfe93df98df5338e2a`, isolated wheel SHA-256 `bd8d2764ffcbe89db4d72a9ba59e430d7f84a2428f3ecd36fe5fb720ccae6abf`. It generated a v1 ledger, v1 backup and frozen export.
- Candidate head `83fe253ed2a979bb23b52f0a3280591d662112a6`, tree `3e4d46feb9a8c7890937b089e486824cb308b93d`, isolated wheel SHA-256 `6dae0ef97ee7c60697e2d098ebad7c294d6ed0afd19e1ba673824b4417c4d980`. The installed console help passed.
- The old installer prepared and probed the candidate wheel on v1. The candidate installer also prepared and probed the old wheel on v1 and accepted the original v1 backup.
- The candidate's guarded upgrade retained project ID, pseudonym key identity and sequence. The candidate reopened both snapshots, and the original and post-migration frozen export directories matched byte for byte. The candidate installer accepted its own wheel on v2 and refused to certify the old wheel on v2.
- The original installed console attempted a one-shot collection after migration. It returned exit code 1 and `collection-failed`. SHA-256 comparisons of the database, WAL, pseudonym key and retained registration before and after matched. No service was started.

The committed tests additionally verify stale-sequence refusal, transactional rollback after both DDL and version update, mismatched table fingerprints, v2 backup verification and argument separation. M16 retains production adoption authority.
