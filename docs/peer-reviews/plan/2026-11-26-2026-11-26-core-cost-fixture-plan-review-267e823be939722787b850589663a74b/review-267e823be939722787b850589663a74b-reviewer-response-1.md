<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-267e823be939722787b850589663a74b"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/004/459/plan/2026-11-26-core-cost-fixture-plan.md"
artifact_commit: "3af38dac61bcc3af1cb4a62fa87a262c4e80b5fb"
artifact_blob: "47015443e0973535b09b8a96c07ca9f0cad63080"
artifact_digest: "sha256:7530d9186bcd0bca742805054132faaf1baf63ae188006f25b2abcd88a834f7f"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-sonnet-5-5"
  model_display: "claude-sonnet-5-5"
  session_fingerprint: "sha256:8e19e746d2e8dc2d737de00b9261687ead9ba6ce7c9e35a8f69cd092ef9722cf"
  identity_source: "runtime"
started_at: "2026-11-26T13:10:04.059Z"
submitted_at: "2026-11-26T13:10:41.136Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent review of the plan against its refined design (`.aitm/stories/004/459/design/2026-11-26-core-cost-fixture.md`). The plan is well scoped and covers all five review-focus items. The producer and receiver boundaries are clear, and the ambiguity-recovery branches are executed through SQLite.

Limit of this review: the planning worktree holds no `packages/aitm-usage` source, so I could not check the named files, symbols (`pinned_inputs.py`, `scope_authority`, `pinned_cli.py`) or the receiver fixture against code. Findings come from the plan and design text only.

## Findings

1. **Rate-only same-cutoff outcome is unspecified.** The design says a rate-only change at the same cutoff "retains the usage projection" and that rate-specific diagnostics live only in provenance. Yet the plan also gives each v1 row a per-row Standard API-equivalent comparison and says price is "preserved". Task 2 tests a "same-cutoff rate-only change" without saying whether the expected receiver result is identical, duplicate or a refused same-cutoff conflict. If a price or amount reaches the v1 row bytes, a rate change alters the row digest and hits the conflict path. If it does not, the plan must say where the comparison is carried. The test cannot assert a correct outcome until this is fixed.

2. **No test for scope-key mismatch within one receiver lane.** The design says the same key must be used throughout a lane and that rotation "needs separate qualification". The plan tests only the 32-byte key length and privacy canaries. Nothing shows that a different key against an already-populated lane produces a distinct, reportable outcome (a new scope assertion identity, not a silent duplicate or an unexplained conflict).

3. **Task 2 verification commands are not exact.** Task 1 gives an exact `uv run --locked pytest` command. Task 2 says only "run red/green locked effort, legacy export and monitor recovery fixture tests". It does not name the files or node IDs. The legacy-export byte preservation guarantee in Global constraints depends on those tests. Without exact commands, "preserve legacy v1 export bytes" cannot be checked reproducibly.

4. **32 MiB bundle limit has no test.** Global constraints bound the emitted bundle to 32 MiB, and the CLI writes it to stdout. No red test covers an over-limit result: the expected error, exit code and sanitized message are not specified, and neither is whether the check runs before output.

5. **Key file read semantics are underspecified.** "Read the scope key at most 33 bytes" implies reading 33 to detect oversize, but the plan does not say a trailing newline is rejected, not stripped. Different handling would give a different pseudonym lane from an identical-looking key file. State this and test it.

6. **Task 2's third checkbox bundles too much.** It combines package tests, Ruff, wheel smoke, GitHub Actions on the exact head, independent source review, trusted verifier and merge-parent/tree verification. There is no red-step run in Task 1 or 2 before implementation, although "red tests" are written. Splitting it and adding an explicit "confirm red" run would make the TDD ordering checkable.

## Required changes

1. Resolve Finding 1: state in the plan whether the per-row price comparison is in the v1 row bytes. State the expected receiver outcome (identical, duplicate or conflict) for the same-cutoff rate-only test, and align the Task 2 test and the provenance fields accordingly.
2. Resolve Finding 2: add a test for a changed scope key against an existing lane and name the expected outcome.
3. Resolve Finding 3: give exact commands or node IDs for the legacy export and monitor recovery fixture tests in Task 2.

## Optional suggestions

1. Add the over-limit bundle test and fixed error text (Finding 4).
2. Specify exact-bytes key file handling and add a trailing-newline test (Finding 5).
3. Split Task 2's final checkbox and add an explicit "confirm red" run before each implementation step (Finding 6).
4. Task 3 hard-codes live values ($0.1754084, three pending observations). Say they are taken from the pinned #461 report, so later drift is not a failure.

## Decision

revisions-requested
