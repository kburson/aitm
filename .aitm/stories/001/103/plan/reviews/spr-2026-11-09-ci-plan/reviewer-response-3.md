# #103 implementation plan — independent manual Codex SPR, round 3

Submitted UTC `2026-11-10T03:10:48Z`.

**Verdict: accepted. No required findings remain.**

## Review identity and coverage

- Declared independent manual same-provider SPR, continuing the distinct Codex reviewer session from rounds 1 and 2. The earlier native design SPR join failed with `APR_CODEX_HOOK_INVALID`. This response supplies a manual decision without native protocol approval.
- Recorded reviewer context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. I rederived fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287` from the exact UTF-8 prefix `ai-peer-review.session/v1\nopenai\n` followed by this reviewer session's handle without an added newline. Model and effort are the recorded reviewer context.
- Artifact `.aitm/stories/001/103/plan/implementation-plan.md`, source `deb5055ac11f5f7abb1fb7f3f61e24ef80590a76`, raw SHA-256 `cda1e4d3141621f0d28c05887f7b94e15d85003e3de0524dc0304a7c6b007cf2`. Both file and named source match. I read fresh contiguous lines 1–20, 21–40, 41–60 and 61–72 to EOF without omissions and verified the prior manual findings against the exact current text. This is plan evidence.

## Finding dispositions

1. **SPR-CIP01 remains resolved.** Lines 50 and 59 pin the CI1 aggregate producer, versioned single-file evidence artifact, CI1 manual readback and CI2 lookup to the selected canonical workflow, run and attempt. Metadata and digest validation reject missing, expired, duplicate, malformed and wrong-attempt records. Authenticated GitHub metadata remains the authority for identities.
2. **SPR-CIP02 resolved.** Lines 44–45 now name a separately reviewed standalone bootstrap observer and policy, with independently recorded exact blob IDs and SHA-256 before use. The observer is materialized outside both checkouts, verified before execution, and uses only the exact base tree, its locked pytest and standard library. Candidate imports and checkout access are excluded. Later baselines use the delivered observer and policy from the exact trusted target tree. Records bind the base, observer, runner, runtime, lock, configuration and policy. Missing, drifted and unapproved observer identities fail closed. Base movement refreshes the exact evidence, and any future reuse needs matching inputs and review.
3. **SPR-CIP03 remains resolved.** Lines 41, 46 and 49 name the console help and normally exiting one-shot witnesses, bind each to the actual child and raw product coverage shard before combining, distinguish forced termination, and exercise refusal against the shipped aggregate predicate. Line 52 retains native failure/correction proof, independent source review and the estimate stop rule.

## Remaining scope and sizing

Lines 15–18 and 45–48 preserve the unrounded 90% line floor separately for the product and executable helper scopes, including unimported production code, exact boundary tests, and meaningful behavioral and recovery assertions. Hosted Darwin capability and coverage remain real gates. Lines 25–29, 52, 60, 68 and 72 preserve three independently closable leaves at 4.0, 3.5 and 2.5 agent-hours and the later parent comparison. Replan or split if the proofs no longer fit. CI ruleset enforcement, Epic #2, C01 and deployment remain outside the plan. No implementation or workflow run was performed.
