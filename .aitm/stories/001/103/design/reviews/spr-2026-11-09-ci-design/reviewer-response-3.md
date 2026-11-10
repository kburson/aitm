# #103 manual independent Codex design SPR — round 3

Submitted UTC `2026-11-10T02:51:11Z`.

**Verdict: changes requested. One new required finding.**

## Review identity and coverage

- This is a declared independent same-provider manual SPR, continuing the distinct Codex reviewer session from rounds 1 and 2. The separate native reviewer attempt failed with `APR_CODEX_HOOK_INVALID`. This is a manual verdict with no native protocol approval.
- Reviewer context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. I recomputed the provider-qualified fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287` from the same active reviewer session using the exact prefix `ai-peer-review.session/v1\nopenai\n` and the active session handle without an added newline. Model and effort are the recorded context, with no fresh native join attestation.
- Artifact `.aitm/stories/001/103/design/github-ci-quality-gates-design.md`, source `dc507c8017ed6fb01cb39c561cec77a6959fb206`, raw SHA-256 `96ef0fb0019e82c3ed43387c6e9efedc83bfeeae6a9094ac4de42980009d120b`. Both the file and the named source match the digest. I read fresh contiguous lines 1–20, 21–40 and 41–52 to EOF with no omissions. I read the previous manual dispositions and the native round-one findings as context. This is design evidence only.

## Prior findings

1. **SPR-CI01 remains resolved.** Lines 17–21 and 49–50 retain the exact workflow/run/attempt binding and add a protected read-only verifier, a deterministic newest-run choice and explicit all-jobs-in-attempt checks. The gate-defining diff and exact blob inventory protect against the candidate approving a weakening through its own output. External check-source enforcement remains separate.
2. **SPR-CI02 remains resolved.** Lines 19, 21 and 23 bind the decision to the live PR target and head both before review and before merge. Exact raw test-merge parents, `synchronize` after an allowed branch update and authorized `reopened` where no head change is needed preserve a practical fresh route without triggering on title or description edits. Lines 15, 27 and 49 require canonical evidence for declared source targets, including the first representative integration target. Old-event reruns and trunk push checks remain separate. [GitHub PR events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request) · [GitHub reruns](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
3. **SPR-CI03 remains resolved.** Lines 27, 44 and 50 preserve the narrow Before Develop preflight exception and require actual hosted execution before merge. Essential Darwin capabilities and missing named required cases fail closed. Optional capability skips are explicitly scoped. A policy disposition does not supply passing CI.

## Required change

**SPR-CI04 · Order the standalone bootstrap and verifier leaves.** Lines 21, 27, 49 and 52 require manual bootstrap, separate verifier delivery, real CI for source delivery and verifier agreement as first-delivery evidence. They leave unclear which source leaf can independently close first. A verifier-first reading would require CI on a target with no proven route. A bootstrap-first reading can strand its closure if the verifier agreement is interpreted as a prerequisite for the bootstrap leaf, since no trusted target revision contains the verifier yet. State the dependency and closure split explicitly. The first workflow leaf can use the approved manual identity and control-diff procedure for its own real CI and review, followed by merge and trunk readback. The separate verifier leaf then uses that established CI route with its 90% helper floor. Prove manual and trusted verifier agreement as the parent’s subsequent live acceptance, on a named exact candidate where both checks can run. Keep the bootstrap exception confined to Before Develop. Preserve each leaf’s own closure point and leave any coverage prerequisite to its separately planned route if the initial product floor is unmet.

## Other design checks

- Lines 33–45 and 51 preserve the owner’s unrounded 90% per product package and add a separate 90% helper floor, locked-dependency wheel smoke and digest check, expected subprocess evidence, trusted base inventory and explicit refusal for missing required tests. The 89.5% regression checks the exact arithmetic. Hard-kill coverage and optional host capabilities remain transparent. Cold/warm timing, complete serial baseline and whole-suite shard parity remain measurable.
- Lines 7–11, 25–27 and 34–38 keep the design scoped to general source CI. No Core pickup, platform port, release publication or production operation follows. The TypeScript lane activates with a real package, and existing lint issues and deliberate malformed fixtures have explicit reviewed scope.
