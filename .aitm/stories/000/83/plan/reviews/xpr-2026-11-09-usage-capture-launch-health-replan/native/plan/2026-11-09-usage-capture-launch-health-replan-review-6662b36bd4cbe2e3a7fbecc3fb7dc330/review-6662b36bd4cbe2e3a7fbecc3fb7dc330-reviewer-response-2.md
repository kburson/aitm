<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-6662b36bd4cbe2e3a7fbecc3fb7dc330"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-launch-health-replan.md"
artifact_commit: "64e425817c676f8d71fdf0e9cffed749aac367bb"
artifact_blob: "c14822dfeeca657b1a20083685ca8fcaabae4e1b"
artifact_digest: "sha256:a7cdf82a5cb1bf215b13e1b286d38cae55cfc18d2d6007dcb86cd9aef1aa66e6"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:e4fa9f0da9324635d8b92a67b1ff93fb5fb7f68f34b4b3caea236c8cc5903284"
  identity_source: "runtime"
started_at: "2026-11-09T20:45:50.472Z"
submitted_at: "2026-11-09T20:50:41.598Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 2 of the independent XPR review of `.aitm/stories/000/83/plan/usage-capture-launch-health-replan.md` at sealed digest `sha256:a7cdf82a5cb1bf215b13e1b286d38cae55cfc18d2d6007dcb86cd9aef1aa66e6` (commit `64e4258`, blob `c14822d`).

**Read evidence.** I read the current artifact fresh with the Read tool in two contiguous ranges of at most 20 lines each. The first call (offset 1, limit 20) returned lines 1–20. The second call (offset 21, limit 20) returned lines 21–23 and reached EOF at line 23, which is blank. Coverage is complete: lines 1–23 of 23. Neither call was truncated or replaced by an omission marker. I also read author response 1 (lines 1–52, EOF) in full. For the turn-1 baseline, I relied on my own turn-1 reading of the prior 17-line artifact at `sha256:92052b10…`, not on the author's summary.

**Disposition verification.**

- **F1: resolved.** Line 22 now covers the gap I raised:
  - a fixed sanitized environment for every retained-runtime execution before acceptance and for the installed launch route;
  - refusal of unapproved plist environment overrides;
  - an isolated launcher, or equivalent controls, on the exact ProgramArguments console, so that caller or launchd Python variables, user/global site and working-directory imports cannot bypass the verified runtime;
  - an isolated no-site probe of the pinned base interpreter;
  - a test that an injected startup path executes nothing.

  This closes both channels I identified: caller variables and launchd `setenv`/plist variables. The line 9 filesystem inspection is retained alongside it.
- **F2: resolved.** Line 9 now has prune refuse before deletion in each of these cases:
  - the retained backup, recovery wheel or any required recovery material would be deleted with the selected runtime directory;
  - the runtime, or its plist or environment, is referenced by an unretired interrupted-upgrade record.

  Physical-ancestry validation applies, and each protected case is tested. This matches the required change exactly.

**Optional suggestions adopted.**

- O1 (PID reuse): line 22 checks the same OS process incarnation before and after the health read, using the actual start identity as well as the PID. The heartbeat must follow that start, so U08's witness surface does not grow.
- O2: line 9 retains the verified backup digest after a successful restore or prune.
- O4: line 16 names U10 at 3.5 agent-hours.

**New content check.**

- *Legacy compatibility (line 20).* An older status payload keeps its ordinary heartbeat and watermarks, and its mode and PID are Unknown. Unattended upgrade of a witness-incapable runtime is refused before the running service stops. A recovery to an older registration keeps explicit evidence and withholds qualification. This is consistent with line 7's "Unknown for activation" and fails closed.
- *Already-active retry (line 22).* The retry uses the same running-process witness, and the heartbeat must follow the process start. A stale heartbeat cannot qualify without a new bootstrap.

**Unchanged and still holding.** Several turn-1 conclusions still hold:

- The live PID plus service-mode predicate and the immutable store and backup boundaries are intact.
- The recovery sequence is intact: preserved `05318125…` and `1d0dd02b…`, the #92 repair, the U12 rerun, the #94 re-pin, a cumulative independent review, then #95.
- The estimates are unchanged: U08, U12 and U09 at 4, U10 at 3.5, and 48.5 in aggregate, all within the cap and under a stop rule.
- #83 remains the permanent collector, and all qualification stays #83-only.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Owners for the new section.** Line 20 mixes U08 work (reading legacy status) with U09 work (refusing before the stop and the recovery disposition). Line 22 is U09 work. Naming those owners inline would make the leaf file boundaries unambiguous at pickup.
2. **"Known witness-incapable installed runtime" (line 20).** The text could say whether this means the upgrade target or the currently installed source. If it means the installed source, it should also name the attended path that eventually moves such an installation onto a witness-capable runtime.
3. **U09 cap pressure (carried from turn 1).** U09 now also absorbs the launcher and environment isolation, the start-identity check and the protected prune cases, all at the four-hour cap. Its JIT should forecast these explicitly so the stop rule triggers early.

## Decision

accepted
