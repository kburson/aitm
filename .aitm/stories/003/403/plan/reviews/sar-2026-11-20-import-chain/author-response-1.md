# Response to the first #403 SAR

The updated #403 story is the detailed contract. The #370 import-chain plan points to it for selection behavior and acceptance. The following revisions are ready for an independent second round.

| Finding | Disposition in the revised plan |
| --- | --- |
| Hidden wildcard and plugin inputs | Require complete path bounds or full fallback, even when the declaring reader is outside the walk. Add both reproduced cases and an opaque-reader regression. |
| Module names and endpoint paths | Resolve invocation-specific paths, imported children, initializers and ambiguity per snapshot. Keep fallback when the path set or relative context cannot be established. |
| Constant binding and loader identity | Admit only proven canonical calls and preceding direct assignments with complete lexical binding checks. Keep unbounded fallback for any unsupported reference or escaped loader. |
| Existing obligations and prior-side witnesses | Preserve both graph sides and required candidate IDs. State the candidate-unavailable and baseline-full distinction and test each. |
| PR agreement and hosted proof | Verify raw old and new path sets, both differences and identity precedence. Use a product-only seeded mutation and complete same-tree phase evidence. |

Implementation and hosted execution are outside this review round. The required gate retains its current role.
