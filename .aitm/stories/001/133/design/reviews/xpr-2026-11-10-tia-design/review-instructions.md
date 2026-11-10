# Task-scoped #133 design cross-provider review

Follow the package's sealed invitation, exact join/submit action, protected
response metadata, and reviewer write boundary. Edit only the authorized
pending response. Do not use Git, amend the artifact, implement, or publish.

Each round, retrieve the current complete file under review with fresh,
contiguous numbered Read tool calls of at most 20 lines apiece from line 1
through EOF. Use the exact artifact path in the invitation. Read tool results
must actually return each line. If any output is abbreviated or truncated,
retrieve the missing lines in smaller chunks. Before submitting, state the
observed read ranges and coverage in the response. Earlier reads, patches, and
tool-call requests are not substitutes. For later rounds, read the prior author
disposition and check its corrections against the freshly retrieved full file.

Review test dependency explanations, conservative uncertainty fallback, CI
shard inventory and exact run custody, full versus selected coverage, and
merge/incident/workspace authority. User decisions include 3/6/10 minute
budgets, isolated PR failure blocking only that PR, and a scheduled trunk
test failure blocking ordinary work and merges until a full repair candidate
passes, repaired trunk passes its full suite, and every governed workspace
has verified receipt. A disconnected roster member holds restart. Preserve
separate approval for affected-only gate cutover. Report material unresolved
design issues as actionable findings; accept only when none remain.
