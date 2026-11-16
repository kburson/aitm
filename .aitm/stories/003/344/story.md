---
schema: "aitm.story/v0"
id: 344
title: "[#133] Verify and repair end-to-end test impact analysis"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/344"
parent: 133
children: []
blocking: []
blocked-by: []
created: "2026-11-16T12:45:44Z"
updated: "2026-11-16T13:44:31Z"
last-branch: "codex/344-functional-tia"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/tia-baseline.md", "plan/tia-evidence.md", "plan/tia-proof/receipt.json", "plan/implementation-verifier.json", "plan/baseline-verifier.json", "plan/implementation-review.md", "plan/test-impact-analysis-implementation-plan.md", "plan/reviews/plan/2026-11-16-test-impact-analysis-implementation-plan-review-c71d9bf99a30b80cea3e96ba9d9c8b9f/review-c71d9bf99a30b80cea3e96ba9d9c8b9f-review-manifest.md"], "attachments": []}
expansions: []
trips: []
---

# [#133] Verify and repair end-to-end test impact analysis

[GitHub issue #344](https://github.com/kburson/aitm/issues/344) · [Parent #133](../../001/133/story.md)

Rank 200, P1, M. Initial estimate of 4 implementation agent-hours, subject to refinement after baseline verification. The delivered predecessors are [#340](../340/story.md) and [#341](../341/story.md).

## Outcome

As an AITM contributor, I want ordinary pull requests to run the tests affected by their changes and show why those tests were selected. When the affected set cannot be established, I want CI to run the full applicable suite. Prove this through the live required check and repair any in-scope gaps before closing the story.

#340 and #341 shipped the coarse base-owned path map and the full-suite-once behavior in #342. #343 demonstrated a mapped Grok change and same-selection reuse. That evidence covers one mapping. On trunk `625b5407978675ac3b906990c8bb0713dcae18fd`, the selector returns only `test_ledger.py` for a change to `ledger.py`, although `test_scope_admission.py` and other test modules also exercise `Ledger`. Use this as the first dependency-coverage case.

## Acceptance criteria

- Run through the normal pull-request workflow using the trusted base, exact PR head and tested merge tree. Compare the selected and actually executed tests with a full-suite run and independently established expected consumers for representative direct source, shared or transitive source, and fixture changes. Record each changed path, the rule or dependency chain behind its selection, and the executed test IDs. Demonstrate that representative changes narrow the run.
- Include a regression case the full suite catches. The required mapped check must catch it too, or the selector must conservatively require the full suite. Include a later push with the same selection after an earlier successful full run, so the case exercises the short check when it matters.
- Prove that an unmapped executable input, uncertain dependency, and shared setup or CI control change require full validation. Cover path moves or removals that affect existing consumers. Verify that a changed selection or fallback runs the required full validation and that superseded evidence cannot pass the current head.
- Fix missing or incorrect selection, execution, fallback, or evidence in the path-map/TIA code or workflow as needed. Retain regression coverage for each fix and repeat the relevant comparisons after delivery. Keep the established #340/#341 workflow and CI protections as the starting point.
- Publish replayable commands and hosted run or artifact links with base, head, tested tree, selected and executed tests, fallback reasons, full-suite comparison, and pass/fail outcomes. Obtain independent review and verify the delivered behavior before closing. Any unresolved gap in these criteria keeps this story and #133 open.

Scope is functional TIA for ordinary PR validation under the [current #133 direction](https://github.com/kburson/aitm/blob/043d7ce22ed2da0d00aaa1236b1eacd9d1710a87/.aitm/stories/001/133/plan/2026-11-16-133-pr-feedback-replacement.md). The [accepted TIA design](https://github.com/kburson/aitm/blob/2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9/.aitm/stories/001/133/design/test-impact-analysis-design.md) defines explainability and uncertainty fallback. Reuse the delivered path map wherever it can meet those criteria. Scheduled backstop activation and Stop the Line are outside this story's scope.

## XPR plan acceptance

[Functional Test Impact Analysis Implementation Plan](plan/test-impact-analysis-implementation-plan.md) was accepted in round 2 by Grok `grok-4.7` at high effort, with Codex `gpt-6.1-sol` at high effort as author. The accepted plan digest is `sha256:a6f7ef90668153eeb063d34b33162424409526021475eeed97dbf342b289c109`. [XPR review manifest](plan/reviews/plan/2026-11-16-test-impact-analysis-implementation-plan-review-c71d9bf99a30b80cea3e96ba9d9c8b9f/review-c71d9bf99a30b80cea3e96ba9d9c8b9f-review-manifest.md) · [Final reviewer response](plan/reviews/plan/2026-11-16-test-impact-analysis-implementation-plan-review-c71d9bf99a30b80cea3e96ba9d9c8b9f/review-c71d9bf99a30b80cea3e96ba9d9c8b9f-reviewer-response-2.md).

## Implementation and baseline

[Baseline and consumer audit](plan/tia-baseline.md) · [Independent implementation review](plan/implementation-review.md) · [Implementation PR #346](https://github.com/kburson/aitm/pull/346)

The full hosted check and [trusted verifier](plan/implementation-verifier.json) passed on the independently reviewed implementation tree.

[Live delivery evidence](plan/tia-evidence.md) records all post-merge cases, including the new full run after selection changed.
