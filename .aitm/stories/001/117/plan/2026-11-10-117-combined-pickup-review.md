# #117 independent combined pickup review

Claude Opus 5.5, high effort, reviewed the exact combined pickup on November 10, 2026 against trunk `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`.

# Verdict: HOLD

I reviewed only the packet and used no tools.

Most of the design holds up. It covers the accepted M07 contract, keeps the delegated owners (M08/M09/M11/M13/M16) out of scope and doesn't invent any Grok capture proof. It is held for one main reason: the four-hour cap isn't realistic. There are also a few custody and ordering gaps that need text and test fixes, which are cheap.

## What I checked

| Item | Result |
|---|---|
| Accepted scope | Mostly conforms. The four accepted tests, UTC restart expiry, the Develop owner missing its destination worktree proof, legacy receipt shapes and green with `test_scopes.py` are all present. Two deviations: the receipt type is renamed (B5), and `install.py` is added beyond the accepted file list. The launcher addition is defensible because the installed launcher breaks the accepted "preserve exact #83 invocation" rule. |
| Known prerequisites | Pass. #116 is closed, Done and delivered; the base `d769b31` is its merge. M04/M05/M06 seams are named. The missing M06 Grok enrollment bridge is stated openly. |
| Testable author and native evidence | Mostly pass. Proofs come only from an adapter reading under the lease, and caller input can't mint or replay them. The Grok handoff expectation is undecided (B4). |
| Native-order suffix revalidation | The rule is specified, but the conflict-grouping key is ambiguous and there's no named test for a late earlier transition (B3). |
| No invented Grok capture proof | Pass. Missing capture proof gives a coverage hold, with no capture epoch and no activation claim. |
| Adopted compatibility and receipt custody | Two gaps: an adoption race (B1) and "queued" acknowledgements with no consumer (B2). |
| Four-hour cap | Fail (B6). |

## Blockers

**B1. Adoption race around `remember_claude_session`.** The pickup picks the adopted route first, then rechecks adoption only under the legacy inbox publication lock at enqueue time. In the pre-adoption Claude path, `remember_claude_session` writes to the legacy ledger *before* that locked recheck. If adoption or the M16 freeze wins in that gap, a legacy write lands on state that has already been adopted.
- **Fix:** do the session write inside the same locked recheck, or prove the M09 writer guard refuses it.
- **Test:** inject the race between the unlocked choice and the session write.

**B2. "Queued" acknowledgement with nothing to consume it.** The witness gate applies only to adopted legacy producers. The new `monitor scope mark|handoff|dispose` path still returns `queued` into a live M06 inbox that nothing drains until M11, so entries pile up with no limit and status stays `queued` forever.
- **Fix:** put both producers behind the same consumer admission witness. Without it, return a sanitized unavailable result and no acknowledgement.
- **Also specify** how the M06 drain handles the new envelope types: skip them in submission order without stalling later control commands, and never `discard` them.
- **Test:** a scope envelope placed ahead of a control command doesn't block it.

**B3. Conflict grouping must use the target boundary.** The pickup groups competing proposals "by … native ordinal plus before-generation", which could be read as the receipt's ordinal. Two receipts at different ordinals before the same next supported turn have to conflict. Grouping by receipt ordinal could apply both.
- **Fix:** state that the key is the stream plus the *target boundary* ordinal plus the before-generation.
- **Add two named tests:**
  - Receipts at different ordinals that share a target boundary conflict.
  - A late earlier transition reprojects the suffix, and a later handoff that was already effective becomes stale and held. This must be distinct from "late revision".

**B4. The Grok handoff expected result is undecided.** "If M05 supplies only the same-prompt link, keep the handoff in hold" leaves the test outcome open. The packet already settles it:
- M05 emits ordered completions with offsets per `stream_ref`, so next-turn position is provable from the fixtures.
- Every Grok route is held anyway, because capture proof is missing.
- **Fix:** fix the assertion now. The marker join is verified, the next-turn position is proven from the M05 fixture ordering, and the route is a coverage hold for missing capture proof. No Grok handoff takes effect in M07.

**B5. The accepted contract signature has drifted.** The accepted contract is `apply_handoff(command: Handoff, receipt: VerifiedBoundary)`; the pickup uses `VerifiedScopeBoundary`. Keep the accepted name, or export it as an exact alias.

**B6. The four-hour cap isn't realistic.** The budget is exactly 4.0 hours with no reserve. It has to cover:
- a new private versioned snapshot under the lease;
- routing with conflicts, suffix reprojection, A→B→C and Develop destination proof against a pinned destination ledger;
- bounded UTC holds;
- four new sealed envelope variants;
- a private authority snapshot with lease-free producer reads;
- a new CLI;
- five legacy grammars with the adoption race and the witness gate;
- recognizer changes for both Codex and Claude;
- the Grok position seam;
- dual-variant launcher verification;
- GREEN across a 714-test suite with two 90% coverage floors.

Even the two-hour checkpoint needs both halves working. The pickup's own rule applies: reopen Refine. The natural split is:
- **M07a:** scope state, routing, holds, native evidence and the four accepted tests.
- **M07b:** envelopes, authority, the CLI, legacy compatibility, the recognizer grammar and the launcher.

The launcher is also the most separable piece if it needs to move again. This is a pickup and Refine action, not a new owner decision.

## Optional refinements

- **R1. Source-key exposure.** Instead of giving the CLI a lease-free read of the writer-only source key, derive a producer-scoped subkey or namespace. That's within the trust model either way, but it keeps M06 custody tighter. Keep the "CLI cannot create keys" test.
- **R2. `--request-id`.** This option isn't in the accepted grammar. Define where it comes from or drop it. Set `allow_abbrev=False` so the recognizer's grammar and argparse acceptance match exactly.
- **R3. `item alias`/`item parent` IDs.** These mint a new `uuid4` on every invocation. State that "idempotent queue IDs" means an exact retry of the same envelope, not identical CLI reruns.
- **R4. Hold overflow.** Say which side overflows at 256 (I'd suggest rejecting the newest, which becomes a gap immediately, never evicting existing holds). Add a size limit, with fail-closed behaviour, for the scope snapshot's transition history.
- **R5. Launcher expansion.** Distinguish an unset variable from an empty one, for example `${CODEX_THREAD_ID+"CODEX_THREAD_ID=$CODEX_THREAD_ID"}`, so an empty string never reaches `session_reference`.

## What clears the HOLD

1. Re-slice per B6 so each part fits the cap, with its own checkpoint.
2. Make the text and test edits for B1–B5 in the pickup that goes to Develop.

The design substance needs nothing beyond that, and live source runtime integration and journal publication stay with the next coordinator as delegated.
