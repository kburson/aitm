# #187 Design, Plan and JIT review · revision 2

Independent same-provider review by Codex `/root/pickup186` on 2026-11-10. Reviewed all 25 lines of `pickup-v2.md`, SHA-256 `71c47ec4f2a118b41fb856e5b23f40fc51c30160f1d3312400284b816cf8a5c2`. The prior review remains in `pickup-review.md`, SHA-256 `eb1215226fb9dd0547ad9cce01243fc9961994b8235b2fa1dcf60103c265a2ce`. This is a local off-platform review by a separate Codex agent.

## Design verdict

Accepted. Lines 11 and 13 restrict cross-story and legacy conflict sweeps to positive agent turns and retain raw tool intervals for qualification by A03. Line 11 separates the latest positively evidenced pending checkpoint from replay recording, receipt recording and snapshot as-of. Line 9 holds all unsupported superseding receipts and restricts holding a referenced target to matching digest, project and subject. The revised rules fit the delivered #186 input and the parent A02 scope.

## Plan verdict

Changes requested. Line 17 now covers unattended cross-story tools and a delayed batch without positive pending evidence. Add a focused supersession fixture to exercise the newly explicit rule when the target is missing or foreign. The rest of the focused and full verification, real seed parity, hosted proof and source review sequence remains acceptable.

## JIT verdict

Accepted for scope. The predecessor, 3.75-hour estimate, two-file write set and scoped planning publication, trunk pin and live rechecks, independent review, and delivery gates are unchanged from the first review. Develop is gated on the remaining Plan revision.
