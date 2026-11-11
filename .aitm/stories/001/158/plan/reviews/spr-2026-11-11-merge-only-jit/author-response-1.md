# Author disposition of the first JIT review

- F1. The stale base remains the first parent of the candidate, with
  the advanced base reachable through its head. The stale head control
  uses a forward-valid actual-to-requested transition and repeats the
  identical transaction after advancing only the actual head. The stale
  flag control is also forward-valid.
- F2. The pair shares a recorded tuple, has distinct request IDs and
  flag OIDs, and requires both terminal responses and joint readback.
- F3. The JIT requires preflight of fixture events and applicable
  automation, an exact ruleset and PR scope, and owned-only cleanup.
- F4. The protected phase names the actual pull request rule, requires
  a ready and mergeable fixture PR, and separates rule attribution,
  transaction success and exact PR authorization.

The trial result and any execution deviations are reviewed separately.
