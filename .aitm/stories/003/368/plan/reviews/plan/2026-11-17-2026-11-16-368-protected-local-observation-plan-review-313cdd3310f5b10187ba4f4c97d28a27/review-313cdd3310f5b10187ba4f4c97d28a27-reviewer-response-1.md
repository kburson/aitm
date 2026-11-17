<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-313cdd3310f5b10187ba4f4c97d28a27"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-protected-local-observation-plan.md"
artifact_commit: "b70e8211591ba243f858a56e1e57f1f38c67555b"
artifact_blob: "7ac282bcd78705458093f3193a7070d4bd2ffc6b"
artifact_digest: "sha256:4ed0f816af1dc9635f4b347a917d44561c949e0425f71f154b6245699b88d6db"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:cd7588a405e04feb723306cd5b5d92d8af1cd6b4f9b6efd6e5e3710a751b8810"
  identity_source: "runtime"
started_at: "2026-11-17T01:06:47.486Z"
submitted_at: "2026-11-17T01:08:38.075Z"
finding_ids: ["R1-F001"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is an independent review of `.aitm/stories/003/368/plan/2026-11-16-368-protected-local-observation-plan.md` at blob `7ac282bc…`, commit `b70e8211`. The artifact digest is `sha256:4ed0f816…d6db`, which matches the digest in the "Revised plan SAR" section of `plan/reviews/2026-11-16-368-plan-sar.md`. I reviewed the whole plan, lines 1–44.

**What I read.** I read story #368, the plan SAR including its revised section, and the preserved first-attempt reviewer response `review-24bc176292f32fd762ed6ca8a23758dd-reviewer-response-1.md`, which holds findings F001–F003 and three optional suggestions. I also read story #355 and its execution qualification, the #353 finding and the #146 full-suite observation findings. I grep-verified the pins against the #354 verified delivery, the #354 CLI probe attachments, the #355 machine receipt and the #344 TIA receipt. I opened product tests read-only in the local trunk checkout `/Users/kpburson/projects/aitm-workspace/trunk`. That checkout may predate `8218a69`, and the plan already requires reconfirmation at the exact base. This review ran only the join command and will run only the submit command. It used no Git and executed nothing else.

**Pins verified.** Commit `8218a69…` and tree `90f2cc40…` appear in the #354 verified delivery (lines 7, 8, 19). Source SHA-256 `d71cd585…101647` appears in the #354 CLI and report probes, the #355 receipt and the #355 plan. Inventory digest `812bc918…` appears in the #344 receipt. The local tests confirm that the fixture `isolated_grok_capture` is imported from `test_monitor_grok_capture` and shared across modules. Line 44's time box is internally consistent. The phases sum to 6.0 h, and the 2.5 h and 3.75 h checkpoints equal the cumulative allocations for the earlier phases (0.75 + 1.75; + 1.25).

**Prior findings: resolution check.**

- *First-attempt F001 (trust scope): resolved in the plan body.* Line 11 now declares the trust scope: protected custody, exact assignment, independently observed process facts, and outcomes for the exact reviewed, admitted closure. It requires `candidate_code_resistance=unqualified` in the results and receipt. Line 40 carries that field into the receipt contract. Line 42 limits #355's inheritance to the exact closure and configuration. One residual gap sits in the board and dependency mechanics of line 42. See R1-F001 below.
- *First-attempt F002 (incidental native children): resolved.* Line 29 adds incidental children as a classified category. Each entry records the owning test or fixture, phase, multiplicity or bounded rule, pinned path and SHA-256, argv shape, attributed create/exec/exit and wait status. These entries create no pytest obligations, and an unclassified launch prevents PASS. Line 30 adds the guest system executables that the closure invokes to the manifest. Line 22 limits deep observation to required children, following #146 findings line 15. Line 24 adds an incidental child to calibration. Line 36's "unassigned native child" control now has a well-defined complement.
- *First-attempt F003 (privileges and early probe): resolved.* Line 5 requires an explicit decision on a guest root-owned controller, on guest SIP and diagnostic tracing restrictions, and on any entitlement. An unapproved protection change produces HOLD. Line 16 adds a fresh-worker create/exec/exit probe, plus a USDT receipt where the observer depends on it, before the instrumented interpreter is built. The probe stops the run on failure, on dropped events or on unavailable tooling.
- *Optional suggestions:* all three were adopted. The pre-launch approvals are merged into one independent preflight packet review (line 30). Line 44 adds time-box checkpoints. Line 40 requires a trusted-side recomputation of the verdict from the retained records.

**What holds.** The plan asks one question and runs three gates that fail closed. Each gate maps to a #355 HOLD row. The trust scope is now explicit and honest about the #146 disclaimer. The native-child taxonomy covers what the real fixture closure does. The foreseeable privilege blocker is surfaced and probed before the expensive build. The live and offline controls are labelled separately and cover the #353 refusal classes. The plan states that the current pickup starts no experiment.

**What does not.** Line 42 tells the executor to "clear this dependency" after PASS and also to "keep #355 blocked" on unqualified trust properties. It names no mechanism that keeps #355 blocked once #368 is removed. #368 is the only open entry in #355's `blocked-by`, so following the plan literally leaves #355 natively unblocked while candidate-code resistance remains unqualified (R1-F001).

## Findings

### R1-F001 — After a PASS, clearing the #368 dependency leaves nothing that keeps #355 blocked on the properties this spike leaves unqualified

**Where.** Plan line 42: "#355 can inherit qualification only for the exact reviewed closure and configuration. Clear this dependency after the independently accepted spike PASS. Keep #355 blocked on any unqualified trust property in its accepted scope, including strict outcome authority for unreviewed candidate code, until separately qualified or explicitly rescoped."

**Evidence.** `.aitm/stories/003/355/story.md` line 11 has `blocked-by: [353, 354, 368]`. #353 is accepted and #354 is delivered (story line 39), so #368 is the only open blocker. Story line 49 says "Stay blocked until [#368] passes independent review of the integrated live qualification." Story line 29 defines #355's scope as running affected tests "for the current uncommitted working tree", which means arbitrary, unreviewed candidate code. #355 execution qualification line 27 records the owner decision to "keep trusted execution as the outcome". Plan line 11 fixes `candidate_code_resistance=unqualified` for any #368 PASS. #146 findings line 22 disclaims that property for the preferred observer. The recent commits `c0b83ede` and `7f160a9c` show that the board's Blocked-By projection is generated from these native declarations.

**Problem.** Line 42 now reads correctly as prose, but the two instructions in it conflict in effect. Clearing #368 from `blocked-by` is the only blocking action the plan specifies. The plan names no native successor blocker and no recorded owner rescope that would carry "keep #355 blocked" forward. #355's own story text promises unblocking on a #368 PASS. A PASS can only qualify the comment-only reviewed closure, which is a strict subset of #355's working-tree scope. So, read literally, the board shows #355 ready exactly when its accepted trust requirement is still unmet. This is the failure mode that first-attempt F001 targeted. It now reaches #355 through dependency tracking rather than through report wording.

**Failure scenario.** #368 records an accepted PASS. The executor follows line 42 and removes #368 from #355's `blocked-by`, and the board sync shows #355 unblocked. A later #355 pickup reads its story line 49 ("Stay blocked until #368 passes…"), sees it satisfied, and resumes trusted pre-commit execution on arbitrary working-tree changes. The receipt's `candidate_code_resistance=unqualified` field is present, but nothing on the dependency path consults it.

**Required change.** In line 42, make the PASS closeout record the replacement constraint before or atomically with clearing #368 from #355's `blocked-by`. For each unqualified trust property in #355's accepted scope, including `candidate_code_resistance`, record one of the following:

1. an explicit owner rescope decision for #355, for example to reviewed-closure or advisory scope, citing the #355 owner decision options; or
2. a native successor blocker, a new or existing story, added to #355's `blocked-by`.

Also require #355's story text (currently line 49) to be updated in the same step so that it no longer promises unblocking on a #368 PASS alone. If neither a rescope nor a successor blocker is recorded, #368 stays in #355's `blocked-by` even after the spike PASS.

## Required changes

1. **R1-F001.** In line 42, make clearing #368 from #355's `blocked-by` conditional on recording, in the same step, an owner rescope or a native successor blocker for each unqualified trust property in #355's scope. Update #355's "Stay blocked until #368 passes" text at the same time. Otherwise retain the #368 dependency.

## Optional suggestions

1. **Order of steps in §1.1.** Line 16 places the early capability probe "after the isolation readback" and requires it to run "under the actual worker identity". The worker identity and its isolation preflight are only defined later, in §1.2 and §1.3. Consider saying explicitly that the probe runs after §1.2 and §1.3 and before the §2 runtime build, or move the probe sentence to the end of §1. As written, an executor following the numbered order could look for a worker identity that does not exist yet.
2. **Headline the scope in the report.** Consider requiring the qualification report's opening verdict line, and not only the receipt fields, to state "PASS for the exact reviewed closure; candidate-code resistance unqualified". A reader who only skims the verdict, as #355's story line 49 invites, would then see the limit.

## Decision

revisions-requested
