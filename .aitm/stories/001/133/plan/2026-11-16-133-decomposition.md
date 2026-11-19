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
| #351 | epic | 430 | Select the tests affected by uncommitted work |  | — |
| #352 | spike | 440 | [Spike] Name the condition that blocks local test selection | #351 | — |
| #353 | spike | 450 | [Spike] Find the process boundary for trusted local test observation | #351 | — |
| #354 | story | 460 | Report the affected tests for the working tree | #351 | #352 |
| #355 | story | 470 | Run the affected tests before commit | #351 | #353, #354 |
| #356 | epic | 480 | Shard tests by execution category |  | — |
| #357 | spike | 490 | [Spike] Classify tests into execution categories | #356 | — |
| #358 | spike | 500 | [Spike] Find what blocks parallel category runs | #356 | #357 |
| #359 | story | 510 | Run a local full sweep as category shards | #356 | #357, #358 |
| #360 | story | 520 | Run a CI full sweep as category shards | #356 | #359 |
| #361 | story | 530 | Schedule the category-shard full sweep | #356 | #360 |
| #362 | epic | 540 | Flag a scheduled build failure |  | — |
| #363 | spike | 550 | [Spike] Identify the run a failure flag should watch | #362 | — |
| #364 | spike | 560 | [Spike] Find where a person and an agent can read one flag | #362 | — |
| #365 | story | 570 | Record the scheduled-failure flag | #362 | #363, #364 |
| #366 | story | 580 | Show the scheduled-failure flag when it is checked | #362 | #365 |

Owner moved this block after rank 420. The ranks are 430 through 580, ten apart.

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

## Platform-agnostic TIA

Owner decision on 2026-11-18, corrected the same day. TIA is one Python program. Linux, macOS, and later Windows supply a CPython interpreter and run that same source.

The job is the test list for a change. Compare the staging area, or HEAD, with the commit where the branch diverges from its parent branch. Follow the chain among tests, imported functions, and libraries, and unwind it to the application. #371 analyzes the Python language facility that makes that program cross-platform.

The owner develops on macOS. Windows stays a later epic for Windows facilities and is not opened here. The hosted `macos-26` queue shortage remains a runner fact recorded on #355. #355 stays on the accepted advisory command.

| Issue | Kind | Rank | Title | Parent | Blocked by |
| --- | --- | --- | --- | --- | --- |
| #370 | epic | 480 | Select affected tests with one Python program |  | — |
| #371 | spike | 490 | [Spike] Analyze how one Python TIA program runs everywhere | #370 | — |

#356 through #366 moved up by 20 so the gap stays 10. Their ranks are now 500 through 600. This order is a note, not a blocker edge. #351 still closes when #355 delivers. #371 writes the finding. A feature story for #370 is opened after that finding is accepted.

Owner direction later the same day, recorded in [the #370 plan](../../003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md). The Linux suite cleanup comes before the TIA probe. After that cleanup every required test runs on Linux. The probe then lists the tests for a staging area, a commit, or a pull request. The same Python program runs wherever CPython and git are installed.

## Linux suite epic

Owner request on 2026-11-18T23:38:27Z. Filed #372 Run the required suite on Linux at rank 480 with five stories:

| Issue | Kind | Rank | Title | Parent | Blocked by |
| --- | --- | --- | --- | --- | --- |
| #372 | epic | 480 | Run the required suite on Linux |  | — |
| #373 | story | 490 | Prove private ledger custody without APFS | #372 | — |
| #374 | story | 500 | Supervise the service without launchctl | #372 | — |
| #375 | story | 510 | Refuse an extra file grant without a macOS ACL | #372 | — |
| #376 | story | 520 | Run product tests on the Linux runner | #372 | #373 |
| #377 | story | 530 | Remove tests that require a Mac | #372 | #373, #376 |

#370, #371, and #356 through #366 moved up by 60 so the gap stays 10. Their ranks are now 540 through 660. This order is a note, not a blocker edge. The Linux suite cleanup comes before the TIA probe. #133 stays done and does not gain these issues as children.

## Mac tests come off first

Owner correction on 2026-11-19T01:20:00Z. GitHub is limiting macOS CI instances. The required `python-base` and `python` jobs run on `macos-26`, so a story that still needs those jobs cannot pass CI. #377 is first. It removes the tests that require a Mac and moves those two jobs to `ubuntu-24.04`. #373, #374, #375, and #376 wait on #377.

| Issue | Kind | Rank | Title | Parent | Blocked by |
| --- | --- | --- | --- | --- | --- |
| #372 | epic | 480 | Run the required suite on Linux |  | — |
| #377 | story | 490 | Remove tests that require a Mac | #372 | — |
| #373 | story | 500 | Prove private ledger custody without APFS | #372 | #377 |
| #374 | story | 510 | Supervise the service without launchctl | #372 | #377 |
| #375 | story | 520 | Refuse an extra file grant without a macOS ACL | #372 | #377 |
| #376 | story | 530 | Run product tests on the Linux runner | #372 | #377 |

The filed table above stays as the record of the first filing. Ranks 480 and 540 through 660 stay. #133 stays done and does not gain these issues as children. There is still no blocker edge between #372 and #370.
