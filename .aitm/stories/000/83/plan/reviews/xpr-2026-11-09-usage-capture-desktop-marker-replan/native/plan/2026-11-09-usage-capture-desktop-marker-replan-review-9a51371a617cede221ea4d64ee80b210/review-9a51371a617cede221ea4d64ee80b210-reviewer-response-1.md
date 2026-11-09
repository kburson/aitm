<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9a51371a617cede221ea4d64ee80b210"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md"
artifact_commit: "37eb09413d7b96d34b5e1219abedf400bfc1cd3f"
artifact_blob: "9c4b3d3a8aaa03eed901b9166f271cfe065f4f78"
artifact_digest: "sha256:b09cb8ee3dfee4b2af7b0773fa3a2b8dc54b68ba2d1287e17563eaf6da5abd90"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:9cec225cc3095656c7d62b2ee43a2ad3b6ff7fc0d1605ea367ee75313ed320c6"
  identity_source: "runtime"
started_at: "2026-11-09T22:14:19.201Z"
submitted_at: "2026-11-09T22:16:37.707Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is turn 1 of an independent XPR review of `.aitm/stories/000/83/plan/usage-capture-desktop-marker-replan.md` at sealed digest `sha256:b09cb8ee3dfee4b2af7b0773fa3a2b8dc54b68ba2d1287e17563eaf6da5abd90` (commit `37eb094`, blob `9c4b3d3`).

**Read evidence.** I read the artifact fresh with the Read tool from line 1 with a 20-line limit. The file has 16 lines, so that one contiguous range (lines 1–16) reached EOF. Follow-up reads at offsets 21 and 41 confirmed the file is 16 lines. Nothing was truncated or replaced by an omission marker. This is the first turn of this review ID. The review directory holds only the author startup, the invitation and this pending response, so there are no prior author dispositions to verify.

For context I read these files:

- the author startup and reviewer invitation for this review;
- the #96 `story.md` (lines 1–47, EOF) and #96 `events.jsonl` line 14;
- #83 `events.jsonl` line 36 and `attachments/source-delivery.md` (lines 1–14, EOF);
- baseline plan `usage-capture-implementation-plan.md` lines 107–114 (the U04 section) and the U04 sizing row on line 40;
- the accepted launch-health amendment `usage-capture-launch-health-replan.md` (lines 1–22, EOF), to compare precedent;
- the earlier relationship-replan XPR turn-1 reviewer response, only to match format.

Only the join and submit commands were available to me. I could not run Git, confirm that commits exist, or inspect the U04 parser. Product source is not checked out in this sparse planning worktree, which holds only `CLAUDE.md`, `README.md` and `.aitm`. I also could not see the raw #96 native record. The claims that the parser is a full-match parser and that the trailing byte is exactly one ASCII LF rest on the artifact's own statement, plus the matching #96 and #83 event `basis` ("actual Codex Desktop marker carrier framing reproduced twice in #96").

**Gate observation (not a finding).** There is no SAR or SPR record for this amendment in this worktree. Line 13 already requires SAR, independent SPR and native XPR acceptance of the exact bytes before #88 reopens. The author must close that gate, but the text is not defective.

**Verified as sound.**

- *Release pin and event consistency.* `c2f3582d07d0f3dfeb680ab565fb3a5c5339d2ac` on line 3 matches the protected trunk merge in `source-delivery.md` (line 9, PR #97). It also matches `released_source` in #83 event 36 and #96 event 14. Both events moved the stories from `develop` to `plan` at 22:13:01Z, after the 22:06:39Z merge. That matches line 13's "Return #83 and #96 to Planning". The #96 story (line 47) records that the amendment is under review and that live qualification is paused at the released source.
- *Blocker diagnosis.* The defect is a specific carrier difference: one trailing LF after the canonical wrapper. It was seen twice on distinct single-line calls, and the first native tool result joined to the exact queued command. This supports reading the LF as Desktop transport framing rather than command content. A full-match parser would reject it before validating the receipt. The artifact also records the containment: no production install, Claude workload or Core activity followed (line 3).
- *Ownership.* Line 7 keeps the fix inside U04 / #88, in "the Codex adapter and its tests". This matches the U04 Files list on baseline line 109 (`sources/codex.py`, `tests/test_codex.py`, `tests/fixtures/codex/usage.jsonl`). It does not reach into U02's marker and binding ownership (first amendment line 38), the ledger or `types.py`.
- *Narrowness of the framing rule.* Line 7 accepts only the existing canonical wrapper with zero or one final ASCII LF. It rejects leading bytes, other trailing bytes, alternate whitespace (so CR/CRLF are excluded), extra code and unsupported wrapper shapes. It forbids generic stripping and arbitrary-code parsing. Command, output and receipt identity mismatches and uncertain native tool order still reject. Accounting and privacy behaviour are preserved. That is the right shape for a carrier fix.
- *Tests.* The plan requires a sanitized positive regression for the exact retained shape and explicit negative-shape coverage (line 7). It requires RED on the exact released code and GREEN with existing adapter tests (line 9).
- *Original evidence and authority.* The proof against the original #96 native record is read-only or disposable-state and uses the unmodified authorized record. It must join the actual queued command's receipt and first request through the approved scanner/adapter path, with zero use admitted outside authorized scope (line 9).
- *Protected-source path.* The fix needs a full serial locked suite, exact independent source review, a normal protected-trunk PR, and verification of the exact merge tree and wheel before qualification (line 9). Prior U04 acceptance is preserved and gets a separate repair receipt (line 13).
- *#96 resume.* #96 resumes only on independently accepted, delivered source with a fresh reviewed JIT. It repeats the isolated proof and rehearsal before production installation and validates the full real receipt before #83 closes (line 13).
- *Permanence and Core exclusion.* Line 13 keeps the same project identity and eventual ledger and leaves Core #2 outside execution. Line 15 leaves lifetime scope, metrics, installed command and the later C44 handoff unchanged. The package stays the permanent collector.

The findings below cover three gaps: the conditions for reusing evidence, a checkable cap and forecast anchor, and the route condition on the framing tolerance.

## Findings

1. **F1 — "Reuse authentic early #96 evidence where it qualifies" has no identity rule (line 13).** The early #96 evidence was produced while the released `c2f3582` package was under test. Resumed qualification must run on a different, repaired wheel. The artifact does not say which classes of early evidence may carry forward. Collector-produced artifacts are not separated from provider-native inputs. Examples of collector-produced artifacts are ledger rows, cursor or checkpoint state, status heartbeats, rehearsal environment outcomes and receipt fields. The rejected first call shows the old wheel's processing already diverged on real input, so its outputs cannot vouch for the new wheel. As written, a JIT could carry forward old-wheel outputs that the new wheel never produced, or that it would produce differently. The receipt would then mix two source identities. That conflicts with line 9 ("Verify its exact merge tree and wheel before using it for qualification") and with the strict identity requirement for the receipt.
2. **F2 — The caps cannot be checked without a repair forecast and cumulative accounting (line 15).** Line 15 says the four agent-hour U04 and U11 caps and the 48.5-hour epic estimate "remain in force" and says to stop "before any ownership or forecast deviation". Two things are missing. First, there is no forecast for the U04 repair or for the repeated U11 isolated proof and rehearsal. Second, the artifact does not say whether repair time counts on top of U04's original actual hours or is a fresh allowance. The same question applies to the repeated U11 proof and rehearsal against U11's 3.5-hour qualification portion. With no anchor, the stop rule has nothing to measure deviation against. Precedent: the accepted relationship replan stated a 45-minute forecast within U13's cap. Line 13 already handles the 0.5 agent-hour workload cap ("record its cost under the same controlled workload limit"). The non-workload hours are not handled the same way.
3. **F3 — "On the verified current Desktop route" is ambiguous as a condition (line 7).** The sentence could mean two things. (a) The adapter must prove from the native record that a record came from the current Codex Desktop route before it allows the trailing LF. (b) The phrase only describes where the shape was observed, and the tolerance applies to every Codex native record the adapter reads. Reading (a) requires a route witness that the artifact neither names nor scopes. It also risks rejecting the actual #96 record if no such field exists, or pushing the implementer into new route-detection logic beyond a "narrow carrier compatibility fix". Reading (b) is the more natural one for a narrow fix, but then "on the verified current Desktop route" reads as a constraint that the tests do not enforce. Either way, the negative-shape tests and the source reviewer need to know which reading is intended.

## Required changes

1. (F1) Define qualifying reuse in line 13. Early #96 evidence may carry forward only as provider-native input records with their recorded authorization and controlled-workload provenance. The delivered repaired wheel must reprocess those inputs. No ledger state, checkpoint, status or heartbeat output, rehearsal outcome or receipt field produced by `c2f3582` may count toward the repaired qualification receipt. Every receipt field must bind to the repaired merge tree and wheel digest.
2. (F2) In line 15, state a forecast for the U04 repair and for the repeated U11 isolated proof and rehearsal. Also state that each counts cumulatively against the leaf's existing actual hours under its four-hour cap, and the U11 portion within its 3.5-hour qualification allowance. The stop rule then has a concrete anchor. If either cumulative total cannot fit, say so and stop for re-estimation now rather than during execution.
3. (F3) In line 7, state whether the zero-or-one-LF tolerance is conditional on a named native route witness or applies to every Codex native record the adapter reads. If it is conditional, name the field and add a negative test showing that a record without the witness still rejects the trailing LF. If it is not, reword the phrase so it describes where the shape was observed rather than imposing a condition.

## Optional suggestions

1. **O1 — Pin the #88 reopen base.** Line 13 says "the exact current protected trunk release", while line 9 requires RED on "the exact released code". Naming `c2f3582d07d0f3dfeb680ab565fb3a5c5339d2ac` (or the exact later trunk SHA, if it differs) as the #88 base would remove any drift between the RED base and the branch base. The launch-health amendment set this precedent by pinning `05318125…`.
2. **O2 — Make the identity comparison explicit.** Say that the adapter removes exactly one final LF only to recover the command bytes. Those bytes must then equal the queued command byte for byte, and the LF never enters any command, receipt or output identity or digest. Line 7 implies this ("only as carrier framing"), but saying it outright gives the source reviewer a precise check.
3. **O3 — Cover both observed calls.** Line 3 records two distinct single-line calls with the same suffix. The read-only proof could show that both join correctly, or record why only the first is in scope. This guards against a fix that only handles the first-call position.
4. **O4 — Distinguish the repaired wheel from the rejected one.** If the repaired wheel keeps the same package version as `c2f3582`, say that receipt and rehearsal identity rest on the wheel digest. Alternatively, require a version change so status, heartbeat and receipt version fields cannot be confused with the rejected wheel in any retained isolated environment.

## Decision

revisions-requested
