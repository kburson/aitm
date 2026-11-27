# #494 accepted pickup review

Grok 4.7 Build Fast returned PASS.

PASS

The single-document C107 scope matches the accepted replan. `#494` only authors `docs/architecture/legacy-sdlc/guard-facts.md` on `codex/core-471-integration` at `8aa608cc1e64ed5986c5b6a8371df5a4c5b3f3e6`, against legacy commit `c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905` and tree `844ae26bb169e8618e45fc3b1aedb57f44896fe0`.

The pinned list is 51 entry/exit registrations and 36 distinct guard exports across the eight states. Entry guards are 11 and exit guards are 40. `contiguityEntryGuard` (7), `blockedByGuard` (5), and `childCannotLeadEpicExitGuard` (5) are the repeated registrations; `refineExitWipBudgetGuard` is on both ready-for-plan and plan. Done is entry-only: `bodyGatesEntryGuardDone`. The three resident actions stay linked to C108/`#495` and are outside the 51 and the 36.

Exception, evidence, and owner fences hold. Discussion, Refine parent eligibility, Ready for Plan ancestry, child-ahead, WIP, ownership, and blockers stay separate families, with registration order distinguished from execution, caller/phase, broader activation, fail-open, and refusal. Guard facts use pinned source and test line anchors; the 105 green representative cases, other-family citations, and explicit gaps are the evidence set. Typed obligations stay distinct from configurable choices. C107 recommends only. C109 keeps authority, bypass, and outside-state modules. C108 keeps resident retry, waiting, recovery, historic schemas, and closeout evidence. C110/`#497` is the only child that integrates authorized dispositions and proof vectors. Draft exit still requires installed Core plus repository validation and green hosted repository and Core CI before Grok 4.7 source SAR; integration merge waits on the exact reviewed candidate, verifier, and closeout, then `#494` moves to Done.
