<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c67668584e194f580a3052e8f2cef4de"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md"
artifact_commit: "db3eb007db8eb004cacf497fd56d372bc579dc8f"
artifact_blob: "88b136427216f6b21324b27d9c8545bc3b3e98f5"
artifact_digest: "sha256:82d010f80234aed2bace6d51c591ddaec3b03c9b6e38f6295297ad9a56baefbb"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0135f0bf409b44d81249f9ed0ca7917c5525cab72e6b3d74ac0b3c6a2f8231f0"
  identity_source: "runtime"
started_at: "2026-11-17T00:22:18.541Z"
submitted_at: "2026-11-17T00:25:30.881Z"
finding_ids: ["R1-F001","R1-F002"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is an independent review of `.aitm/stories/003/355/plan/2026-11-16-355-pre-commit-execution-plan.md` at blob `88b136427216f6b21324b27d9c8545bc3b3e98f5`, commit `db3eb007`. The artifact digest is `sha256:82d010f8…baefbb`, which matches the plan SAR and the `implementation-plan-sar` event in `355/events.jsonl`. I reviewed the whole plan, lines 1–38.

**What I read.** I read story #355 and its events, the epic #351 story, the #133 decomposition row, and the plan SAR. For #353 I read the accepted finding and its independent review. For #354 I read the plan, the verified delivery JSON, the delivered CLI probe, source review round 2, the delivery retro and the closure receipt. I also read the #146 selected-observation findings. I opened `tools/ci/path_map.json` and `tools/ci/tia/suites.json` read-only in the local trunk checkout `/Users/kpburson/projects/aitm-workspace/trunk`. That checkout has no `working_tree_report.py`, so it predates `8218a69`. Git was out of bounds, so I did not verify its exact ref. This review ran only the join command and will run only the submit command. I executed nothing else.

**What I verified.** Plan line 7 names base `8218a69…`, tree `90f2cc40…`. Both match `354/plan/2026-11-16-354-verified-delivery.json` and the #354 closure receipt. Plan line 17 cites 30 IDs and inventory `812bc918…`. Both match the delivered CLI probe's `admitted-comment` case. That probe used the same `-B -E -s` invocation and returned `unsupported-change` for the extra-path control. Plan line 30 says #354 accepts only its own four-file delivery shape. That matches #354 plan line 15: HEAD must be the anchor, or the anchor plus exactly the four delivery paths. Otherwise the report returns `unqualified-base`. A #355 merge therefore makes the report unusable unless it is requalified, as the plan says. Line 11 summarizes #353 correctly: the stock route is cooperative, and the controller-observed exit is necessary but not sufficient. Line 18 summarizes #146 correctly: the selected route was hosted and used instrumented CPython/DTrace with a reviewed executable suite. The trunk checkout's `suites.json` does not list `test_grok_scope_receipts.py`, while `path_map.json:46` does. That agrees with the SAR's claim that the stock local suite policy lacks the audited module. Line 19 is consistent with this.

**What holds.** The plan does qualification first and fails closed. Task 1 stops before any candidate pytest or feature source when the boundary is absent. Task 2 is gated behind a provider-specific addendum with its own SAR and XPR. The plan treats the two `unqualified` report fields as limits on the claim, not as admission failures. It also keeps observed failures distinct from indeterminate runs. All of these match the #353 handoff.

**What does not.** The plan states that the story requires the strict, independent tier, but the story does not say so. On a HOLD, the plan names no route that would let the story deliver anything (F001). Task 1 does not list which local mechanisms it will check. A HOLD therefore cannot show that the search was complete, and an executor cannot tell when Task 1 is finished (F002).

## Findings

### R1-F001 — The plan asserts a strict-only scope that the story text does not require, and its HOLD exit gives no next route

**Where.** Plan line 5: "report an independently supported pass or fail". Plan line 11: "The accepted #353 finding permits cooperative feedback under a declared scope, while this story's strict result requires the independent boundary." Plan line 21: on HOLD, "record the #355 blocker … and stop".

**Evidence.** Story #355 line 33 asks for less: "An agent can run that list and get a pass or fail while the rest of the suite stays unrun." The story uses "the process boundary from the accepted #353 receipt." That receipt has two tiers. #353 findings line 25 says: "Under cooperative reviewed-code scope, a local advisory verdict can join the real child exit to a complete matching receipt and report its limits." It reserves refusal for strict trusted execution. The epic is the only text that supports the strict tier. Epic #351 line 38 says "#353 names the process boundary a **trusted** pre-commit run needs." The #353 spike title also says "trusted local test observation". The plan cites neither.

**Problem.** The plan rules out new accounts, entitlements, privileged configuration and hosted runners (line 13). The only qualified precedent is #146's hosted, instrumented-interpreter route. #353 classes the stock local route as cooperative. Under these constraints, HOLD is the most likely result of Task 1. When the plan reaches HOLD, it records a blocker and stops. It does not tell the owner that a declared-advisory variant is available under the accepted #353 finding. It also does not say who decides between that variant and provisioning a new boundary. The tier choice determines whether #355 can deliver anything, and the plan presents that choice as settled by the story without citing a source.

**Failure scenario.** Task 1 correctly finds no qualified local boundary and publishes HOLD. The story stops with "blocker recorded". The owner reads that the strict boundary is unavailable, but not that the accepted #353 finding already permits an advisory pass or fail with declared limits for this exact list. Planning time is spent, and the epic's goal, "an agent runs the tests affected by uncommitted work before commit", stays blocked by a scope decision that nobody was asked to make.

**Required change.** In Architecture (line 11), cite the authority for the strict tier: epic #351 line 38 and the #353 spike title, or an owner decision if one exists. Then require the Task 1 HOLD receipt to state the exact next condition as an owner decision between two options:

1. Provision a qualified independent boundary as a separate, re-estimated scope. Line 7 already allows this.
2. Re-scope #355, or split a sibling story, to deliver the #353 cooperative advisory result. That result would use the real child exit plus a complete matching worker receipt. It would be labeled advisory and not trusted, with the limits stated.

The plan must not pick option 2 itself. It must only surface both options in the receipt.

### R1-F002 — The Task 1 search for an "already governed execution boundary" has no enumerated candidates, so neither a PASS nor a HOLD can be checked for completeness

**Where.** Plan line 11: "qualify a locally available, already governed execution boundary". Line 18: "any already approved local route referenced by the project … read-only available host identity and named mechanism facts". Line 20: "use a previously authorized isolated runtime".

**Problem.** Line 20 requires the HOLD record to state "exactly why the source supports the conclusion". The plan never says which mechanisms Task 1 must examine, or which read-only fact proves each one eligible or ineligible. "Named mechanism facts", "already approved local route referenced by the project" and "previously authorized isolated runtime" have no referents in the plan or its cited inputs. An executor cannot tell when the search is complete. One executor could stop after the stock `local.py` route. Another could spend the 3-hour budget probing sandbox or container tooling. A reviewer of the qualification receipt cannot check that a HOLD was not premature, or that a PASS did not rest on a mechanism outside the governed set.

**Failure scenario.** The executor checks the stock controller and #146, finds both ineligible, and publishes HOLD. A pre-existing, project-approved isolation route was never examined, and nothing in the plan would have caught the omission. The reverse can also happen. The executor finds an installed but unapproved isolation utility and treats it as "available", even though line 11 excludes it.

**Required change.** In Task 1, list the candidate boundary mechanisms that this attempt examines, with the read-only fact that decides each one. For example:

1. The stock `tools/ci/tia/local.py` controller. This is diagnostic and cooperative per #353.
2. The #146 hosted controller and instrumented-interpreter/DTrace route. This is hosted and historical, and outside this local scope.
3. A pre-existing distinct OS principal that the worker can use without any account or privilege change.
4. An already-installed, project-approved OS-enforced sandbox, container or VM runtime, with the project record that approves it.
5. Native tracing under the host's current protections, with project-reviewed instrumentation.

State that any mechanism not on the list is outside this attempt and goes to the line 7 scope decision. Require the qualification receipt to give PASS or HOLD for each listed mechanism with its deciding fact.

## Required changes

1. **R1-F001.** Cite the source of the strict tier in Architecture: epic #351 line 38, the #353 title, or an owner decision. Require the Task 1 HOLD receipt to name the owner decision between (a) provisioning a qualified boundary as a separately estimated scope and (b) re-scoping to the #353 cooperative advisory result with declared limits. The plan does not select either option.
2. **R1-F002.** List the candidate boundary mechanisms that Task 1 examines and the read-only deciding fact for each. Declare unlisted mechanisms out of scope. Require the qualification receipt to give PASS or HOLD for each listed mechanism.

## Optional suggestions

1. **Byte-comparable replay.** In Task 1 line 17, pin the expected values from the #354 delivered probe for the reproduced admitted comment: `content_sha256` `d71cd585…101647`, `snapshot_sha256` `4c200d09…c9727d`, and `unsupported-change` for the extra-path variant. A replay can then be compared to the delivered evidence byte for byte, rather than only by its ID count.
2. **Trusted tooling identity.** Line 17 runs the report "from a trusted checkout". Say that this checkout must be at `8218a69` / `90f2cc40`. #354 requires the tooling selector bytes to equal the anchor's (#354 plan line 20), so a tooling checkout at another commit can fail differently.
3. **HOLD state.** Name the story state (for example `blocked`) and the Project 24 Status that HOLD sets. Also name what unblocks it. Line 21 says only "record the #355 blocker". A HOLD stops the story without any independent check. Consider a short independent readback of the qualification receipt, matching the SAR plus XPR that a PASS gets through the addendum.
4. **Undefined terms.** Define "strong authority" (line 28) and "named mechanism facts" (line 18), or replace them with the concrete checks they mean.

## Decision

revisions-requested
