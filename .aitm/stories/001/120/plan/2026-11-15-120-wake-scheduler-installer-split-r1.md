# #120 M10 scheduler and native installer split

The accepted M10 includes a scheduler, private wake ingress, generic sender, explicit park, three native installers, and the Grok prompt-scoped producer. Independent Refine held at about 6.0 implementation agent hours. Retain its existing four-hour cap and the accepted product scope by splitting the installer receipt and provider-specific producer coverage into a separate Epic #100 child.

## #120 private wake ingress and park scheduler

Keep #120 at Rank 240 under Epic #100. It owns monitor_scheduler.py, the scheduler-facing part of monitor_control.py, monitor park in cli.py, and the generic HookSender and stable launcher contract in sources/hooks.py. It adds private ingress, transient approved-source resolution, keyed wake scheduling, bounded work, explicit park, and observable wake retirement. Use a fake coordinator and isolated private state for native socket ownership and denial tests. Retain the approved-source gate, delivery cursor custody and workflow scope behavior.

JIT must freeze the exact native socket address limit, pinned bind-and-verify strategy, Darwin getpeereid and Linux peer-credential contract, native payload and wall-clock budgets, fairness quota, monotonic scheduling and unfinished-wake recovery. Explicitly accept any acknowledgment interface added to notify and take_due. Specify the private launcher settings authority and distinguish durable pending hints from process-local scheduling leases. Test a failed scan and crash before completion without retiring the durable work. Preserve exact #119 replay behavior. Estimate 3.5 hours, Size M, pending narrowed Refine and JIT.

The prerequisite set stays #115 and #119. #121 consumes the scheduler and ingress and owns the running coordinator, native root watchers, wake completion and fallback reconciliation. Its three existing incoming prerequisites #115, #120 and #304 stay intact.

## M10b owned native wake hook installers

Create a direct Epic #100 child titled "[M10b] Install owned native wake hooks" after this amendment receives independent PASS. Assign Rank 285 after #124 at 280 and before #125 at 290, and a provisional estimate of 2.5 hours, Size M. #120 is its only incoming native dependency. M07 #117 and Grok carrier #115 are already Closed. M07 is reached transitively from #120 through #119 and #118.

The new child owns monitor hooks install in cli.py, provider-specific hook descriptors and producers in sources/hooks.py, isolated install fixtures and the Grok prompt-scoped producer. It reuses the approved-source checks, private launcher settings and generic wake sender from #120. Deliver owned user-local Codex plugin, Claude Code hook entry and Grok Build hook file, preserving foreign settings, native trust and unchanged tracked project files. Run install twice in isolated homes and test a refused install without loss of existing authority. Use the pinned provider event and compatible target package, and keep native activation and release proof in the existing rehearsal and qualification stories. The Grok producer follows M05 carrier and M07 admission, then joins durable completion. A generic wake never issues a marker.

#125 owns installed-service rehearsal and must also wait for M10b. Its existing #121, #124 and #304 prerequisites stay intact. #121 does not acquire an installer prerequisite. Later rehearsal and native qualification still require their existing evidence.

## Activation evidence

Before declaring the split active, verify the new registered issue in the correct project and under Epic #100. Read back the #120 to M10b and M10b to #125 edges, #120 and #121's original sets, #125's exact old set plus the new leaf, and the independent siblings. Publish the split and exact review in planning with the new numeric issue and its binding to this amendment. The new child receives its own Refine, JIT, Test, independent source review, verified delivery and native Close at its rank. Narrow #120 after the signed-off graph projection. Epic #2, C01 and production cutover are outside this amendment.
