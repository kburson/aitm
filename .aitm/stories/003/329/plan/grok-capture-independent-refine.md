[13:59:21]
REFINE_329: PASS, subject to the binding JIT conditions J1–J14 below. Any Stop trigger returns the story to Refine. The story must not widen.

**Boundary**

- Four owned files:
  - `monitor_registry.py` (blob `350e5da3`)
  - `monitor_scope.py` (blob `a69ff3b2`)
  - `sources/grok.py` (blob `5963de99`)
  - `test_monitor_grok_capture.py` (new)
- `monitor_journal.py` (`e64622a3`) is read-only evidence. #330 exclusively owns `prepare`, ACK, `_stream`, `_source_checkpoint`, the cursor codec and C3 (single admission per prepare).
- #121 keeps coordinator wiring. #137 keeps Linux carrier qualification.
- Prerequisites #115, #117, #304 and #326 are closed. #330 is correctly blocked by #329.

**Amendment conditions**

- **C1 (Linux surface):** Addressed by holding Linux as unsupported. This is only sufficient if the hold is explicit and typed. Today `_eligible`, `_read_grok` and `grok._SURFACE` all hard-code macOS, so this needs J5.
- **C2 (no downgrade of contradicted markers):** Correctly scoped. The current code is the defect:
  - `start_hook` drops a failed or multi-run hook (`self.hook` stays `None`).
  - `verified_boundary` collapses each of these into `None`, which is indistinguishable from hookless:
    - no issuer
    - receipt `None`
    - receipt validation failure
    - hook later than its terminal
  - J6 makes the required tests exact.
- **C4 (post-#326 reproduction):** Pinned at trunk `84b936d1`, tree `4b322edd`, with journal and scope blobs. Ancestry of the #326 merge is asserted but not shown in the supplied data (J1).
- **C6 (graph integrity):**
  - #117 is closed.
  - #119 bears on #330/249 only, not on this leaf.
  - That rank 248 is free and precedes #121 (250) is not demonstrated in the supplied data (J2).
- **C7 (disjoint from #121):** #121's three files are not listed here, so disjointness is unverified (J2).
- **C8 (evidence boundary):** Covered by "typed restart through the actual `read_delta`". The proof must observe a non-`None` `GrokCheckpoint` argument (J12).

**Design findings that the JIT must resolve**

1. **Registry types are exactly Codex/Claude-typed.** `CaptureFrontier.checkpoint: SourceCheckpoint`, `CaptureReadBound.cursor`, `_CaptureArm.position` and `CaptureProgress.cursor` cannot carry Grok state. `RegistryView.format` is strict equality, so a format bump is a migration and therefore a Stop.
   - The bounded design is a separate, additive, ordinal-only Grok epoch record.
   - It should hold no `GrokCheckpoint` in the registry, because the checkpoint carries up to `_MAX_TURNS` of history and would create registry growth and storage risk.
   - The checkpoint persists with the journal cursor, which #330 owns.
2. **Restart has two halves.**
   - M11c owns epoch reload, plus pass-through of a caller-supplied prior `StreamCursor`. This means scope stops nulling `native_cursor` for Grok.
   - #330 owns persistence of the cursor itself.
   - If scope needs its own Grok cursor store, that is a Stop.
3. **Grok ordinals are byte offsets within one incarnation.** `span_disposition` is keyed only on `stream_ref`. A file replacement restarts the offsets, so epochs must bind the incarnation.
   - The span of a completion must run from its `user_prompt_submit` offset to its terminal offset + 1, not be a terminal-only point. Otherwise a turn that started before enable or disable is wrongly eligible.
4. **Routing defect.** `resolve_route` takes `_timeline(...).scope` through the ordinal. A prior marked scope therefore attaches its story to a later hookless turn.
   - The fix must be a type-selected Grok branch.
   - Codex/Claude decisions must stay byte-identical.
5. **Held vs excluded is inconsistent.** The story's tests say revoked and foreign profiles are "held", but the amendment's M18/M19 outcome is "closed exclusion of unauthorized profiles". The JIT must assign exactly one typed disposition per case (J9).
6. **Late receipts.** A completion with an attempted but unverified hook must surface as a typed held result, never as a remembered hookless completion. Otherwise a later-verifiable marker can never be re-evaluated.
7. **C3 seam.** `_read_grok` performs admission internally. If #330 needs to edit `monitor_scope.py` to bind one admission proof, the M11d file set (C5) breaks. M11c should provide that seam.

**Risks that can exceed this leaf (each is a Stop → Refine)**

- A `NativeSurface` Linux member, or any edit to the enum's module.
- The GrokCheckpoint/GrokCompletion codec living outside `grok.py`, or needing a version change, in order to persist the attempt classification.
- The #117 receipt / original-owner lookup living outside `monitor_scope.py`.
- A registry format bump, or any change to the non-Grok encoding or digest.
- Any new fixture file.
- A scope-side cursor store.
- Any edit to the journal or to #121's files.

**Estimate**

- 3.5h is attainable only with the minimized ordinal-only epoch and reuse of `span_disposition`.
- A parallel cursor-typed capture machinery would realistically take 4.5–5.5h, which exceeds the 4h cap.
- Keep 3.5 / 1.75 / 4.0 as provisional and bind them under J14.

**Binding JIT conditions**

- **J1 – Re-pin the trunk.**
  - Prove the #326 merge is an ancestor of the JIT base.
  - Re-pin the four blobs.
  - On any drift from `84b936d1`, rerun the controlled reproduction and record the new trunk and blobs.
- **J2 – Graph checks.**
  - Confirm rank 248 is free and precedes 249/250.
  - List #121's three product files by path and show none of the four files here.
- **J3 – Registry codec.**
  - Pin the literal registry codec.
  - Add the Grok epoch as an additive, defaulted field that is omitted when empty.
  - Prove a registry without Grok epochs:
    - round-trips byte-identically
    - keeps the same digests, receipts and `_PendingCapture.digest`
    - decodes from existing on-disk fixtures
  - Do not change `_REGISTRY_FORMAT`.
- **J4 – Grok epoch record.** It binds:
  - project and source
  - approved tuple and surface
  - trusted checkout ref
  - session and stream ref
  - incarnation ref
  - qualified #304 profile ref
  - generation and enabled flag
  - start ordinal and start boundary ref
  - an optional terminal ordinal and terminal boundary ref

  The only write path is a writer-leased, guarded publication from a current admission plus a positively verified boundary returned by the adapter in the same read. Approval alone, a caller-supplied ordinal, observation presence or anchor presence never creates or extends an epoch.
- **J5 – Surface.**
  - Scope derives the surface from the approved tuple.
  - The authority path holds every non-macOS Grok tuple with a typed unsupported diagnostic, and has a test for it.
  - The legacy observational path stays unchanged and has no authority.
- **J6 – Typed adapter evidence.** Exactly three types: verified-marked, verified-hookless and attempted-unverified (held). Each of the following is held and never hookless, with a test for each:
  - a failed hook
  - a multi-run hook
  - a hook later than its terminal
  - no issuer
  - a receipt of `None`
  - an invalid receipt
  - a mismatched receipt
  - a duplicate or conflicting receipt
  - an existing history entry whose receipt state differs
- **J7 – Spans.**
  - The Grok span runs from prompt-start to terminal + 1, evaluated via `span_disposition` on incarnation-bound epochs.
  - A span that straddles an enable or disable boundary returns `UNKNOWN` and is held.
  - Incarnation replacement or a mutated prefix is refused before any new proof.
- **J8 – Routing.**
  - A marked turn routes only when the verified receipt matches the #117 transaction, project, original owner and story.
  - A hookless turn routes project-only (`explicit=None`) only when the anchor project equals the epoch project and the checkout matches.
  - The live witness, root and cursor are revalidated after the read.
  - Pre-admission (no epoch) yields zero ROUTED decisions, with a test for it.
- **J9 – Ordered transitions.** Pin one disposition and one ordering each for:
  - disable, fenced at a verified terminal boundary
  - profile revocation, which fails closed for anything not proven before the fence and never reroutes earlier results
  - a foreign or never-authorized profile, which gets closed exclusion consistent with M19
  - ambiguous supersession, which is held

  Restart reload must reproduce identical decisions.
- **J10 – C3 seam for #330.** `_read_grok` accepts an optional pre-obtained admission proof and revalidates it, keeping `_LiveSourceUnavailable` intact, so #330 needs no scope edit.
- **J11 – Fixtures.** Use only retained native bytes and the existing #304 isolated issuer, already in the tree (pin path and blob) or embedded in the test file. No new fixture file and no paid turn.
- **J12 – Restart proof.** The test asserts that `read_delta` receives the prior `GrokCheckpoint` (not `None`), resumes at its offset and re-emits nothing. A forged or mismatched prior is refused.
- **J13 – Acceptance replay.**
  - Replay the retained post-#326 probe bytes through scope and show the expected marked and hookless route decisions.
  - Journal `prepare` must still return the same held reason, unchanged. This proves the journal was untouched.
  - Run the existing Grok, registry and scope regressions.
- **J14 – Estimate checkpoint.**
  - Re-estimate after pinning the codec. If it exceeds 4.0h, Stop → Refine split.
  - At 1.75h, J3 and J4 must be green. Otherwise Stop.

The existing gates are unchanged: qualified release, locked local Test, signed exact hosted Test, independent source review, verified protected delivery and native Close. There is no production issuer, release activation, allowlist write, Epic #2, C01, cutover or Claude #204.
