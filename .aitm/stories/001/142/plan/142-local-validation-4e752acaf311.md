# #142 local candidate verification — attempt 1

- [PR #263](https://github.com/kburson/aitm/pull/263), exact source `4e752acaf311c42c4173fc532977502b88ba398a`, tree `61eeabeed1362d5c39188dd6aade2b6549515b01`, target `trunk` at `011342493399ed6e8a12ba0e9c2a4a1e9efaf294`.
- Python 3.13.9, uv 0.10.6, lock enforced. The three owned files are the only additions.
- Focused pytest: **41 passed**, 41 collected. [Exact focused node IDs](142-focused-nodeids.txt).
- Combined selector, snapshot, inventory and graph pytest: **147 passed** in 63.33 seconds.
- Ruff lint and format checks passed on both Python additions. JSON manifest parsed and Git staged whitespace passed.
- Red/green evidence: the binding and traversal tests failed before implementation; the fallback tests failed before full-inventory and missing-scope decisions existed. The final suite passed with exact hosted bindings, raw path bytes, before and after witnesses, cycle and tie behavior, complete multi-lane fallback, and mandatory and skip accounting.
- The selector tests are separate local evidence. The existing hosted six-job #103 gate must be verified independently.
