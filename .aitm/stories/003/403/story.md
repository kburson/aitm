---
schema: "aitm.story/v0"
id: 403
title: "List affected tests from the import chain for one real change"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/403"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T23:50:50Z"
updated: "2026-11-20T12:50:45Z"
last-branch: "codex/403-import-chain"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-19-370-import-chain-list.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# List affected tests from the import chain for one real change

[GitHub issue #403](https://github.com/kburson/aitm/issues/403) · [Parent #370](../370/story.md) · [Plan](../370/plan/2026-11-19-370-import-chain-list.md).

List the affected pytest tests for one real product change by walking reverse import edges in #383's Python probe. #385 found three full-suite decisions under unbounded uncertainty and one unavailable decision because the inventory could not classify a renamed test module. #393 and #398 measured the existing Grok replay boundary. Preserve that evidence and use a different real product input here.

## Exact inputs and compatibility

Index and HEAD use the single merge-base of the named parent and HEAD. Index reads staged entries and excludes unstaged and untracked content. HEAD reads Git objects independently of the index and worktree. PR graph and inventories use the literal PR base and the GitHub-tested merge. Verify the tested tree and the ordered parents `(literal base, PR head)`. The selected and full lanes run on that tested merge. Record the single merge-base of the PR head and literal base as divergence.

For PRs, compare the divergence-to-head and base-to-tested path sets using the same raw byte Git change reader. Include both non-null endpoints of each change, including both names for renames and the old name for deletions. Record both sets and both directional differences. Different sets force full when the candidate inventory is available. Matching sets permit normal selection checks. Refuse invalid or drifted identity before evaluating full fallback. Recheck identities and the comparison after collection.

Limit the policy change to the #383 advisory probe. Preserve its old and new graph sides, surviving candidate node IDs, mandatory and newly collected obligations, changed and removed obligation handling, and existing conservative selection and inventory controls. A missing candidate inventory yields unavailable with zero assigned IDs. Missing or invalid baseline inventory yields full when the exact candidate inventory is available. An exact snapshot or identity refusal yields unavailable even if a candidate inventory is present.

## Uncertainty applicability

Walk reverse edges separately on the applicable old and new sides. Preserve witnesses on both sides and map surviving obligations to the candidate inventory. A record is applicable if its reader is reached, or if it can hide a reverse edge from a changed or reached path. If a required bound cannot be proved, retain full fallback and record the reason. A reached shared `conftest.py`, other shared input, or changed path with no test witness forces full. Retain all fixture and configuration edges.

- **Known input bounds.** Match repository byte paths exactly or under a slash-delimited directory prefix. For imports, resolve module spellings to candidate repository paths within each exact snapshot. Include package initializers and all plausible owners. An input bound that intersects a changed or reached path is applicable.
- **Dynamic imports.** Accept calls to the proven canonical `importlib.import_module`, including an unrenamed `from importlib import import_module` binding. The call must take one absolute module argument. It may be a string literal or a local name initialized by exactly one simple direct assignment of a string literal earlier in the same lexical function. The assignment must execute before each accepted call. Reject the bound when there is any other binding or deletion, including parameter, global or nonlocal use, nested writes, captures in a pattern, and names introduced through imports, comprehensions, assignments, exceptions, loops or context managers. Require proof of loader identity with no aliases, shadowing, escapes or unsupported references. Relative arguments, unknown package arguments, and richer loader forms including unsupported `__import__` forms retain unbounded fallback. Every possible loader reference and use in that reader must be accounted for. A single unsupported use, including a loader escape with no recognized call, keeps the record unbounded. This bounded lexical check covers the Claude and Codex adapter locals and the two canonical unrenamed imports present on trunk. General constant propagation is outside scope.
- **Unresolved, ambiguous, and relative imports.** Retain or re-read the original import statement and its level, module name and imported members on the correct snapshot. Resolve every plausible target, child import and initializer from supported pytest and package invocation roots, including supported repository-qualified and tool-root spellings. Consider each legal package context and ambiguous owner. Discount an unresolved record only when the complete possible path set is demonstrably disjoint from the walk and the reader is outside it. An empty inferred context list or an incomplete statement record leaves the uncertainty applicable. A proven external import with no possible repository target can be excluded when its reader is outside the walk.
- **Wildcard and pytest plugin imports.** Account for possible module imports through package exports, including children reached by `__all__`, and for plugin modules and their reachable inputs when a declaration can load them. A declaring reader outside the walk can still hide a dependent test. Use complete endpoint path bounds when they can be established. Otherwise force full.
- **Opaque and unclassified records.** Unparsed, unreadable, unindexable or unsupported source remains applicable when an omitted owner or dependency can connect to the change. Require proof of disjointness before discounting these records. Unrecognized reasons remain applicable. Preserve the existing unavailable decision if exact materialization or candidate collection fails.

An accepted selection includes the reached surviving pytest IDs plus the existing mandatory, newly collected and other candidate obligations required by #383. Record import witnesses, uncertainty decisions, and the reason for each additional obligation or fallback. Keep the current path map, required workflow, evaluator, verifier, branch rules, and pinned #355 command unchanged. Suite declarations and per-function source hash admission are outside scope.

## Acceptance

1. Add offline regressions for the two SAR false negatives. A wildcard child and a pytest plugin target each have a direct passing witness and a hidden failing consumer. The affected assignment must include the failing consumer or fall back to full. Exercise an opaque reader with an independent positive witness. Cover endpoint aliases, dotted import parent initializers, from-import children across legal package contexts, and fallback on an incomplete context.
2. Exercise direct literal and same-function constant positives, including the current unrenamed loader imports. Exercise a nested nonlocal write, a module or loader alias or escape, a mixed reader with one unbounded call, unsupported loader arguments, and other rebinding forms. Confirm that an uncertainty on either applicable snapshot side forces full. Verify prior-only witnesses after a move or removed import, mandatory and newly collected IDs outside the walk, missing baseline inventory, and missing candidate inventory.
3. Verify staged and HEAD isolation and PR refusal on incorrect parents or tree. Exercise matching and mismatching path sets locally with divergent bases, including a rename and deletion. Confirm a mismatch lists both directional differences and a bad identity still refuses. Use one divergent-base case in the two hosted product cases.
4. On hosted Ubuntu, qualify one real production-only mutation with a shorter assignment. Use an exact green baseline for the relevant existing tests. The mutation must break an existing nonmandatory test reached through an import witness. Preserve test source bytes so the failure demonstrates the production import chain. Evaluate candidate `host_watch.py` and its existing tests first. Check the full run for every failure and compare selected outcomes against matching full node outcomes on the same tested tree. Record exact IDs, witnesses, Git identities and lane times.
5. Run one real full-fallback case on a comparable hosted Ubuntu runner. A change reaching the shared product `conftest.py`, such as a change to `monitor_registry.py`, is a candidate. Demonstrate the shared or uncertain edge independently of any divergent path-set mismatch. If an attempted narrow candidate reaches shared setup, treat it as the full case and choose another product file. Stop after one qualified narrow case. The divergent control does not add a third hosted product case.
6. Verify complete pytest inventories and per-node phases for the hosted comparisons. Treat absent, stale, incomplete or conflicting evidence as a hold on qualification. Publish the advisory receipt under #370 and keep #370 open until it is accepted. Gate promotion remains a separate decision.

[Parent #370](https://github.com/kburson/aitm/issues/370) · [#383 probe](https://github.com/kburson/aitm/issues/383) · [#385 findings](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/370/plan/2026-11-19-370-hosted-shadow-findings.md) · [First SAR](plan/reviews/sar-2026-11-20-import-chain/reviewer-response-1.md)

## Implementation and testing

The exact candidate is in [PR #406](https://github.com/kburson/aitm/pull/406). Track the hosted shadow qualification and required CI in the [delivery checklist](plan/delivery-checklist.md).

## Hosted import-chain qualification

Both hosted Ubuntu shadow cases qualified on `9b5f22c2f49250fe5c9208ccb13df9fc7bccba6e`. [Findings](../370/plan/2026-11-20-370-import-chain-shadow-findings.md) · [Exact evidence](../370/plan/2026-11-20-370-import-chain-shadow-evidence.json).

Required CI and the delivered verifier passed on the exact implementation PR. [Independent source review and CI receipt](plan/reviews/2026-11-20-403-source-review.md).
