<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a9af7c6091f4f1719529a371c02f6f77"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/524/design/github-extension-design.md"
artifact_commit: "8862808e2dd2062df1c0d2e156e6711c2dbaabbb"
artifact_blob: "e4e12d87bab444496df675abf41d410b63eb6fa5"
artifact_digest: "sha256:bce3087c1067ca38c1f25c7c98486c5934b4eb4fff3048fcf5eee75e99cf547b"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:0c13cad915596f8573c341829b1f37504efbaedb00fd577eb7fafa121ffe23b5"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:28.603Z"
submitted_at: "2026-11-27T06:15:17.716Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005","R1-F006"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The design is well bounded. Core keeps story state, admission and evidence authority. The provider is limited to GitHub translation and scoped host verification. The #525 read-only source slice is cleanly separated from hosted mutation, M3 and board work. It has an explicit handoff contract that M7 #522 consumes (`history-import-design.md` lines 9 and 48). The complete / unavailable / incomplete result taxonomy is the right one. Binding cursors to source identity, cutoff and field selection, and refusing to infer a repository-wide snapshot from a live list, are both correct and important. The hosted-delivery bullets defer properly to Core's #2 governed PR handoff, the #158 receipt boundary and the master plan's every-push audit open decision (`master-plan.md` lines 40 and 99).

I checked the following and they hold:

- All relative links in the artifact resolve: `000/1/plan/master-plan.md`, both `000/2/plan/*` files, `005/522/design/history-import-design.md` and `005/523/design/rubric-design.md`.
- The estimate arithmetic is right: 3.75 + 7.5 + 3.75 + 19.5 + 6.5 + 3.5 = 44.5, and the PR row adds up (4 + 3.5 + 4 + 4 + 4 = 19.5). Every named child is at or under 4 h.
- M7's estimate explicitly excludes the #525 adapter (`history-import-design.md` line 54), so #525 is not double-counted across milestones.
- The master plan's M2 row items all have a home in the capability map: issue graduation with uncertain-outcome reconciliation, hierarchy, sparse projection, PR/CI mapping, protection readback, GitHub init and the every-push audit caveat.

The remaining issues are concentrated in the #525 source-access contract. It is the first landable slice and the one that M7 will pin byte-for-byte, so its semantics need to be exact before JIT. Several statements are either inaccurate for GitHub's REST behavior or leave M7 unable to tell whether the handoff covers its corpus needs. None of the issues affect the overall architecture.

## Findings

### R1-F001 — "Later-edited" detection from `updated_at` overclaims and will misclassify most issues

The artifact says: "An observed update after the cutoff is identified as later-edited with preserved acquired bytes and timestamps." On GitHub, an issue's `updated_at` changes on any activity: new comments, label and milestone changes, assignment, state changes, title edits and transfers. It does not change only when the body is edited. For a legacy corpus that has seen any post-cutoff activity, nearly every touched issue would be flagged "later-edited" even when its body bytes are unchanged since the cutoff. This weakens the signal M7 uses to decide disposition (`history-import-design.md` line 34: "edited sources"). It may also push records into quarantine needlessly.

The reverse also matters. For comments, `updated_at` is a closer proxy for a body edit, but it still does not prove that the acquired bytes differ from the bytes at the cutoff.

The contract should name the observation precisely: "updated after cutoff; acquired bytes may postdate cutoff". It should state that this is a conservative drift flag, not an edit claim. Optionally, it can name a qualified edit-history source (for example, GraphQL `userContentEdits` / `lastEditedAt`) as a later capability if M7 needs true edit detection. The issue and comment flags should be distinguished.

### R1-F002 — The REST issues list includes pull requests; the contract does not say how they are treated

The artifact relies on "documented REST endpoints where their fields suffice". `GET /repos/{owner}/{repo}/issues` returns pull requests as issues, marked by a `pull_request` key. Issue numbers and comments are shared across issues and PRs. The contract does not say whether PRs are excluded, included or reported as a separate kind. This affects:

- the "exact bounded inventory" count in the handoff proof;
- the issue and comment limits pinned at JIT;
- M7's inventory, which says the historical count "around 2,165 is a planning hint" (`history-import-design.md` line 13). An inventory that silently mixes in PRs would distort that count.

The source interface should state the PR disposition explicitly and report it in the receipt (for example, as excluded counts). The deterministic fixture should include a PR among the listed issues.

### R1-F003 — Byte form and digest basis for bodies are unspecified, so digests are not reproducible across implementations

The artifact promises "selected raw fields or streamable bytes, a digest". GitHub can return a body as source markdown (`raw`), rendered `html` or `text`, depending on the media type. The API carries it as a JSON string, so encoding and normalization choices (UTF-8, line endings, Unicode normalization, a null body versus an empty string) change the digest. M7 must "match exact hashes and counts on repeated extraction and fresh checkout" (`history-import-design.md` line 34). That only works if the byte form is pinned in the versioned source schema.

The contract should name the media type and representation (for example, the raw markdown body as UTF-8 bytes of the decoded JSON string, without normalization). It should also name the digest algorithm and the exact digest input for each record and for the page evidence. It should state how a `null` body is represented as "explicit absence", distinct from an empty string.

### R1-F004 — The initial payload omits fields M7 will need, and the handoff does not enumerate which M7 sources are out of scope

The initial issue payload lists repository and issue IDs, number, URL, state, timestamps and body. It omits:

- the title;
- labels;
- `state_reason` (completed / not_planned), which matters for "historical closure retained as source data" (`history-import-design.md` line 7);
- the author or other actor identity, if M7 needs it.

The title, at minimum, is plausibly required to normalize a legacy story record. Labels are a common carrier of the legacy kind, phase and estimate metadata.

Separately, M7 captures "reviewed phase estimates, Timing Log comments, and supported commit or approval evidence" (`history-import-design.md` line 14). M2 selects only Timing Log comments and defers commit or adjacent evidence. That deferral is sound. However, the handoff does not say whether non-Timing-Log comments (where reviewed estimates or approvals may live) are in or out of #525's scope. M7 line 48 will "refuse an incompatible or insufficient handoff", and that refusal will happen at M7 intake, after #525 has already shipped. The gap should be closed at design time:

- Either add the title, labels and `state_reason` to the initial payload, or explicitly defer them.
- Publish in the handoff a list of covered versus not-covered M7 source kinds, so that M7's sufficiency check is mechanical.

### R1-F005 — Ownership and timing of the Timing Log selection predicate is circular across M2 and M7

M2 says: "Pin M7's approved Timing Log selection predicate and its version in the qualification configuration." This makes #525 qualification depend on an M7 decision. M7, however, lists "trusted Timing Log formats" as something to resolve "before implementation pickup" of M7 (`history-import-design.md` line 44). M7 pickup in turn waits on #525 (line 9, line 65). As written, #525 cannot qualify until M7 has made a decision that M7 schedules after #525.

Either of these would resolve it:

- (a) Make the predicate a versioned request parameter that the consumer supplies. #525 then qualifies the selection mechanism against a fixture predicate, and the receipt records the predicate ID and version used.
- (b) Make "M7 Timing Log predicate v1 approved" an explicit JIT prerequisite of #525, and update M7's pre-pickup list to match.

Option (a) keeps #525 independent of M7 decisions, which is consistent with the rest of the artifact's independence claims.

### R1-F006 — "Adapter" ownership wording conflicts with M7's design

This artifact says "The adapter registers through Core's released extension discovery surface. The M2 provider owns the dedicated read interface." M7 says "M7 owns the legacy source adapter and the separate corpus export envelope" (`history-import-design.md` line 7), while also excluding "the #525 adapter" from its own estimate (line 54). Readers cannot tell whether "legacy source adapter" in M7 means #525's GitHub read adapter or an M7-side legacy-format parser or normalizer.

This artifact should name the #525 component unambiguously, for example "GitHub legacy-source read adapter (M2-owned)". It should state that M7's parser and normalizer that consume it are M7-owned. Ideally the M7 design would get a matching one-line clarification in its own review cycle. The fix requested here is only to this artifact's wording.

## Required changes

1. Reword the cutoff and update semantics so that a post-cutoff `updated_at` is a conservative "may postdate cutoff" drift flag, distinguished for issues and comments, not an edit claim. Optionally name a qualified edit-history source as a later capability (R1-F001).
2. State the pull request disposition for the issues listing, report it in the receipt, and include a PR in the deterministic fixture (R1-F002).
3. Pin the body media type and representation, the null-versus-empty encoding, the digest algorithm and the exact digest input in the versioned source schema (R1-F003).
4. Add the title, labels and `state_reason` to the initial issue payload, or explicitly defer them. Add a covered versus not-covered M7 source-kind list to the handoff (R1-F004).
5. Resolve the Timing Log predicate circularity, preferably by making the predicate a versioned request parameter that the receipt records (R1-F005).
6. Name the M2-owned GitHub read adapter unambiguously, and distinguish it from M7-owned parsing and normalization (R1-F006).

## Optional suggestions

1. "Use focused delivery slices with four to six children where applicable" reads as an epic-wide count, but the estimate table implies about 12 children (1 + 2 + 1 + 5 + 2 + 1). Clarify that four to six applies per capability slice, or drop the count and keep the ≤ 4 h per child rule.
2. The link line to the master plan and the Core #2 documents sits between "Acceptance and open decisions" and "Delivery handoff and sequencing". Move it to the end, or into a "References" line, so it does not read as part of the acceptance list.
3. In the fixture list, consider adding a deleted or `ghost` author, a minimized or hidden comment, and an issue transferred out of the repository. Each produces a distinct REST shape and exercises the unavailable versus empty distinction.
4. Consider stating that secondary rate limits and `Retry-After` / `x-ratelimit-reset` handling are part of the "read retries" contract, since the live bounded read against a corpus of about 2k issues plus comments can trigger them.

## Decision

revisions-requested
