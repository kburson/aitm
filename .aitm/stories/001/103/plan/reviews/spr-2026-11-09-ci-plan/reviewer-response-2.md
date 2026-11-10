# #103 implementation plan — independent manual Codex SPR, round 2

Submitted UTC `2026-11-10T03:09:30Z`.

**Verdict: changes requested. SPR-CIP02 remains open in part.**

## Review identity and exact coverage

- Declared manual same-provider SPR, continuing the independent Codex reviewer session from round 1. The earlier native design SPR join failed with `APR_CODEX_HOOK_INVALID`. This response supplies no native protocol approval.
- Recorded reviewer context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. I rederived the same provider-qualified fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287` from the exact prefix `ai-peer-review.session/v1\nopenai\n` followed by the active reviewer handle without an added newline. Model and effort are the recorded context.
- Artifact `.aitm/stories/001/103/plan/implementation-plan.md`, source `6bed7897a5cc5f34521b6d560c2631e582be6875`, raw SHA-256 `8088ee6a373308185e0b5e4590a0c59cc57a6a716e4799f39c866d98d7fce555`. The live file and named commit both match. I read fresh contiguous lines 1–20, 21–40, 41–60 and 61–72 to EOF without omissions, then checked the round-one dispositions. No workflow was run.

## Dispositions

1. **SPR-CIP01 resolved.** Lines 50 and 59 name the CI1 aggregate publisher, versioned `candidate.json`, a run/attempt-qualified artifact and the CI2 lookup. They require a matching GitHub association and digest and refuse absent, expired, duplicated, malformed or wrong-attempt evidence. Manual readback uses that same channel and authenticated GitHub metadata remains authoritative for identity.
2. **SPR-CIP02 partially resolved.** Lines 44–45 and 52 now refresh the exact event base in a separate hosted workspace, pin its tree and environment and test inventory omissions and skips. The remaining bootstrap provenance gap is below.
3. **SPR-CIP03 resolved.** Lines 41 and 46 name the installed help invocation and actual normally exiting one-shot fixture, authorize narrowly scoped test instrumentation, and retain invocation, exit, PID and nonempty product data before coverage combine. Deliberately killed service processes remain distinct. Lines 49 and 52 require behavioral refusal against the shipped aggregate predicate, missing capability or child evidence with the other lanes green, and a failing then corrected native demonstration within the forecast.

## Required correction

**SPR-CIP02 · Pin the trusted base evidence collector at bootstrap.** Line 44 pins the base source and, when absent there, an approved bootstrap policy. It does not identify the executable that creates full node IDs and phase outcomes for that base. Line 46 gives that job to a new evidence hook owned by CI1, which does not exist in the protected bootstrap base. The current base lock also does not include any newly added measurement tooling. A base checkout and approved policy alone cannot produce the specified record, while importing the candidate's unreviewed hook into the baseline lets that candidate shape its own comparator. Name the controlled source of the bootstrap collector and any required tooling, bind their exact identities to the baseline, and state that subsequent baseline runs use the delivered collector and trusted target tooling. A minimal route is a separately reviewed, digest-pinned observer that runs the bootstrap base's locked pytest and records full IDs and phase outcomes without importing the candidate. An equivalent independently controlled baseline route also works. Add a refusal for missing or drifted baseline observer identity, and keep the bootstrap preflight and independent source review gates intact.

## Remaining plan assessment

The raw 90% package and helper floors, inclusion of unimported modules, behavioral assertions, qualified serial Darwin tests, isolated wheel smoke, three independently closable leaves and separate ruleset authority remain intact. CI1 stays at four hours and explicitly must reforecast or split before starting if the required evidence no longer fits. CI2 and CI3 remain sequential and Epic #2, C01 and deployment remain outside scope.
