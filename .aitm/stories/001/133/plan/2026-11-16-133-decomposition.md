# Decomposition of #133

Owner decision on 2026-11-16. #133 delivered the hosted pull-request path map and stays open. The remaining claims are three independent backlog epics. Each epic separates research from development: spike stories answer one question and create no production software, and feature stories deliver the behavior those accepted findings describe.

#133 was large enough that one epic was serving several claims at once. These epics are smaller building blocks. A later block can learn from an earlier delivered block. The epics do not block each other.

## What #133 already delivered

- #340 delivered the path-map check.
- #341 delivered full-suite reuse on that check.
- #344 delivered and verified functional test impact analysis for ordinary pull-request validation.

#133 remains in planning state `develop`. Its children array is unchanged. Its disposition, Actual, and Cost are unchanged. The new epics are not children of #133 and are not GitHub sub-issues of #133.

## Independent epics

| Issue | Kind | Rank | Title | Parent | Blocked by |
| --- | --- | --- | --- | --- | --- |
| #351 | epic | 210 | Select the tests affected by uncommitted work |  | — |
| #352 | spike | 220 | [Spike] Name the condition that blocks local test selection | #351 | — |
| #353 | spike | 230 | [Spike] Find the process boundary for trusted local test observation | #351 | — |
| #354 | story | 240 | Report the affected tests for the working tree | #351 | #352 |
| #355 | story | 250 | Run the affected tests before commit | #351 | #353, #354 |
| #356 | epic | 260 | Shard tests by execution category |  | — |
| #357 | spike | 270 | [Spike] Classify tests into execution categories | #356 | — |
| #358 | spike | 280 | [Spike] Find what blocks parallel category runs | #356 | #357 |
| #359 | story | 290 | Run a local full sweep as category shards | #356 | #357, #358 |
| #360 | story | 300 | Run a CI full sweep as category shards | #356 | #359 |
| #361 | story | 310 | Schedule the category-shard full sweep | #356 | #360 |
| #362 | epic | 320 | Flag a scheduled build failure |  | — |
| #363 | spike | 330 | [Spike] Identify the run a failure flag should watch | #362 | — |
| #364 | spike | 340 | [Spike] Find where a person and an agent can read one flag | #362 | — |
| #365 | story | 350 | Record the scheduled-failure flag | #362 | #363, #364 |
| #366 | story | 360 | Show the scheduled-failure flag when it is checked | #362 | #365 |

Recommended later development order, as a note only: #351, then #356, then #362. That order is not a blocker edge.

When #363 finds that no production scheduled run exists, it names #361 as the story that would create one. #365 then stays blocked until that run exists. #362 still has no blocker edge to #356.

## Research and development

A spike writes a finding. Production code, CI, and the hosted path map stay unchanged in a spike.

A feature implements the accepted spike receipt. It stays blocked until that receipt is accepted. When the receipt says the result cannot be trusted, the feature records that result and stops.

## Starting material

Local selection: #138, #139, #140, #141, #142, #143, #147, #267, #288, and #339.

Category shards: #285, #286, #148, #290, #292, #293, #294, and #337.

Failure flag: #277 and #278 showed an advisory warning with no merge authority. #278 also paused work and named a repair owner. That pause and nomination stay outside #362. #158 showed a merge fence accepting a moved base. The flag stays off the merge route.

## Left closed

The withdrawn stories #144, #145, #146, and #149 through #157, and #159 through #178, stay closed. They are evidence for the spikes. They are not reopened by this decomposition.

## Development

Development does not start from this note. Codex picks up a feature story after the spike receipts it depends on are accepted.
