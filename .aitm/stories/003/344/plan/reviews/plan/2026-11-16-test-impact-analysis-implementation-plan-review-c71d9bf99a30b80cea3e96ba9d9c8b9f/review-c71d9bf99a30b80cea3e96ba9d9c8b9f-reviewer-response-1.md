<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c71d9bf99a30b80cea3e96ba9d9c8b9f"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md"
artifact_commit: "1eded398ddd7e718f544bfa3e78f651cc13dbb81"
artifact_blob: "894ae5cabd9c561c84f9ed28edcb7339cb23a985"
artifact_digest: "sha256:162d4d2a95eec01adcb8181dadff2dd550b63282ee8ce85eb45fb0d9361b46da"
agent:
  host: "grok"
  provider: "xai"
  model_id: "grok-4.7"
  model_display: "grok-4.7"
  session_fingerprint: "sha256:0c26620ccf192459c096abf761f4125c0e239c36725cd214d71437bf7a857592"
  identity_source: "declared"
started_at: "2026-11-16T12:55:58.895Z"
submitted_at: "2026-11-16T13:07:01.995Z"
finding_ids: ["R1-F001","R1-F002"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent review of `.aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md` at blob `894ae5cabd9c561c84f9ed28edcb7339cb23a985`, commit `1eded398ddd7e718f544bfa3e78f651cc13dbb81`. The plan is the whole file, lines 1–69.

**Read coverage.** Story #344, design #133 sections 2–3 and the reserved-decision close of section 8, the 2026-11-16 #133 replacement decision, the #340 and #341 delivery records, and the #339 paired-feedback record. Product controls were read from `/Users/kpburson/projects/aitm-workspace/trunk` at ref `refs/heads/trunk` = `625b5407978675ac3b906990c8bb0713dcae18fd`, the same commit the plan names as the #340/#341 delivery. That included `tools/ci/path_map.py`, `tools/ci/path_map.json`, `tools/ci/python_gate.py`, the selection and child checks in `tools/ci/verify_pr.py`, `tools/ci/tia/edges.json`, `.github/workflows/ci.yml`, `tools/ci/tests/test_path_map.py`, and the Ledger and Grok fixture consumers under `packages/aitm-usage/tests`. The shell boundary for this review was the join and this submit, so the Task 1 replay command was not executed. `select()` and the map were read directly.

**What holds.** The story's replacement scope is the plan's scope. Ordinary PR validation reuses the base-owned map and the #341 full-once stamp. Scheduled backstop, Stop the Line, and a general selector stay out. Trunk's Python job is `timeout-minutes: 20` with three xdist workers (`workers=3` and `-n 3`). The ledger rule names only `packages/aitm-usage/tests/test_ledger.py`, while `test_scope_admission.py` imports `Ledger` and calls `Ledger.initialize`. The Grok fixture prefix maps `tests/fixtures/grok/` to `test_grok.py`, and `test_grok.py` reads `headless.json`. #339's failing edit is the row refresh plus input tokens 12790 instead of 12789, observed by `test_headless_projection_is_only_corroboration`; the passing correction kept the row refresh and restored 12789. Both CI lanes diff with `git diff --name-only --no-renames --diff-filter=ACDMRTUXB`, so a rename contributes both paths. The selector entry point, `mode` / `tests` / `source` / `key` / `children`, and the base-blob rule match the plan. The focused pytest command is runnable from `packages/aitm-usage`: pytest is a locked dev dependency, `PYTHONPATH=../../tools/ci` matches `from path_map import`, and the gate tests locate the map, policy, and workflow through `__file__`. On a failing mapped push the stamp restore still runs, because its `if` does not include `success()`, and the save step does include `success()`.

**What does not.** Two instructions contradict the acceptance rule they are meant to implement. An unclassified path is both pinned as implicit no-impact and forbidden from checks-only (F001). The full-once stamp is required to be limited to a compatible base and policy, but the task makes that key change conditional even though the live key has neither (F002).

## Findings

### R1-F001 — An unclassified path is pinned as implicit no-impact and also forbidden from that disposition

**Where.** Plan line 44: a documentation-only change uses an explicit trusted no-impact rule, and "Unclassified inputs cannot receive this disposition." Plan lines 51–52: red tests pin "implicit no-impact for an unknown path" and "known no-impact", then "An explicit positive no-impact match is the only route to checks-only" and "An unknown path that lands alongside a known mapping forces full."

**Evidence.** `select()` in trunk `tools/ci/path_map.py` (lines 85–93) skips a path whose rule lookup is `None` when the path is not executable, then returns mode `checks` when nothing was chosen. A non-executable path with no rule, such as `notes/foo.md`, is therefore implicit no-impact today. `README.md` and `docs/` are different: they are explicit rules with `"tests": []`. `test_path_map.py` lines 29–30 keep `sources/grok.py` plus `docs/ci.md` mapped to `test_grok.py` only, and lines 135–136 expect `README.md` alone to be `checks`. Design section 3 allows a no-test selection only when trusted policy positively classifies every changed path. An uncertain path is a broad fallback, not a skip.

**Risk.** The red-test list and the two normative sentences cannot be implemented together. One reading locks today's skip and lets an unclassified file pass as checks-only, which `verify_pr.py` accepts when mode is `checks` and the test count is 0. The other reading fails that red test as soon as the fallback is fixed. "Alongside a known mapping" also leaves the unknown-alone case unspecified, so a lone unclassified path can stay `checks` while a mixed diff goes `full`.

### R1-F002 — Suppressing the extra full run is still keyed only by pull request and selected modules

**Where.** Plan line 13: an earlier full result may suppress the extra full run "only within the same PR and compatible base, policy, and selection." Plan line 53: "If a compatible stamp must be narrowed further, include the base and trusted selection-policy identity in the stamp key, in addition to PR and selected modules."

**Evidence.** `cache_key()` (`path_map.py` lines 37–49) returns `pr-<number>-full-<selection key>`. `_selection()` (lines 96–104) hashes only `mode` and `tests`, or uses the literal `full`. `ci.yml` lines 220–222 publish that string, and lines 311–334 restore and save the Actions cache with it. There is no base SHA and no map or policy digest. `test_cache_key_is_exact_and_rejects_unsafe_values` and `test_workflow_uses_the_base_selector_and_cancels_a_superseded_run` pin that shape (`pr-12-full-…` and `pr-${PR_NUMBER}-full-${key}`). #341's two successful runs shared one selection key and did not record a base or policy identity.

**Risk.** The "if" is already true, and the conditional lets an implementer keep the pinned key. A later push on the same PR whose selected module list is unchanged then skips the extra full suite after the base moves, or after the trusted map changes in a way that does not alter this PR's test list. That is the stamp hole the constraint forbids. The short check would still run, and a missing consumer introduced with the new base or policy would not.

## Required changes

1. **R1-F001.** Replace "implicit no-impact for an unknown path" with the disposition the red test must assert. An unclassified path, alone or beside any other path, cannot end as `checks` or `mapped`; it forces full, or it fails closed when full evidence cannot be established. Keep an explicit empty-test rule, such as `docs/` or `README.md`, as checks-only only when every changed path has that positive classification. State that an explicit no-impact path beside a mapped rule stays mapped to the mapped rule's tests, matching `test_path_map.py` lines 29–30, and that this is not the unclassified case.
2. **R1-F002.** Delete the condition. Require the stamp key to include the pull-request number, the applicable base, the trusted selection-policy identity, and the selected modules before a restored stamp may suppress the extra full run. Say that the current key does not, and that `test_cache_key_is_exact_and_rejects_unsafe_values` and the workflow pin of `pr-${PR_NUMBER}-full-${key}` change with it. Keep the rule that a content-only change, with the same base, policy, and selected tests, repeats the short check and does not start another full suite.

## Optional suggestions

1. The Task 1 replay regex does not see every Ledger consumer. `packages/aitm-usage/tests/test_monitor_ledger_version.py` imports `from aitm_usage import ledger` and calls `ledger.Ledger.open`; it matches neither `from aitm_usage.ledger import` nor `Ledger.initialize`. Say in the replay step that the retained command output is the reproduction of the known gap, and that the independent reverse-import trace, including transitive imports and subprocess strings, is the consumer inventory.
2. Name the cutover for the new per-path `paths` evidence. The control-changing PR still executes the base selector, which does not emit `paths`. New evidence should become required only once that selector is the trusted base. Until then the gate should keep accepting the current selection schema and existing full or legacy receipts.

## Decision

revisions-requested
