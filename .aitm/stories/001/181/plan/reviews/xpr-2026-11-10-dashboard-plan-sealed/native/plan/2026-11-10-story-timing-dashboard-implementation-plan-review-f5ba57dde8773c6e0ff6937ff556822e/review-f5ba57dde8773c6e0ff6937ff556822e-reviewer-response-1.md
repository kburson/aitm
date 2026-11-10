<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-f5ba57dde8773c6e0ff6937ff556822e"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
artifact_commit: "3c4815fb6e42a5372f9f99fad5453c4a535e0169"
artifact_blob: "7c7d4c65971b8424b6feb2189fb885d2b35c530a"
artifact_digest: "sha256:e8e051336de6976db1a3cc87f42610cc6614d0946df9ac76d06773b4151e7b93"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:ff8a11f512bd9ed26aac55367574791ae964359ddeb6d2365a98f8fe2916149f"
  identity_source: "runtime"
started_at: "2026-11-10T20:58:00.039Z"
submitted_at: "2026-11-10T20:59:47.259Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed the plan at commit `3c4815f` against the accepted #181 design (`ed54c65d…f46a5`), the #181 `events.jsonl` and the registered v0 seed `attachments/2026-11-10-actual-backfill.json`. The plan is well structured. The leaf order and dependencies are acyclic and match the design's slice gates. The arithmetic checks out: A totals 19.5 h, B totals 6.0 h, together 25.5 h, and 774,000 ms equals #111's recorded 12m 54s. The plan covers most of the design's A/B acceptance items. Typed interfaces separate the leaves cleanly, and the plan keeps the Slice C boundary and the #2/#100 ownership explicit.

Two problems block the plan as written, and a third puts the headline parity assertion at risk. First, A01's admission rules, as worded, reject the one legacy seed that A02, A03 and A05 rely on. Second, A04's Cost admission depends on an operator verification receipt that no leaf owns. Third, the parity assertions on the seed don't account for A02's new overlap-hold rule or for differences in the ancestry graph. The remaining items are smaller test-coverage and clarity gaps.

## Findings

1. **A01 cannot admit the registered v0 seed under its own rules (blocking).** A01 accepts only the explicit kinds `story-timing-receipt` and `story-usage-receipt`, and only regular-file blobs "at registered paths under the subject's `attachments/timing/`". The plan's registration shape (line 47) uses `data.path`, `data.sha256` and `data.scope.story`. The actual seed registration (`.aitm/stories/001/181/events.jsonl` line 3) differs in every respect:
   - It uses `data.kind: "historical-actual-backfill"`.
   - It has a `data.evidence` array of three paths (`.md`, `.json` and the coordination `.md`).
   - It has a single `receipt_sha256` and no `scope`.
   - The file lives at `attachments/2026-11-10-actual-backfill.json`, not under `attachments/timing/`.
   
   The design names this as "the sole multi-story legacy exception". A02 says the "registered #181 v0 seed" contributes and that "unregistered or digest-mismatched copies add nothing". A03 and A05 assert parity against it. As written, A01's reader drops the seed as an invalid or unregistered input, so every seed-dependent assertion downstream fails or is vacuous. The plan doesn't say which leaf owns the exception path, and A01 owns `evidence.py`, so A02 cannot add it without crossing file ownership.

2. **No leaf owns the operator verification receipt that gates Cost (blocking).** A04 binds Cost admission to "a registered, sanitized operator verification receipt" that names the export or report identity, source digest, checked scope and selector, rate basis and coverage. That is a third evidence type alongside the timing and usage receipts. A01 pins only `aitm.story-timing-receipt/v1` and `aitm.story-usage-receipt/v1`, two `core.evidence.recorded` kinds, and the capture guide and fixtures for those two. The plan leaves several questions open:
   - What are the schema, the evidence kind and the storage path?
   - Is it a separate registered file or fields inside the usage receipt or its registration?
   - Does it live under the story's `attachments/timing/`, and which story owns it when one report covers many stories?
   - Who documents it in `capture.md`?
   
   A04 depends only on A01 and owns only `usage.py`, so as written it would have to change A01's validator and guide. A06 then relies on "A04's verified report binding" for the board write.

3. **The seed parity assertions may conflict with A02's overlap-hold rule and with the pinned ancestry graph (high risk).** Two mechanisms can make the recomputed values diverge from the seed:
   - **Overlap holds.** A05 requires exact parity for "all ten Actual values with the existing receipt", and A03 requires "exact direct plus descendant totals from the v0 seed". A02 holds any span where the same actor is concurrently attributed to different stories, including across distinct observation keys. The seed reuses actor pseudonyms such as `A001` across epic-direct and child intervals. Its own coverage notes say coordinator intervals were "shared with #116" or "interleaved", and some were left unassigned. If any registered seed interval overlaps the same actor's interval in another story, A02 holds it and the recomputed Actual drops below the readback.
   - **Ancestry graph.** The seed's inclusive rollups use a fixed `counted_children` list (for example, #100 counts 111–116). A03 walks the A01 parent graph from the pinned tree. If that graph includes another child or a gap, the inclusive totals diverge.
   
   The plan doesn't say whether exact parity is expected, whether any divergence must be explained, or whether the seed has been checked for these cases.

4. **Duplicate and conflicting registrations are untested.** The gates call receipts immutable registered inputs, and line 55 lists "stray or mismatched registered bytes" as a top risk. A01's test covers unregistered, escaping, mismatched-digest, future-dated and duplicate-key inputs. It doesn't cover the same path registered twice with different digests, the same receipt registered twice, two registrations whose `scope.story` disagrees with the hosting story directory, or a receipt rewritten in a later commit together with a fresh registration. Without these cases, an append-only event stream can quietly swap the bytes behind a stable batch-plus-story path. The design's stable retry path makes this case likely.

5. **The B01 test omits watermark and basis display that the design's acceptance item 6B requires.** Design acceptance 6B requires the dashboard to show "timing watermarks and evidence basis, coverage and snapshot provenance". The design also requires the per-measure evidence-through UTC in the row detail, separate from the snapshot as-of and the usage cutoff, with Unknown where none exists. B01's implementation step lists "separate cutoffs, timing basis". B01's test asserts only "valid scoped labels, provenance and direct/child detail". The per-measure evidence-through display and the Unknown watermark case have no test. B02 also never observes them.

6. **A01 doesn't test estimate scope parsing.** `PlanningTree` carries "estimates with source and scope". The design requires scope Unknown when the estimate evidence doesn't declare it. A01's test fixture has no estimate record, so the first check of estimate parsing comes at A05's end-to-end assertion. That is after A03 has already consumed estimates for calibration.

7. **A06's "repeat the same batch identity" step is ambiguous.** Republishing identical bytes at the same path produces no Git change. Publishing different bytes at the same path breaks immutability. A06 doesn't say which case it exercises, or whether it means a second registration event for unchanged bytes. The dedup rule itself is already tested in A02.

## Required changes

1. **Fix the seed admission path (Finding 1).** In A01, specify the seed exception and test it. Admit exactly the existing `historical-actual-backfill` registration on #181. Bind its `receipt_sha256` to `attachments/2026-11-10-actual-backfill.json` specifically, not to the other two `evidence` entries. Require the design's exact digest `8d619b60…b139`, accept that path as the only one outside `attachments/timing/`, and expose its phase, role and attempt as Unknown. Add positive and negative cases to `test_pinned_tree_and_receipt_registration`: the seed is accepted at the exact digest; it is rejected at another digest, at another path, or under another story; and a second `historical-actual-backfill` registration elsewhere is not treated as a seed.
2. **Give the operator verification receipt an owner (Finding 2).** Either (a) assign its schema, kind, path rule, registration and validation fixtures to A01 and document it in `capture.md`, or (b) define it as named fields of `aitm.story-usage-receipt/v1` or its registration in A01. Then state in A04 exactly which fields bind the report identity, source digest, scope, selector, rate basis and coverage. Re-estimate A01 if the scope grows.
3. **Settle the parity expectations (Finding 3).** Before A03 and A05 assert exact parity, establish whether the registered seed contains any same-actor overlap across stories and whether the pinned parent graph matches each seed row's `counted_children`. Then state either "exact parity is expected because none exist", with that check retained as a fixture assertion, or the specific expected held spans or graph differences and how A05 reports them against the readback.
4. **Add the registration conflict cases (Finding 4).** Extend A01's test with the cases from Finding 4: the same path with two different digests, duplicate identical registrations, a scope or story-directory mismatch, and a later-commit rewrite. Define the expected outcome for each (gap, conflict or replay).
5. **Test the watermark display (Finding 5).** Extend `test_offline_render_and_escaped_evidence` to assert the per-measure timing evidence-through UTC, the evidence basis, the planning commit with its commit time, the as-of, and the usage selector, cutoff and pricing basis. Include an Unknown-watermark row. Add the watermark observation to B02's browser checks.

## Optional suggestions

1. Add an estimate record with declared scope and one without to A01's fixture so `PlanningTree` estimate parsing is tested before A03 (Finding 6).
2. State in A06 whether the repeat step republishes identical bytes as a no-op or appends a duplicate registration. Assert the expected single contribution for that case (Finding 7).
3. Require `--commit` to be a full 40-hex object ID and reject ref names and abbreviations. This makes the "moved ref" vector structurally impossible instead of relying on a single early resolution.
4. Have both CLIs check that `--output` resolves outside the repository worktree (after resolving symlinks) and fail closed if it doesn't. The gates state this requirement, but no test enforces it.
5. In A05, name the canonical JSON normalization (key ordering, separators, number and decimal string forms, trailing newline). Then two independent implementations or a later Slice C consumer can reproduce the digest without reading `snapshot.py`.

## Decision

revisions-requested
