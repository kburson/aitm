# #142 local candidate verification — attempt 1

- [PR #263](https://github.com/kburson/aitm/pull/263), exact source , tree , target  at .
- Python 3.13.9, uv 0.10.6, lock enforced. The three owned files are the only additions.
- Focused pytest: **41 passed**, 41 collected. [Exact focused node IDs](142-focused-nodeids.txt).
- Combined selector, snapshot, inventory and graph pytest: **147 passed** in 63.33 seconds.
- Ruff lint and format checks passed on both Python additions. JSON manifest parsed and Git staged whitespace passed.
- Red/green evidence: missing inventory binding and missing graph traversal failed before implementation; the fallback suite failed before full-inventory and missing-scope decisions existed. The final suite passed with exact independent hosted bindings, raw path bytes, former and current witnesses, cycle and tie behavior, complete multi-lane fallback, and mandatory and skip accounting.
- The selector tests are separate local evidence. The existing hosted six-job #103 gate must be verified independently.
