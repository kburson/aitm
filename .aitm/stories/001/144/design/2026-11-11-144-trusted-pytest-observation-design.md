# #144 design — Trusted pytest observation prerequisite refusal

**Leaf design.** Wave 30, Rank 30, #133 T07. Author and assigned implementer: Codex / story144, acting for kburson. Wave owner retains planning publication, Project, issue and remote actions. The wave's proposed deliverable is a sanitized, dated refusal record; this design is not that record or a qualification result.

## Purpose and source of authority

The leaf asks whether an observer independent of the candidate can establish complete pytest collection before assignment and actual execution afterward. [#144](../story.md) inherits [accepted #133 design §4](../../133/design/test-impact-analysis-design.md#4-inventory-shards-and-test-evidence), raw SHA-256 `2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928`, and [accepted T07](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L268), parent plan raw SHA-256 `ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7`. T07 permits a bounded controller recommendation or an explicit refusal. This design uses the refusal route because the mandatory prerequisites have not been verified.

[#139 / T02](../../139/story.md) supplies the classifier and provenance distinction, not independent observation. The pinned comparison source is `trunk` commit `56266ed30bbc572b7e56bc64777e802be264c23f`, tree `8028f12297fbb3ce6012ad238e2242cfd2f2e839`, from [#139 delivery](../../139/plan/2026-11-11-139-final-delivery.md). No trial candidate, runner identity, run or attempt exists for #144.

## Gate before any trial

A later pickup would need explicit owner authorization for a named, isolated macOS/APFS target, with verified filesystem and native process capability, and evidence that an independently controlled observer and protected evidence channel can operate under a separate principal. A capability receipt would have to pin the approved target, isolation boundary, platform and filesystem, immutable source and tree, applicable base/head, lock and toolchain, policy and controller identities, observer principal and evidence custody. Bind any later observations to that capability, exact scope, run and attempt; bind execution to the prior complete collection and exact assignment. Do not mint a capability receipt or substitute historical #103 evidence for this gate.

At the initial readback (2026-11-12 01:52:11 UTC), GitHub's repository runner endpoint returned `total_count: 0` and an empty runner list. This is limited to the repository's returned self-hosted runner inventory. No authorized isolated macOS/APFS target, separate observer principal or protected observation channel was verified in the wave's available evidence. The runner response does not establish absence of hosted, organization or other runners elsewhere. The established #103 CI path is separate and is not available to this trial. No provisioning, dispatch, runner probe, fixture execution, implementation, or alteration to CI or production is in scope. Any later trial needs a new owner decision and reviewed pickup under applicable safety boundaries; this record confers no authorization.

## Defensive evidence requirements and current dispositions

Candidate code in a pytest process can affect collection, test behavior, and reported outcomes. A correctly formed report, matching digest, artifact attestation or successful process exit can attest to facts about a report or invocation, but cannot establish complete collection or actual per-obligation execution. Separate control and custody are necessary; they do not by themselves prove what happened inside pytest. Independent source review still evaluates the meaning of the tests.

These rows describe acceptance evidence only. The observation status of every row in this wave is **Not run**; there are no fixture observations, successes, failures, or observed gaps in individual shards.

| Acceptance case | Evidence required before a positive qualification decision |
| --- | --- |
| Known complete collection and ordinary execution | Independently establish all applicable IDs before assignment in both modes. Observe the assigned IDs and their actual outcomes afterward. Full mode covers every applicable obligation; selected mode identifies the exact subset and records unselected outcomes as unobserved. |
| Same-shape receipt from an untrusted source | Refuse it as evidence of collection or execution without an independently trusted observation and exact binding. |
| Missing required collection ID, including a newly applicable ID | Establish completeness independently or refuse before assignment in both modes; comparison to a matching base inventory alone does not establish completeness. |
| Reported pass without independently verified execution, including a substituted in-process outcome | Require evidence of actual execution and outcome for each assigned ID in both modes. Refuse an unverifiable outcome even when in-process output is green. |
| Authenticated failure with a missing sibling shard | Preserve any verified test failure and the separate missing-evidence disposition. An incomplete aggregate cannot pass. |
| Required native child-process coverage | Require independently supported child activity and coverage tied to the exact obligation, source and attempt. Missing proof prevents qualification for the affected scope. |

Full execution is eligible as a fallback only if it can meet the same trusted evidence requirements. No trial here means the boundary is **unqualified and untested**, with no claim of a discovered defect, failure, or impossibility.

## Deliverable and disposition

The leaf plan must name an immutable, documentation-only refusal target on planning and define validation and independent review of its exact bytes. The report should carry dated, sanitized prerequisite evidence and limitations, the source comparison identity, explicit unrun dispositions, attribution and next action. Keep private paths, transcripts, logs, credentials and sensitive runner identifiers out of publication. There is no source candidate, product PR, activation, or hosted CI evidence for the refusal. Acceptance of the record would be acceptance of the scoped refusal only.

Preserve the capability hold on [#145/T08](../../145/story.md), [#146/T09](../../146/story.md) and their dependent work, even if the refusal record is later administratively delivered. Return the trust boundary to #133 design review. Before a new pickup, the owner must resolve authorization and demonstrate both prerequisites, or replan. Keep [#103](../../103/story.md) as the existing gate authority and local advisory available within its existing scope. #158 and #159 are outside this wave.
