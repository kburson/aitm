# Story #264 Plan same-provider review, round 2

**Decision — REQUEST REVISIONS** for the exact Plan candidate identified below. One residual change is required under SPR R1-F004.

## Review evidence

- Read physical lines 1–121 in full, including blank lines, of `.aitm/stories/002/264/plan/dependency-maps-implementation-plan.md` in the isolated review worktree. Supplied candidate commit `869e0237f13630152fcdec138730398000b7c04d`. Independently computed raw SHA-256 `01d990bf16e400a6de2e56a5d88467b76c4aa3b56583920e913101f92e71aa5f` and rechecked it at submission.
- Reread [SPR round 1](264-plan-spr-1.md) lines 1–36 and read native XPR round 1 reviewer response lines 1–299 and author response lines 1–53 for `review-6ed9de683e9ba54e0a3bee5ed08392b2`. Rechecked the cited accepted Design digest `50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7`.
- Independent Codex reviewer session `/root/formal_design_spr`. Model Unknown. Effort Unknown. Review started 2026-11-12 15:16:01 UTC and was submitted 2026-11-12 15:17:16 UTC.

## SPR dispositions

| Finding | Disposition |
| --- | --- |
| SPR R1-F001 | Resolved. Lines 34–36 and 43–58 assign historical path normalization, eligible header parsing, one lifecycle fold and gap classification to D1. Direct-child declaration failures hold the result and boundary uncertainty stays partial. D5 at line 91 checks the same distinction and withheld readiness. |
| SPR R1-F002 | Resolved. Lines 62–67 and 87–92 specify one canonical pre-admission fixture and exercise both production admission boundaries. Line 75 renders the restricted canary with an attachment profile and checks all shareable surfaces. |
| SPR R1-F003 | Resolved. Line 27 carries separate early static sequencing authorization into JIT and preserves independent static qualification and M6 scope. |
| SPR R1-F004 | Partially resolved. Lines 113–114 now distinguish retained and removed selection. Line 120 conditions hosted fallback on current audience authorization. D7 still needs to specify what happens to the whole prior local view during an unresolved visibility transition. |
| SPR R1-F005 | Resolved. Lines 58, 67, 76 and 82 specify supported Python 3.13 unittest invocations. Lines 82–83 distinguish default hermetic coverage from a requested and passing pinned replay, require both Git objects and Graphviz, and identify the repository input. |

## Required residual change

### SPR R1-F004 — Withdraw the whole prior view during a pending scope transition

Plan line 114 specifically hides prior details while the visibility transition is unresolved. It conditions stale fallback on same-context authorization after a failure, but does not say to hide the prior graph, text view and audit context while the new scope is pending. If a tighter profile takes effect and its snapshot request stalls, an implementation could hide the detail pane while old graph labels, links or counts remain visible until the request completes. That would display data without admission for the current context under Design lines 25 and 39.

Require all prior graph, text, detail and audit surfaces to be withdrawn when their eligibility for the active context is unresolved or lost. Keep selection by ID only if the newly admitted snapshot still allows it, as the revision already provides. Add a D7 check that holds the new snapshot pending and verifies that the old surfaces have already cleared before either success or failure. The same-context authorized stale fallback and the hosted rules at line 120 can stand.

## Native XPR round 1 finding check

| Finding | Disposition in the revised Plan |
| --- | --- |
| XPR R1-F001 | Addressed. Lines 43 and 49–58 name the supported historical location pattern, reuse the reader's eligibility rules and actual sibling journal, and map relevant reader gaps to hold, partial coverage or Unknown. |
| XPR R1-F002 | Addressed. Lines 62–67 and 87–92 define the logical pre-admission fixture, native loaders, profile binding, shared fixture location and parity reruns. |
| XPR R1-F003 | Addressed. Lines 67 and 82–83 move real-pin checks to D4, require explicit repository input and a passing run at both pins, and distinguish an unrequested skip from qualification. |
| XPR R1-F004 | Addressed. Lines 66 and 91 carry the reverse disagreement and excluded-ID case, selected-epic gate and unresolved incoming boundary case through the shared fixture and parity, with the disagreement reported in the admitted audit. |

Lines 3, 11 and 15–29 preserve the linked follow-on outside the accepted 13-item M6 scope, separate static, local and hosted qualification, and require accepted Design, Plan and item-specific JIT before execution. D6a and D6b are independently verifiable slices. This is the Codex Plan disposition. The native reviewer owns the XPR disposition.
