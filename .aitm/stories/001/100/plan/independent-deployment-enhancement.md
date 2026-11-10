# Cross-agent usage monitor deployment follow-on plan

Proposed work after base product proof. Use the
[enhancement design](../design/independent-deployment-enhancement.md)
and the [accepted monitor plan](multi-project-usage-monitor-implementation-plan.md)
as separate inputs.

| Candidate story | Result and verification |
| --- | --- |
| Independent distribution | Stage a versioned product artifact and operator configuration. On a clean qualified host without AITM-Core, verify install, enrollment, service start, report/export, upgrade, and removal. Recheck the legacy command and export compatibility. Split by supported host when required to meet the four-hour leaf cap. |
| Optional Core adapter | After the standalone artifact and compatible receiver are proven, qualify installed-but-disabled, explicitly enabled, missing, and incompatible combinations using a pinned released Core. Verify matching exports, redacted data and Unknown preservation without starting a second monitor. |

Refine and review these stories separately after the base monitor has
qualified. Identify the release channel, artifact name, support matrix,
and publication authority then. Qualification evidence and an approved
release are separate gates.
