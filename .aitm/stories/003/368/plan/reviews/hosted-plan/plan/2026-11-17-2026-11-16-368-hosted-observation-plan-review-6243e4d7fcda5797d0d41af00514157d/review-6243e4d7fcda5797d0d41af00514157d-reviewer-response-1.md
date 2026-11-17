<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-6243e4d7fcda5797d0d41af00514157d"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-observation-plan.md"
artifact_commit: "0213ea4d15c36f157390dcd5557c3cd402b7142e"
artifact_blob: "8e0f7b28e339217ece9de4b8aeba6dd5bf692459"
artifact_digest: "sha256:1972d91495d2e241c47da58e61302d478b589c82c01198ec5e76f5066a79b423"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:8fc7ae3d6719f6e60e348c7e1e29c6f1abc1a36bb6a271375be89095a109ecba"
  identity_source: "runtime"
started_at: "2026-11-17T04:30:53.831Z"
submitted_at: "2026-11-17T04:33:35.359Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-16-368-hosted-observation-plan.md` (blob `8e0f7b2`, digest `sha256:1972d914…`) against these sources:

- the accepted local plan `2026-11-16-368-protected-local-observation-plan.md`, which this revision names as the authority for the unchanged assignment, observation and refusal criteria;
- the accepted live-tracing HOLD `2026-11-16-368-live-tracing-findings.md`;
- `story.md` and the hosted-plan SAR;
- #146's `trusted-observation-replan`, `full-suite-observation-findings`, `selected-observation-findings` and the independent `selected-observation-review`.

I also checked that #355's plan pins the same CPython 3.13.9 and pytest 9.2.0 at `8218a69`. That means the recovered #146 patches target the same interpreter and pytest versions, though not the same dependency lock.

The direction is sound and well bounded. Moving to the #146 runner family directly addresses the local stop, where stock DTrace exposed no `proc` provider. #146 recorded working process and user-space DTrace on hosted `macos-26`, and this plan correctly treats that as historical capability that still needs fresh admission. The plan also improves on the local attempt in several ways:

- It turns the local review's open items into requirements: worker network denial must be exercised with a controller-created listener, owner and mode readback is required, and the out-of-scratch write must be refused against a worker-writable sentinel.
- It keeps candidate-code resistance, candidate inventory and impact completeness unqualified.
- It stages the work as admission, then independent packet review, then an integrated run with a re-check for image drift.
- It keeps #355 blocked under the accepted closeout rule.
- It carries the lesson from #146 that artifacts can disappear on rerun.

Three gaps need fixing before this exact revision can govern execution. Each comes from moving to a public, ephemeral, multi-job host:

- Evidence export as written can drop the raw streams that independent reconciliation needs.
- The plan does not say where the instrumented runtime is built or how it is admitted across separate jobs.
- The plan does not bind which tree each checkout uses, or where the report replay runs, now that the branch head differs from the product tree.

None of these changes the experiment question or the scope.

Limits of this review: I did not run Git, query GitHub or compute digests. I did not inspect `16df827e`'s harness sources, the `8218a69` lock or the live GitHub-hosted image. I took the #146 run and result facts from the repository's reviewed findings documents.

## Findings

1. **The evidence export can lose the raw streams that independent reconciliation needs.** The Evidence section keeps "raw streams under the controller during the job", then stages "only an explicitly enumerated synthetic evidence bundle". It scrubs "host paths and any sensitive fields" and retains "enough normalized rows and digests". A GitHub-hosted VM is destroyed when the job ends. Anything not exported is gone, so the local plan's model of retaining raw streams privately under controller control has no hosted equivalent. If the export holds only normalized rows plus in-job digests of raw streams that were never exported, then:
   - (a) the trusted-side reviewer cannot reparse the trace independently and can only replay the controller's own normalization;
   - (b) the raw-stream digests become unverifiable controller claims;
   - (c) scrubbing raw bytes breaks any byte-level digest check.

   This is weaker than the accepted #146 precedent. There, the independent reviewer downloaded all 38 streams, checked "each retained stream's byte count and SHA-256" and "parsed the raw DTrace streams separately from the controller verdict". The local plan also requires recomputing "the final result from the retained records using the admitted reconciler on the trusted side". With only public inputs and synthetic canaries, the raw streams should contain nothing secret beyond runner paths, user names and PIDs. Also, "synthetic evidence bundle" misdescribes the product-run evidence, which is real traced execution of public product tests. Today, the plan's HOLD for an "insufficient" export is the only guard, and it leaves undefined what counts as sufficient.

2. **The plan does not say where the instrumented runtime is built or how it is admitted across jobs.** #146's observer depends on a controller-built CPython 3.13.9 with DTrace and custom line probes, plus a source-patched pytest 9.2.0. #146 built these in-job; its bounded-slice findings record trace-build compiler failures and a captured Mach-O probe table. This plan runs at least two separate fresh VMs: the Stage A admission-only job, then the Stage B job after packet review. The Stage B packet must bind "protected inputs including pytest and interpreter provenance" before the Stage B job exists. If the runtime is built inside the Stage B job, the packet can bind only the source, patch and recipe digests. The resulting binary, its probe table and the installed pytest bytes are first produced after review, so they fall outside the "immutable effective-input … admitted runtime/observer digests" required by local plan §2.2. If instead the runtime is built earlier and carried forward, the plan says nothing about how its custody and digest survive the move between jobs. In either case, the reviewer of the preflight packet cannot know which runtime bytes they are admitting. Stage A's benign probe does not cover this, because it runs before any instrumented build.

3. **Tree binding for the branch head, the trusted tooling and the candidate is ambiguous, and so is where the report replay runs.** The branch starts at `8218a69` and adds paths under `.github/workflows/` and `.github/spikes/368/`. The job's checkout tree is therefore not `90f2cc40`. The plan says to "verify … checkout tree" but not which tree is expected. It also does not require that the head's diff from `8218a69` is exactly the enumerated added paths. The "separate checkout" for the admitted comment does not state its commit. The local plan's "separate trusted tooling and candidate scratch checkouts at that commit" is carried in only by the general deference to the local plan. That matters here, because a candidate built from the branch head would include the `.github` additions. It would then fail as `unsupported-change` against base `8218a69`, or produce a different `snapshot_sha256`. The "Bind the authority" bullet also does not say whether the CLI replays run on the trusted local side as packet inputs or inside a hosted job. Stage B ¶1 then refers to a "fresh report replay" in the packet. Where the replay runs decides which side's report the packet admits and which snapshot Stage B ¶3 re-checks as "frozen and original".

## Required changes

1. Rewrite the first Evidence bullet so the exported bundle includes the raw observer, process-event and controller streams needed for independent reparse, byte-exact, as in #146.
   - If any redaction is needed, do it with a pinned, reviewed, deterministic sanitizer.
   - Record digests of both the raw input and the sanitized output, and state that sanitizing never changes fields the reconciler consumes.
   - Require the trusted-side independent review to reparse the exported raw streams and recompute the verdict with the admitted reconciler before a PASS.
   - Replace "synthetic evidence bundle" with wording that covers real product-run traces derived from public inputs.
   - Define an "insufficient" export as one missing any stream the reconciler or independent reparse needs.
2. State where and when the instrumented CPython and patched pytest are built, and how the packet admits them. Two acceptable forms:
   - (a) A reproducible in-job build: the packet pins the source, patch and recipe digests plus the expected output digests and Mach-O probe-table digest. The Stage B job verifies them before calibration, and any mismatch is a HOLD.
   - (b) A dedicated build: the build runs in Stage A or its own reviewed job. The built bytes are exported with authenticated run, attempt and artifact identity and a SHA-256, preserved locally, and bound in the packet. Stage B imports them only after a controller-side digest and probe-table recheck.

   In either form, record the build log and toolchain identity. A build failure or drift produces HOLD.
3. In "Bind the authority", state the expected trees and replay location:
   - The branch head tree must equal `90f2cc40` plus exactly the enumerated `.github/workflows/…` and `.github/spikes/368/…` paths, checked by an authenticated tree read.
   - The trusted tooling and candidate checkouts must both be at `8218a69`/`90f2cc40`, never at the branch head.
   - Say whether the three CLI replays run on the trusted local side, in-job, or both. Say which report and snapshot the packet binds, and which snapshot Stage B ¶3's "frozen and original" re-check refers to.

## Optional suggestions

1. Stage A ¶3 says USDT is observed "if the proposed observer uses USDT". The plan already names #146's observer, which relies on CPython DTrace (USDT) probes and custom line probes. Make the user-space check unconditional. Also consider requiring the Stage B in-job recheck to list the instrumented interpreter's own provider and probes, for example `dtrace -l -m` against a running instrumented process, before calibration. User-space capability was explicitly left unqualified in the local findings.
2. Stage B ¶2 opens "On the qualification job". Stage A's job is the "admission-only job", so this reads as if Stage B reuses it. Name the Stage B job, for example "the integrated job", and say that calibration, intake controls and the 30-ID run all happen in that one job after it repeats Stage A. Separately, "six hosted mandatory IDs" is ambiguous in a plan about hosted execution. Say "the six `required_tests` in the pinned `tools/ci/policy.json`".
3. Pin least-privilege `permissions:` in the experimental workflow, for example `contents: read`. Also check whether any existing `on: push` workflows will fire on `codex/368-hosted-qualification`. If they do, scope them out or note that their runs are unrelated to this evidence, which keeps "no merge or gate change" visibly true. Say how the "scoped to … the repository maintainer" restriction is enforced, for example by a job-level actor condition.
4. Define "fresh fenced invocations". A reasonable definition: before each subsequent invocation, the controller confirms that no worker-UID process survives from the previous one and that the worker's scratch directory has been reset.

## Decision

revisions-requested
