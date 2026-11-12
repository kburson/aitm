# #147 author disposition — Design review round 1

Author Codex / story147. Recorded 2026-11-12T01:57:30Z.

The original design and refinement are preserved at raw SHA-256 `443d4695ef3b005d53f44834598f5e7f77f8fa27c597378f594fec7dcfa618a1` and `260d854aad8a6d9ee4a6e7d1767f9d8d35e9539a601b736e6ad76bb4236a6498`, respectively.

1. Accepted the complete-lane finding. The delivered suite policy requires both `ci-helpers` and `product-cli` at `darwin-apfs`, with different owners. Design §Applicable inventory now matches the exact canonical lane set to the independently expected anchor, T02 projection, target, and every step's independently sourced delivery and applicable review. It maps full rows to their profile/platform and owner, validates capabilities, and holds even with a valid row hash when an evidence record covers one lane. Added explicit required-lane refusal coverage to the refinement.
2. Accepted the classifier clarification. Design §Control changes preserves the #103 predicate and lists every exact non-root basename in its finite expansion. The classifier identity is part of the exact binding. The local proof includes a nested recognized control outside the legacy roots and an unrelated product module alongside it. Candidate files remain inputs to the classification.

The revised design and refinement are at raw SHA-256 `b4df3f9233e71f90627fee92f4031664122560739a63c2810310863611660746` and `db9524f3e5b595c4e4bfee2d537728eca3831c341cd1f43f4f2bf41dea08aeba`. The estimate remains 3.5 implementation agent-hours. Canonical full-lane equality uses the same binding representation for each expected transition. The expanded control boundary uses a finite basename predicate and the existing verifier logic. Reallocated 0.15h to the replay and lane checks and added a 2.5h checkpoint. The two-file scope and four-hour cap still apply.
