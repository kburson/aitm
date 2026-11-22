# #364 Shared failure flag storage implementation plan

**Goal**

Deliver one location and schema that people and agents can read and #365 can update safely.

**Scope**

[Story](../story.md) and [epic plan](../../362/plan/2026-11-21-362-delivery-plan.md). Target `planning`. The receipt specifies the store and its reader/writer contract. Production creation and configuration belong to #365.

## Tasks

- [ ] Compare a dedicated repository issue, expiring workflow artifacts, and a branch-backed file for web/CLI access, durability, write permissions, repeatability and merge independence. The working choice is one dedicated issue with a stable number and immutable issue ID. Verify issue update permissions in the [GitHub Issues API](https://docs.github.com/en/rest/issues/issues#update-an-issue), and read an existing issue through the browser URL and `gh api` without writes. Decide the repository binding, how #365 provisions and pins the target, and what happens if the issue is closed, edited or unavailable.
- [ ] Publish the precise contract for a versioned JSON block and generated summary. Proposed fields are `schema`, `state` (`active` or `clear`), and the last decisive `run` with `repository_id`, `workflow_id`, `run_id`, `run_number`, `run_attempt`, `head_sha`, `conclusion` and a UTC result timestamp. Derive the canonical attempt URL from the fixed repository and numeric run/attempt IDs. Keep the decision and the #363 ordering watermark in the same atomic record. Coordinate the exact ordering key and activation floor with the #363 receipt at #365 JIT. Define a separate uninitialized or unreadable result and how the record communicates the age of the decision. Fix schema and parse rules before handoff.
- [ ] Specify minimal permissions, one fixed writer target, serialization and readback, retry after ambiguous API outcomes, idempotent duplicates and the persisted watermark used even after a clear. Show example active, clear and unavailable responses. Document recovery for a malformed record and a missed writer invocation with the normal authenticated read/reconcile route.
- [ ] Open the receipt PR. Obtain independent Grok PR review on its current head and record accepted delivery before #365 starts.
