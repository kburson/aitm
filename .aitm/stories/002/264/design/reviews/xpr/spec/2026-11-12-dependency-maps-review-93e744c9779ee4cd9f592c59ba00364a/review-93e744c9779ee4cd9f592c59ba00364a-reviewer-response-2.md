<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-93e744c9779ee4cd9f592c59ba00364a"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/264/design/dependency-maps.md"
artifact_commit: "e63ab450a9e79f361ed7fc15169e28a9015a5b91"
artifact_blob: "cffa70dc31c66be92e2a49935cd0c36bf2fa4997"
artifact_digest: "sha256:50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:2d641c6d7af179cf4dd5a85a3bdc8bfac47ffaf80a900a255d16eb349a917115"
  identity_source: "runtime"
started_at: "2026-11-12T15:03:40.810Z"
submitted_at: "2026-11-12T15:07:49.672Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is my round-2 review of
`.aitm/stories/002/264/design/dependency-maps.md` at blob
`cffa70dc31c66be92e2a49935cd0c36bf2fa4997` (commit `e63ab45`, digest
`sha256:50a78e6d…16e7`). That digest matches the revised SHA-256 stated in
author response 1.

**Read coverage.** I read the whole revised artifact (lines 1-60 of 60) in
one Read call, and author response 1 in full. I compared the revision line
by line with the round-1 blob I read earlier. I did not use Git.

A correction to my round-1 summary: I said the artifact had 61 lines. Both
versions have 60 content lines. This does not affect any finding.

**R1-F001 (visibility profile on the static command): resolved.**

- **Required input (line 13).** The command now takes "an epic number, exact
  Git planning commit, visibility profile, and explicit output path".
- **Private bundle profile (line 13).** It names the versioned built-in
  `private-local-v1` profile for the private bundle and marks it ineligible
  for attachment. Line 25's admission rule therefore applies to every
  bundle. The line 31 `<visibility-profile>/` path is only for approved
  attachment profiles, so a private bundle can never be put at an attachment
  path.
- **Policy source (line 13).** Attachment profiles resolve from "an
  owner-approved allowlist pinned in the planning commit, following the M6
  preview precedent for reviewed story IDs and display titles". This agrees
  with Leaf A line 25 of the M6 read-only preview plan. The profile governs
  admitted fields, links, source-pin visibility and destination. Output is
  held when the profile cannot be resolved or does not match the
  destination, which agrees with the "keep output local" rule on line 29.
- **Provenance on outputs (line 14).** All three outputs now carry the full
  planning commit, the UTC cutoff, the profile key and the profile digest.
  Together with line 31, this lets the attachment review on line 29 check
  each file's provenance directly. It also gives line 15's "same admitted
  input" reproducibility claim a concrete identity.
- **Conformance (line 59).** The Python and TypeScript fixtures now share
  the same profile input.

**Optional suggestions from round 1.**

- Suggestion 1 was adopted: line 35 now reads "outside this design".
- Suggestion 2 was adopted: line 22 now says that a displayed child epic
  that is an endpoint is an ordinary, reducible prerequisite. It preserves
  "explicit gates of the selected epic", which matches line 21.
- Suggestion 3 was adopted in part. The tie-break is now exact: "Compare
  equal-length paths lexicographically by numeric story ID." The author
  response leaves the other carried-over items to the Plan. That is
  acceptable, and none of them blocks Design acceptance.

**New-text check.** I checked the changed lines (13, 14, 22, 35 and 59)
against lines 15, 21, 24, 25, 29 and 31. They introduce no contradiction.
Holding attachment output on an unresolved or mismatched profile is
consistent with the last-valid rule on line 15. Allowlist exclusion goes
through admission (line 25), so a child excluded by the allowlist is not an
"expected admitted child record" under line 24's hold rule. The graph rules
and the #133 qualification numbers did not change, so my round-1 source
checks still apply: 41 children, 64 edges, 9 reducible, 55 displayed, the
#133 → #2 gate, #160 → #162 absent, and the #227/#193 reverse-field gap.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. In the Plan, give `private-local-v1` a one-line admission rule. For
   example, it might admit every record readable at the pin with no
   allowlist filtering. "The operator's local reference" on line 13 is
   clear in intent, but the restricted-record fixture on line 59 needs a
   concrete admission rule to compare against.

## Decision

accepted
