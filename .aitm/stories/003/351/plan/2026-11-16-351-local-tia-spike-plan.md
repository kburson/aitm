# #351 local TIA spike plan

The #351 research phase asks two independent questions. #352 identifies the first missing prerequisite to name tests for one ordinary dirty source edit. #353 identifies the authority boundary for reporting pass or fail on an assigned local test set. Each spike delivers a reproducible finding and an independent verdict. The [epic](../story.md) and child stories set the scope. Research produces planning evidence only.

## Common inputs and review sequence

- Pin current remote trunk `8799c5a445dd4b51d499132e9a314b64796ae918`, tree `456a155fbe7d10cb7daafd2bf46f134be78366a8`, and planning base `4176a99a37f64b9a4c9d1c71080a760ebe3820c1`. Capture effective OS, Git, Python, and uv versions. Use a private scratch Git clone or directory for probes, with an exact shared trunk base and disposable candidate bytes. Store sanitized summaries and reproduction commands in the respective child story.
- Complete manual SAR against the exact plan before conducting the probes. Put the verdict and plan SHA-256 in the planning record. Run the research, then have an independent reviewer read and challenge each finding against the plan, pinned source, and evidence. Address and re-review material disagreements. Each final verdict binds its own finding digest.
- Require accepted #352 and #353 findings before feature development. #354 and #355 get separate implementation plans and SAR before their respective Develop steps. The #355 plan additionally depends on #354's delivered interface. #344's hosted path, production rules and CI are outside these probes.

## #352 name the first blocking condition

Estimate 2 research agent-hours, Size S, Rank 440, P2. No prerequisite issue. Deliver `352/plan/2026-11-16-352-findings.md` and a sanitized machine receipt. Consult #143, #267, #288, #339 and the current local snapshot, inventory and hosted path-map source.

1. Use an existing regular mapped production source with a maintained consumer, `packages/aitm-usage/src/aitm_usage/sources/grok_scope_hook.py`. Verify the exact rule path and oracle under #344. Run the stock `python -m tools.ci.tia.local --base <trunk-sha> --plan` on a clean scratch checkout and on a scratch checkout with just that source changed. Keep both exits, modes, reasons, changes and snapshot identities. Also call the effective snapshot resolver directly to preserve the dirty path and before/after content IDs if the stock plan refuses. Record whether a failure precedes test collection or occurs during classification.
2. Compare stock hosted map on committed base versus HEAD while the scratch worktree is dirty. Then evaluate the same bytes as a scratch-only commit and compare with the same pinned base and unchanged control files. Keep the rule and consumer path, and state whether module targeting proves all exact test IDs. Distinguish visibility of the edit, map qualification, and the earliest stock local refusal.
3. If the stock local planner refuses before selection, trace the first condition to its parser or invoker and use the smallest read-only diagnostic that confirms it. A one-edit path witness can establish a bounded handoff for #354. A diagnostic alone cannot qualify the entire working-tree selector. State which unknown changes must widen or refuse, and whether #354 must stop because there is no supportable test list.

Accept only if the receipt answers the question for its exact fixture, explains differences from #339 if any, and makes a supportable or stop recommendation for #354.

## #353 identify the process trust boundary

Estimate 2 research agent-hours, Size S, Rank 450, P2. No prerequisite issue. Deliver `353/plan/2026-11-16-353-findings.md` and a sanitized machine receipt. Consult #146's selected and product-slice findings, #267's benchmark, #143's local advisor, and the current launcher and pytest observer.

1. Trace controller, worker, same-interpreter plugin and candidate tests, environment, output path and verdict aggregation. Attribute directly observed process facts and worker assertions. Check how inventory, node outcomes, native children, control bytes and report custody were treated in the retained #146 reviews.
2. In private scratch with the locked Python/pytest, use a benign module with one passing and one failing test and launch one explicitly assigned node per child. Have the parent record PID, exit, invocation, receipt consistency and cleanup. Also run an invalid assignment and reconcile distinct selected node IDs with collection, reports and return codes. Record whether the observer hooks and test bodies run in the same interpreter, and whether the probe isolates their filesystem authority. Demonstrate scoped process observations with ordinary success and failure. No privilege or machine configuration changes are needed.
3. State the minimum process and evidence boundary for a trustworthy local result. Distinguish cooperative developer feedback from assurance against candidate-controlled Python. Require exact snapshot and assignment linkage, qualified outcome source and fail-closed handling for missing, incomplete or stale evidence. State which parts a scratch child actually establishes and which remain qualification work for #355. An unavailable required boundary keeps #355 from claiming trusted execution.

Accept only if the finding explains the old shared-process observation, uses #267 as a selector accuracy check rather than execution attestation, and gives #355 concrete acceptance or refusal conditions.
