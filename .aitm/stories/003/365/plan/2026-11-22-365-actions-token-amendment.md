# #365 Existing Actions token amendment

The owner directed #365 to use the existing job-scoped GitHub Actions token to update issue #418. The original authenticated sweep attempt is the source of truth. This replaces the earlier App requirement and resolves the activation hold from the [account-token spike](2026-11-22-365-account-token-spike.md).

The record remains advisory. Keep the accepted scheduled-workflow identity, original-attempt rule, activation floor and linked run. Compute the latest decisive attempt from authenticated Actions history. A valid manual edit cannot supply a decision or set its ordering. Track edit metadata in the pre-write snapshot. Authenticate a potentially newer cached link directly when the run is missing from the list. An unrelated or missing link cannot override a verified result. A failed provider read holds publication. The shared bot identity gives no exclusive publisher attribution. A malformed body or unverifiable result preserves the display until it can be reconciled.

The user identifies `planning` Git history as the audit record for backlog edits and timing. Issue #418 is outside the backlog. Use its GitHub edit history and the exact-run link to inspect advisory changes. Record deployment evidence in the #365 planning ledger.

The story keeps its existing closure gates. Validate [PR #419](https://github.com/kburson/aitm/pull/419) with fresh exact-head Grok review, canonical CI and the trusted verifier. After merging, reconcile via the deployed workflow and verify the pinned issue body against the linked sweep attempt.
