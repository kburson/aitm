# Story #264 Design same-provider confirmation

**Decision — ACCEPT** the exact revised Design for story #264. No required Design revisions remain.

## Review evidence

- Candidate `.aitm/stories/002/264/design/dependency-maps.md` at supplied commit `e63ab450a9e79f361ed7fc15169e28a9015a5b91`. Read all physical lines 1–60, including blank lines, from the review worktree. Independently computed raw SHA-256 `50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7` and rechecked it at submission.
- Read native XPR round 1 reviewer response lines 1–161 and author response lines 1–50 for `review-93e744c9779ee4cd9f592c59ba00364a`. The story record still matches the previously reviewed SHA-256 `d6b9798689a9c2427dc903e121e4ca81eb0aae25ee2fa565cf889cfb22cbceea`.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 15:08:23 UTC and was submitted 2026-11-12 15:08:58 UTC.

## Finding disposition

**Native XPR R1-F001 is addressed.** Line 13 specifies a visibility profile as a required command input and identifies the built-in versioned `private-local-v1` profile as ineligible for attachment. The attachment profile resolves from the owner-approved allowlist at the exact input planning commit. It governs fields, links, source-pin visibility and destination. An unresolved profile or scope mismatch holds attachment output.

Line 14 puts the planning commit, UTC cutoff, profile key and profile digest on each of the Mermaid Markdown, Graphviz SVG and audit Markdown outputs. Lines 25 and 29–31 retain visibility admission before graph projection, audience-bound attachment review and the pin/profile publication path. Line 59 requires the same profile input and expected graph and audit results in the Python and TypeScript fixtures.

The revision also clarifies numeric lexicographic witness selection at line 14 and distinguishes reducible prerequisites involving displayed child epics from preserved gates of the selected epic at line 22. The accepted graph, refresh and accessibility behavior remains covered at lines 19–25, 39–46 and 56–60.

## Scope

Lines 3 and 50–52 keep #264 as a linked follow-on outside the 13-item M6 release and preserve the existing #258 and #260 dependencies. Released Core and #250/#251 still gate the product viewer. Line 41 retains the separate hosted delivery gate and audience qualification. Plan acceptance and applicable item-specific JIT review are still required before Develop. This is the Codex Design disposition. The native reviewer owns the XPR disposition.
