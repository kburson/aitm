# Usage capture delivery leaves

Accepted [baseline implementation plan](usage-capture-implementation-plan.md), raw SHA-256 `07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5`. The [accepted amendment](usage-capture-replan.md) at raw SHA-256 `7df41b26c4b4f9ce786807832ba544862560eac1e297a22c497fb31791f5c239` brings the total to **13 leaves, 48.5 implementation agent-hours**. Every leaf is estimated at four hours or less. [Original native issue receipt](leaf-issue-receipt.json) · [Revised native issue receipt](leaf-replan-receipt.json).

The collector activation and on-host proof are the project sequencing prerequisite for [Core C01 / #3](../../3/story.md). Work on the accepted Core decomposition follows that checkpoint. The plan and links record scope and order. Individual leaf design, plan, JIT and delivery evidence follow the normal workflow.

| Key | Issue | Hours | Required predecessors |
| --- | --- | ---: | --- |
| U01 | [#84](../../84/story.md) | 4 | — |
| U02 | [#85](../../85/story.md) | 4 | #84 |
| U13 | [#86](../../86/story.md) | 3 | #85 |
| U03 | [#87](../../87/story.md) | 3.5 | #85 |
| U04 | [#88](../../88/story.md) | 4 | #87 |
| U05 | [#89](../../89/story.md) | 3.5 | #87 |
| U06 | [#90](../../90/story.md) | 3.5 | #86, #88, #89 |
| U07 | [#91](../../91/story.md) | 3.5 | #86, #90 |
| U08 | [#92](../../92/story.md) | 4 | #91 |
| U12 | [#93](../../93/story.md) | 4 | #92 |
| U09 | [#94](../../94/story.md) | 4 | #93 |
| U10 | [#95](../../95/story.md) | 3.5 | #94 |
| U11 | [#96](../../96/story.md) | 4 | #95 |
