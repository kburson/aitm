# #133 pull-request feedback replacement

Owner decision on 2026-11-16. Stop the shadow-qualification loop and replace the unfinished #133 scope with two production changes. A full suite of up to 20 minutes is acceptable. An ordinary pull request should run only the tests its paths map to.

## What stays

Delivered evidence stays where it is, including #267, #285, #287, #290, #292, #293, #294, #323, #337 and the #339 packet. #103 remains the full-suite backstop until #340 replaces the ordinary pull-request check. Trunk already runs that full suite with three pytest-xdist workers, so this replacement does not add another worker story. The measured 6 to 9 minute final attempt is that parallel suite. The 22 minute median wait came from 2 to 5 attempts per pull request.

#339 is useful evidence and not a production change. The stock selector refused 250 unclassified tests. An explicit fixture-to-module run then caught the same failure locally in 1m 26s, and skipping the red hosted attempt finished the matched pair 4m 52s sooner. General selection stayed unqualified, and the full gate still ran on the corrected head.

## What closes

Close #338 and #339 without further review or implementation. Close the superseded Backlog leaves #149–#157 and #159–#178. Leave delivered #158 as it is. Remove #133 as a blocker of Core #2. #100 remains a blocker of #2.

## Replacement order

1. [#340](../../../003/340/story.md) makes a maintained path-to-test map the required pull-request check. The trusted workflow chooses the tests. Unmapped executable, workflow, shared-setup and map changes run the full suite.
2. [#341](../../../003/341/story.md) runs that short check on every push and the full suite once for the reviewed head. A superseded run is cancelled. A later push reruns the full suite only when the mapped selection changes or the map falls back.

Neither story adds a scheduled backstop, a merge hold, a workspace pause, or a proof-grade selector.
