[05:12:39]
HOLD

The direction is sound. Containing the unqualified Claude Agent overlap as `OVERLAP_UNVERIFIED`, keeping #204 open and swapping only #204's direct #119 edge after the replacement edge is verified all fit the accepted M08b5 exit clause. The #272 findings also justify the change. The exact amendment still has five gaps that stop it from safely unblocking #119.

**Blocking findings**

1. **Same-stream progress is not defined, so it can't be tested.**
   - **What the draft says:**
     - It requires that "genuinely eligible ordinary work still reaches its existing route."
     - It also says a mixed stream "can also delay" later ordinary work, and a gap "may hold" later eligible work "until that source can safely reconcile."
     - While #204 is open there is no way for that source to reconcile, so the hold is effectively permanent.
     - "Do not skip the held interval" and "preserve the prior replayable frontier" conflict with the existing hold rule. That rule records an explicit gap and discards replay state when retention or the hold limit runs out.
   - **Fix:** State one exact outcome for later ordinary requests on the affected stream: held, or routed past a keyed gap. Define the stream's state when the hold limit or provider retention runs out. Say which rule takes precedence and what the reported backlog range is in each case.

2. **The replacement's scope contradicts its own dependencies.**
   - **What the draft says:**
     - The title says "Contain and report," and the scope adds rules for user-facing report labels.
     - The handoff says the replacement doesn't depend on M09, M12, M13 or M14, and that gap display belongs downstream.
     - "Past snapshots intact" also points to M12/M13 publication, which doesn't exist before M09.
   - **Fix:** Limit the replacement to journal-level containment, the cursor/frontier and independent progress. Move the report-label and snapshot rules to M12–M14 as exact amendments, and rename the issue to match.

3. **The fixture's expected results are missing.**
   - **What the draft says:** The fixture must cover an unrelated diagnostic, a retry and a late child record, but it never says what should happen to each.
   - **Why it matters:** M08b4 already says genuine diagnostics and mixed cases hold progress. A retry of an ambiguous parent request and a late child each need a stated keyed outcome.
   - **Fix:** For each case, state hold or route, cursor effect, and usage effect. Name the replacement's contract and tests the same way the other leaves do. Require the fixture to be sanitized and allowlisted; deriving it from "retained genuine" evidence without that conflicts with the private-trace rule in M17/M18.

4. **Where the folded-positive check lives is unclear, so a cycle isn't ruled out.**
   - **What the draft says:**
     - #204 is a pre-M09 journal leaf, but the moved folded-positive check needs M09's actual write ACK and one atomic publication. That requires work after #119.
     - "No reverse edge back to this qualified-source release" is ambiguous.
     - The M09 leaf text in the packet still lists `test_folded_replacement_and_child_withdrawal_share_view` and the folded-replacement contract.
   - **Fix:**
     - Name the issue that carries the post-M09 integration and its edges, for example #119 → integration and #204 → integration.
     - Add any #119-blocking-#204 edge only after the #204 → #119 edge is removed and verified.
     - Include the exact amended M09 leaf text, which replaces the folded test with the negative control.

5. **The scope of the export amendment isn't exact.**
   - **What the draft says:** "Surface the known gap … in reports and exports" doesn't say which exports.
   - **Fix:** Restrict it to the versioned monitor export. State that #83 fixed-sequence exports and C44's compatible payloads stay unchanged. Require the backlog/gap range to be sanitized: no source path, raw provider ID or sibling identity.

**Checks that passed**
- **Prerequisite set:** {118, 199, 201, 202, 203, 209, 210, replacement} matches current state. Everything except #204 is closed.
- **Edge order:** creating and verifying the replacement edge before removing the #204 edge is correct.
- **Order and #204:** M11 and Grok stay after #119, so parent order is unchanged. #204, #270/#272/#273 and #282 stay outside the release chain.
- **Privacy rules:** no estimated ledger adjustment, no fabricated ACK, and project/story labels only where scope supports them.
- **Qualification:** M17–M19 keep their requirements except the folded positive for this carrier. Production cutover is still excluded.

To re-review, please resubmit with exact replacement issue text and named tests, plus the exact amended text for M09, M12–M14, M17–M19 and NA-1.
