# Verdict REVISIONS REQUIRED

Read all 237 numbered lines in the seven requested shell calls. The plan SHA-256 matches the author response: `1f2bd6312b236ca2358333b8f3c97ce6d7132bddbe5dd2d800968be23be2c90e`. The receiver recovery, operator paths, and native qualification findings are resolved. Two blocking changes remain.

1. **High — Close the cutover rollback crash windows.** Plan lines 145–147, 197, 208–211. Spec lines 65–69. M16 captures the backup before stopping the legacy writer, then confirms a final checkpoint without saying what happens if the writer advanced. It also makes rollback depend on a first-write marker without specifying how recovery detects a durable project write if the process dies before recording that marker.

   **Required change.** Under the original writer guard, verify that the rollback bundle matches the final legacy checkpoint. If it differs, capture and verify a matching bundle or refuse cutover. Define how recovery detects the first durable monitor write, including a project commit whose ACK or marker was interrupted. Allow legacy restore only when the absence of new writes is proven.

   **Test acceptance.** Commit a legacy write between backup and stop, then prove rollback preserves it or cutover refuses before migration. Crash after the first durable monitor write and before its ACK or separate marker. Recovery must retain that observation and refuse to restore the legacy bundle over it.

2. **Medium — Define how a summary creates a reopenable snapshot ID.** Plan lines 179–184, 190–192. Spec lines 59–61. M13 specifies how to open a durable fenced manifest, but leaves out how a read-only `report projects` invocation binds its requested window and rate basis to an ID. Two summaries can use the same fenced publication with different inputs. The publication ID alone cannot identify both summaries.

   **Required change.** Assign M13 the contract for issuing the summary ID and resolving it on drilldown. The ID must bind the exact fenced publication, UTC window, and rate basis. Specify who persists the binding if persistence is required.

   **Test acceptance.** Request two summaries over the same publication with different windows, then request another after a rate-card update without a new usage write. Reopen each ID from a separate process after restart. Each drilldown must reproduce its original interval and pricing or return explicit unavailable if a pinned input has expired.
