# #103 manual independent Codex design SPR — round 4

Submitted UTC `2026-11-10T02:53:12Z`.

**Verdict: accepted. No required findings remain.**

## Review identity and coverage

- This is the declared independent same-provider manual SPR, continuing rounds 1–3 in the same distinct reviewer session. The separate native reviewer attempt failed with `APR_CODEX_HOOK_INVALID`. This manual verdict supplies no native protocol approval.
- Reviewer context is Codex Desktop, `openai`, `gpt-6.1-sol`, high effort. I rederived the provider-qualified fingerprint `sha256:a3bb437a4264b6ad468ee66ea2fa72d26913b9712e2db7f6ecbf105ed0bbd287` from the exact UTF-8 prefix `ai-peer-review.session/v1\nopenai\n` followed by the active reviewer session handle without an added newline. Model and effort are the recorded reviewer context and lack a fresh native join attestation.
- Artifact `.aitm/stories/001/103/design/github-ci-quality-gates-design.md`. Source `144133b12dfb0fe62644c8359550c92abd4333c2`. Raw SHA-256 `d48fc2bd0b1973c48a39b4b197a9ab7e97d77db7bdd34980e58022037d4c1ed0` matches the file and the source commit. I read contiguous lines 1–20, 21–40 and 41–54 to EOF without omissions and checked prior manual finding dispositions. No source implementation or hosted CI was exercised in this review.

## Finding dispositions

1. **SPR-CI01 remains resolved.** Lines 15–21 require canonical workflow and attempt binding to authenticated GitHub metadata and exact live base/head. Candidate evidence supplies lane outputs only. The protected read-only verifier rejects incomplete or ambiguous attempts and requires each expected job in the selected attempt. Gate-defining blob comparisons and explicit owner disposition prevent a candidate from using its own weakened controls to certify itself. Lines 50–51 retain relevant negative evidence, and later ruleset enforcement stays separate under line 27.
2. **SPR-CI02 remains resolved.** Lines 19 and 23 bind live target and head to the event and the two ordered parents of the raw tested commit. They require fresh evidence after drift, with a branch update and `synchronize` or an authorized `reopened` event where no update is needed. Lines 27 and 50 verify the trunk route and a representative integration target. Old reruns retain their event identity and trunk push evidence remains scoped to that tree.
3. **SPR-CI03 remains resolved.** Lines 27 and 44 retain the initial Before Develop route exception only, require a qualified hosted Darwin runner and close the gate on required capability gaps, required missing cases or unexpected skips. Optional capability skips are declared as such. Lines 49–50 do not let a below-floor prerequisite, missing Darwin proof or a policy disposition create passing CI.
4. **SPR-CI04 resolved.** Line 21 applies the approved manual readback and control diff until the verifier's separate delivery. Line 49 makes a below-floor behavior prerequisite conditional on its own explicitly reviewed route and stops if that route is unavailable. Line 50 closes the workflow bootstrap on its own real PR run, 90% product coverage, independent review, exact trunk delivery and readback, integration-target proof and sign-off. Line 51 then uses the proven route to deliver and independently close the verifier with its own behavioral tests and helper floor. Line 52 separately closes file quality and the future TypeScript contract. Line 54 assigns exact candidate manual/verifier comparison to the parent after delivery, so neither leaf depends on a verifier it has not delivered.

## Scope and sizing

Lines 33 and 40–45 preserve locked wheel smoke without editable imports, the unrounded 90% line floor per active product package, observed expected subprocess coverage, the trusted base inventory, and full serial Darwin validation before measured parallelization. One hundred percent remains aspirational for meaningful behavioral tests. Lines 7–11 and 34–38 keep this to general source CI and the deferred TypeScript contract. Core, operational qualification, release publishing and unrelated cleanup stay outside scope. Lines 49–54 preserve the four-agent-hour leaf cap and require refinement or a further split before a larger leaf is admitted.
