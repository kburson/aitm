---
schema: "aitm.story/v0"
id: 403
title: "List affected tests from the import chain for one real change"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/403"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T23:50:50Z"
updated: "2026-11-20T01:26:00Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-19-370-import-chain-list.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# List affected tests from the import chain for one real change

[GitHub issue #403](https://github.com/kburson/aitm/issues/403) · [Parent #370](../370/story.md) · [Plan](../370/plan/2026-11-19-370-import-chain-list.md).

List the affected tests for one real product change by walking the import chain. This replaces #402 before that story starts. Do not qualify another Grok replay declaration, another edit of `_headless_tokens`, or another hosted shadow of `packages/aitm-usage/tests/test_grok.py`.

#383 already returns a test list for the staged index, for HEAD, and for a pull request. Index and HEAD diff the divergence commit. The pull-request graph diffs the literal PR base against the tested merge. On the real repository that list is the full inventory. #385 showed why: an unresolved record with no `possible_inputs` is applied to every changed path, and the product tree has `dynamic-import`, `unresolved-import`, and `relative-import-context` records. The 16-test fixture had none of those records, so it narrowed. #393 and #398 then saved lane time by hash-pinning one reviewed boundary. That boundary is timing evidence. It is not the selector.

## Behavior

Use the #383 probe and the file graph in the one Python program. Index and HEAD diff the single merge-base of the named parent and HEAD against the staged index or the HEAD tree. A pull request keeps the #383 graph input: the literal PR base, the first parent of the tested merge, against the tested merge tree. Record the divergence commit as well, the single merge-base of that literal base and the PR head. The selected tests and the full run both execute on the tested merge.

For each changed path, walk the reverse import edges to pytest node IDs. An unresolved record applies to that path only when it can hide a reverse edge the walk would miss, or when the walk already goes through the uncertain file.

- A record with `possible_inputs` applies when the changed path or a file reached from it is under one of those prefixes, or when the record's reader is in the walk.
- A `dynamic-import` record with no `possible_inputs` is read from each call in that reader. A call qualifies when its module argument is a string literal, or a name assigned exactly once by a direct statement of the same function to one string literal. That assignment is a direct statement of the function. It is not inside an `if`, a loop, a `try`, a `with`, a nested function, a lambda, a comprehension, or a class. A parameter, a global, an attribute, a subscript, an alias of the loader, or a second assignment does not qualify. When every dynamic call in the reader qualifies, those string values are the prefixes and the `possible_inputs` rule applies. `packages/aitm-usage/tests/test_claude.py` function `adapter` and `packages/aitm-usage/tests/test_codex.py` function `adapter` qualify. When any call in the reader does not qualify, the record applies to every changed path and the mode is full. Do not build a general constant-propagation pass.
- An `unresolved-import` or `ambiguous-module` record applies when the imported name is the module of the changed path or of a reached file, or when the reader is in the walk. A different name does not apply.
- A `relative-import-context` record applies when the reader is in the walk, or when a legal package context of that file would import the changed path or a reached file. When those contexts cannot be listed, the record applies.
- A `wildcard-import`, `pytest-plugin`, `python-parse`, `unindexable-source`, or `unsupported-python-mode` record applies when its reader is in the walk.
- Any other unresolved reason applies to the changed path. Do not invent a narrower rule for a reason this list does not name. If that reason is what still forces full, name it in the receipt.

A shared input stays full. A walk with no test witness stays full. A missing exact snapshot or a missing inventory stays unavailable. A wrong pull-request parent or tested tree stays unavailable. Index mode ignores unstaged and untracked edits. HEAD mode ignores the index and the worktree.

When every changed path has a static walk, the mode is `selected` and the list is the reached node IDs. When any changed path has an applicable uncertainty, the mode is `full` and the reason names the record.

Do not add a suite declaration. Do not hash-pin a function body. Do not drop a `conftest.py` edge to shorten a list. Do not bound dynamic imports that the chosen change does not meet. #393 and #398 stay as they are.

## Acceptance

1. On hosted Ubuntu, one real product change on current trunk returns a list shorter than the full inventory. The change is not the 16-test fixture and it is not `_headless_tokens`. The reverse walk is static under the rules above. The hosted case is a pull request. Selection uses the literal base and the tested merge, and the divergence-to-head path set equals the base-to-merge path set. A seeded failure in a reached test fails in the selected run and in the full run. Both runs execute on the tested merge. Every full-run failure is in the selected list. Record the witnesses, node IDs, Git identities, and lane times. If the first candidate reaches a shared `conftest.py` and therefore the tests that use it, record that candidate as a full case and choose another product file. Stop after one narrow case.
2. On the same runner, one real change that meets an applicable uncertainty returns full. Use an unbound non-literal dynamic import, an unresolved import of the changed module, or a shared `conftest.py` in the walk. The full run is the outcome for that case.
3. Show index mode excluding an unstaged edit, HEAD mode excluding the index, and a mismatched pull-request parent or tested tree returning unavailable. Show one pull request whose literal base is not the divergence commit. Record the divergence, the PR head, the literal base, the tested commit, the tested tree, and the ordered parents. When the divergence-to-head path set and the base-to-merge path set differ, the mode is full and the reason names the paths that differ. That pull request can be the full case in item 2. It does not add a third hosted product run. When the path sets match, the pull request can be the narrow case in item 1.
4. Publish the receipt under #370. Keep the run advisory. Leave the required workflow, path map, evaluator, verifier, branch rules, and the pinned #355 command unchanged. #370 stays open until this receipt is accepted. Promotion of the list into the required gate is a separate decision.

## Refinement

Owner direction on 2026-11-20 after the review of this story. A same-function constant binding qualifies as a dynamic-import prefix. The pull-request graph stays on the literal base and the tested merge. The divergence diff is recorded beside it. Different path sets stay full. Same path sets use the import-chain list, and the outcome comparison runs on the tested merge.

[Parent #370](https://github.com/kburson/aitm/issues/370) · [#383 probe](https://github.com/kburson/aitm/issues/383) · [#385 findings](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/370/plan/2026-11-19-370-hosted-shadow-findings.md)
