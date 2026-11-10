# #103 implementation plan — independent manual Codex SPR, round 4

Submitted UTC `2026-11-10T03:18:08Z`.

**Verdict: changes requested. One required fixture-list correction remains.**

## Review identity and exact coverage

- Declared independent same-provider manual SPR, continuing the distinct Codex reviewer session from rounds 1–3. The earlier native design SPR join failed with `APR_CODEX_HOOK_INVALID`. This response supplies no native protocol approval.
- Recorded reviewer context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. I recomputed fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287` from the exact UTF-8 prefix `ai-peer-review.session/v1\nopenai\n` followed by the active reviewer session handle without an added newline. Model and effort are the recorded reviewer context.
- Artifact `.aitm/stories/001/103/plan/implementation-plan.md`, source `463f995fc21c8b78fe21235ee983b66e0fb9580d`, raw SHA-256 `5b8e28aa3b12e315778086352241f8817a03d2b855f11b889e92bba9779207e5`. File and named source match. I read fresh contiguous lines 1–20, 21–40, 41–60 and 61–77 to EOF without omissions. I compared the prior manual findings and native round-one response.

## Finding dispositions

1. **SPR-CIP01 remains resolved.** Lines 52 and 64 identify the versioned aggregate artifact, exact run and attempt, authenticated association and digest, required data, closed refusal cases, and common manual and automated readback. The candidate provides lane evidence while native metadata remains authoritative for identity.
2. **SPR-CIP02 remains resolved.** Lines 46–47 pin the same independently reviewed observer blob in bootstrap and delivery, with a base mode using only the standard library and locked base pytest. It cannot import the candidate. It verifies exact blob and SHA before use, switches to the delivered trusted target observer after bootstrap, and refreshes the exact base while refusing stale or unapproved evidence.
3. **SPR-CIP03 remains resolved.** Lines 41 and 47–51 identify both normally exiting subprocesses and their actual raw coverage shards, preserve separate hard-kill proof, and add required pytest phase and exit failures. The workflow passes its actual dependency results to the single tested aggregate predicate. Missing, failed, skipped and cancelled required jobs and missing host or child evidence fail against that predicate.

## Required correction

**SPR-CIP04 · Finish the trusted verifier refusal matrix.** CI2 lines 63–64 still do not require fixtures for a missing required job, a skipped required job, a live PR head that moved without a new matching event, and reported head, base or tested-commit identity that conflicts with authenticated GitHub metadata. Native round-one Finding 6 requested those cases explicitly. Line 64 states the required identity comparison, but the round-two candidate still has no fixture obligation for it. CI1 aggregate fixtures do not exercise CI2's separate protected verifier. Add these independent CI2 fixtures with otherwise green evidence, requiring a nonzero or explicit blocked result. Preserve the existing stale-base, partial-rerun, artifact and wrong-workflow cases.

## Other checks

- Lines 43–44 place the authorized minimal binding probe before helper or wheel work and stop if provider metadata cannot independently identify the tested merge. Lines 54–55 confine mutable integration proof to two named disposable refs with explicit prior authority, record movement evidence and let CI1 close on its own sign-off before CI2. Line 65 gives CI2 a current live proof after its own protected delivery, with separate retarget and cleanup authority and no dependency on CI3. Line 77 retains the parent comparison on CI3.
- Line 57 allocates 3.25 active hours plus 0.75 reserve within the four-hour cap. The individual allocations sum to 3.25 and the post-probe stop is explicit. Line 18 budgets both hosted macOS lanes and separates runner time from active work and billing. Lines 25–29 retain 4.0, 3.5 and 2.5 hours and independently closable leaves.
- Lines 15–16 and 47–50 preserve meaningful behavioral tests, the unrounded 90% product and separately defined helper floors, unimported source, separate branch reporting, qualified serial Darwin execution and locked wheel smoke. No work on Epic #2, C01, deployment or external ruleset enforcement is admitted.
