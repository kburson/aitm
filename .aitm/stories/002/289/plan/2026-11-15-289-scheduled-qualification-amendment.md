# #289 Scheduled execution and deadline qualification

The original plan required a genuine scheduled hosted run to match the daily slot. The configured slot remains 03:47 UTC with a 45-minute grace period. A run registered beyond that window cannot supply current green evidence, clear an incident, or satisfy the daily deadline. Preserve the current reader and incident adapter behavior.

For this shadow story, a genuine completed GitHub schedule event on exact protected default trunk may independently demonstrate scheduling, full execution, and artifact custody even when it arrives late. Record the late execution as a historical result with its exact provider run, attempt, test inventory and artifact digest. Require a separate native reader result marking the daily slot incomplete, verify that the incident adapter refuses this result for recovery, and retain the existing tested warning and recovery handoff for authenticated observations. The independent reviewer must cover both the historical execution and the daily deadline before closure.

This amendment supersedes the original plan's in-window requirement for closing the shadow implementation story. #291 will rehearse the human-operated hold. #294 retains the review of operationally reliable backstop recovery before any production cutover. #103 and the effective trunk rules remain as deployed.
