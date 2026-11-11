# #203 independent exact source review HOLD

Claude Opus 5.5 medium, local off-platform, November 10, 2026 America/Chicago. Head `3359eda7ebf21db2267e2faf3436f72c4bf9a7d6`, tree `0354543e89d0557b1e8949682af2844615d8c0b0`, literal trunk `e4701f2e89d34f93f13d717199254b66aa3f0457`. Review packet SHA-256 `f006863ac72c9e1b49bcfdfe8db462281dc6bcb2017b73139149392918e89a60`.

# HOLD

The production logic matches the JIT almost everywhere, and the hosted identities and coverage line up with the local gates. Three things block acceptance. One JIT rule for the v2 codec has no visible check or test. Two token-refusal tests pass for a different reason than the one they are named for. The baseline test count in the hosted evidence doesn't match the local inventory.

## Blocking

**B1. The v2 decoder may admit an empty original span.**
- The JIT lists "nonempty original span" among the v2 admission rules.
- `_validate_route_records` has no `hold.affected.start < hold.affected.end` check, and `_route_target` doesn't have one either.
- None of the 28 cases in `test_v2_decoder_rejects_malformed_or_unowned_shape` uses an empty span.
- With an empty span, the `_eligible(...)` span check in `_route_proposal` could pass trivially.
- Fix: if `ProofHold` already enforces this when it is decoded, cite that and add an `empty-span` case. Otherwise add the check and the case.

**B2. Two of the issued-token tests don't isolate the change they are named for.** The code looks right by inspection: `_route_proposal` refuses when a `_Resolution` exists, and `require_route_disposition` compares `(hold, record)` with the issued proof. The JIT asks for exact tests of these paths, though, and these two would pass even if those checks were missing.
- **`issued...[expire]`** runs with `release=True` and moves the clock past `expires_at`. The `self._now() >= hold.expires_at` check refuses on its own, so this case can't be told apart from `[expired-proposal]`. There is no test of an issued **GAP** token refusing after `expire()`, which is the case the `hold_state` field exists for.
- **`issued...[legacy-dispose]`** rewrites the transcript back to `older_rows` before calling the legacy `dispose`. The terminal batch recheck and the target prefix recheck would refuse from the rewrite alone.
- Both cases assert only a bare `LedgerError`, with no `match=`.
- There is also no isolated test that a hold already changed by a `_Resolution` refuses at issuance.
- Fix: add a release=False token test that only calls `expire()`. Add a dispose test whose refusal comes only from the resolution, or assert the refusal message that resolution produces.

**B3. The hosted and local baseline counts don't match.**
- The hosted raw replay reports `baseline_tests: 995`.
- The local inventory reports 996 retained baseline IDs plus 73 new ones, which makes 1069. The JIT also says 996 on `e4701f2e`.
- Both runs report 1069 tests in total, so the hosted run implies 74 new tests while the local list has 73. I counted the 73 myself.
- Explain the difference before Close. If the hosted baseline was taken against a stale tree such as #202's, the "before" evidence doesn't bind to the literal trunk.

## Verified

**Identities.** Base is `e4701f2e`, head is `3359eda7`, and the reviewed tree is `0354543e`. All six jobs passed. Coverage is 10652/11604 for product and 778/821 for helpers in both the hosted and local runs. Only the two allowed files change.

**v1 codec and old reader.**
- `_ScopeSnapshot` and `scope-v1.json` are unchanged.
- The probe re-encodes a v1 file byte-for-byte.
- The frozen old reader refuses v2 at the strict codec and leaves the file byte-identical (sha `8002ac…`).
- `test_default_hold_keeps_v1_and_cannot_be_retroactively_retained` confirms the exact v1 bytes.

**v2 decoding (`_snapshot`).**
- It tries v1 first, then v2.
- `_validate_scope_snapshot` and `_validate_route_records` reject mixed, unknown, extra and nested shapes.
- The checks cover: digests (lower-case 64-hex), allowed `hold_state` and outcome values, RESOLVED only from HELD, unique IDs, at most one disposition per hold (counted within `route_dispositions` only), the target's link to its hold, provider, session, stream and ordinal, terminal ordering, a distinct receipt and boundary, and the prefix's source, locator and incarnation with strictly increasing offsets.

**Writer custody (`_require_route_custody`).**
- It requires an initialized source key and an approved source matching surface and provider.
- It validates each new object's refs and that its receipt ref is keyed to its command.
- It runs on every writer snapshot and every v2 `_save`.
- Readers without a writer get the structure only. The custody, source-key and symlink tests cover this.

**Legacy writers and reserved IDs.**
- `replace(state, …)` keeps the v2 type, so mark, handoff, default `hold`, `expire` and `dispose` carry both new collections through unchanged. `test_legacy_writers_preserve_both_v2_collections` checks this.
- `_require_unused_route_disposition_id` reserves stored route-proof IDs against legacy writes, and the decoder rejects any overlap with legacy IDs.

**Opt-in hold (`hold(..., retain_route_target=True)` / `_route_target`).**
- The hold must be owned and anchored, with a positive prefix.
- A hold that would be GAP at capacity raises before anything is published.
- Re-asking for a legacy hold with no saved target raises.
- An exact replay returns the existing hold, and different bytes refuse.
- A publication interrupted before or after the file replace recovers to a single consistent snapshot.

**Issuance (`verify_route_disposition` / `_route_request` / `_route_proposal`).**
- The writer lease is taken first. The inbox `publication()` lock is then held, together with `open_grant` and `require_witness` before and after, across proposal, publication and the re-run confirmation.
- The request must be exactly a `DispositionRequest` matching the command's ID, project, hold and `release_previous`. The envelope digest is stored.
- The terminal must be a TURN, the final recognized boundary, with no cursor and only `BOUNDARY_UNVERIFIED`.
- The original boundary must appear exactly once in the same batch, with the same checkout.
- The saved prefix is reauthenticated, and the current physical extent must equal the read prefix.
- RESOLVED checks the route before the span, at every event inside it, and at its end. A failed check raises and is not turned into GAP.
- Nothing calls `_apply` or the legacy `dispose`, and nothing consumes the queue item.

**Re-checking (`require_route_disposition`).**
- The token must be the same object in the weak identity map. It re-runs the full request and proposal checks, compares the result with the issued proof, and does not write.
- The consumed, withdrawn, revoked, expired-advertisement, relocated and later-usage cases are each isolated and each refuse.

**EOF and later usage.** The ordered fixture has monotonic rows with +4 deltas and asserts no cursor and only `BOUNDARY_UNVERIFIED`. After real later usage the parser still shows the same receipt, but both issuance and reissuance after restart refuse.

**Directory sync failure.** No token is issued. A later exact replay neither rewrites the file nor changes the view.

**State left alone.** `view()`, `journal.as_of()`, the journal store bytes and the cursor are all compared and unchanged across issuance and replay.

## Non-blocking

1. The witness uses `_scope_now()` while RESOLVED expiry uses `ScopeState._now()`. That matches the existing code, but the two clocks should be documented.
2. If `recheck()` or `require_witness` fails after the yield, the record stays on disk but no token is issued. This is allowed ("a persisted result never issues authority"), but it deserves a comment.
3. No test sends a `DispositionRequest` under a grant registered only for `mark`. The wrong-type test changes both the request type and the grant's action.
4. The JIT asks for an assertion that no progress or journal path consumes either prefix. The tests show this only indirectly, through unchanged journal bytes and cursor.
5. For #210: once `expire()` overtakes a HELD GAP proposal, it can never be reissued, because the replay record's `hold_state` no longer matches. The code confirms this conservative behaviour.
6. `VerifiedRouteDisposition` also holds `_command`, which the JIT doesn't list. It's harmless.

The merge, "closed" provenance and graph re-check come after this review, so none of them is evidenced yet.
