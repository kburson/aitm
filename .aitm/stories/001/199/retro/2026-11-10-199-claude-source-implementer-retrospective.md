# AITM #199 Claude source implementer retrospective

I authored the Claude scanner, producer and adapter changes and their adapter regressions for M08b1 as Codex (`/root/claude_revision_source`). The coordinator authored the ScopeState issuance and capture checks, the scope regressions, and the later correction that preserved the existing cross-project handoff test ID.

## Design alignment and corrections

The private collector binds the exact predecessor and successor objects from a successful fixed read. The adapter keys the normalized revision material and the scanner prefix through the actual committing row. The prefix fixture independently computes the digest from the bytes through that row. Timed results and untimed cost-state rows both use their own native ordinal. The earlier timed context still determines the legacy diagnostic location. Ordinary adapter serialization and legacy diagnostics retain their existing shape and behavior. [Accepted pickup](../plan/2026-11-10-199-claude-revision-proof-plan.md)

My first producer tests failed on the missing collector after checking the legacy results. Later tests exposed terminal witnesses that depended on a nonzero excluded baseline or counters available only from an earlier read. I changed the producer to carry each contributor’s span from its original assistant row through its latest accepted counter or stop row. A stop can extend that span even when the counts stay the same. The paired fixtures verified that one terminal row can complete two requests and that the legacy completion still appears when its private witness must be held.

The first overlap repair used the existing active-route overlap evidence. Preflight then found that a foreign or missing parent could escape that check after an ordinary user row cleared the active Agent route. The isolated RED reproduced incorrect witnesses for those two updates and for a child with no positively verified original parent. I retained each nested request’s original verified parent alongside its last accepted counter or stop ordinal for the fixed read. Foreign, missing and initially unverified linkage now keep the terminal proof held. Verified linkage and a same-parent update after a route reset both pass. The nine route cases compare legacy batches and diagnostics for equality. The coordinator’s ScopeState checks apply the routed original owner’s capture entitlement to every contributing span, including another request’s disabled counters. [Independent source verdict](../plan/post-ci-source-review.md)

## Verification and timing

| Evidence | Recorded result |
| --- | --- |
| Final adapter, Claude and scanner suite | 210 passed in 3.92 seconds. Ruff and whitespace passed. |
| Earlier producer-only package replay | 931 passed in 110.25 seconds before the last overlap corrections. |
| Superseded full producer replay | 935 passed and one existing Codex owner-proof test failed in 112.89 seconds. |
| Final producer-only package replay | Stopped at 38% to stabilize the shared review ancestor for the integrated frozen gate. Exit 143 carries no suite verdict. |
| Exact replacement delivery | 948 product and CLI tests and 182 helper tests passed. Signed hosted run 42931801378 attempt 1 and independent Claude Opus 5.5 medium source review passed. |

The two superseded integrated freezes retained their exact trees and partial outputs without suite verdicts. The first hosted candidate then held because the existing handoff test ID was missing. The coordinator restored the original ID and gave the new same-project case its own test name. The replacement retained the producer source, and the signed hosted replay verified all 919 required baseline package test IDs. [Delivery checklist](../plan/delivery-checklist.md) · [Superseded hosted hold](../plan/hosted-first-candidate-hold.json) · [Signed hosted run](https://github.com/kburson/aitm/actions/runs/42931801378/attempts/1)

In the superseded producer replay, the existing Codex owner-proof test failed with “Develop scope requires the current destination owner worktree.” On literal trunk I reproduced that error by changing an unrelated ancestor directory’s ctime during snapshot verification while the source inode and mtime stayed unchanged. The same baseline test passed without the controlled perturbation. The spontaneous failure lacked that trace, so its trigger remains **Unknown**. The exact frozen and hosted replacement suites passed with the scanner custody rule in place. In future concurrent runs I would establish distinct temporary roots before freezing the candidate so fixture setup cannot perturb shared ancestor metadata. [Delivery checklist](../plan/delivery-checklist.md)

The test runtimes above are measured elapsed durations. My active implementation and review time and their breakdown are **Unknown** because I did not record a continuous effort timer.

PR #205 merged into literal `trunk` at 00:39:45 UTC on November 11, 2026, still November 10 in America/Chicago. I verified ordered parents `1452999b2f0f5a90161e39862458029c0084772c` and `a1cde1c364560bed6bca3dcd6f85d021e2fb52f1`, merge commit `2eebb3b7f6b262d3ed4951ffde0cbcb5d3a5ade3`, reviewed tree `9899ff4990510ebc9de09566fb08efcb33f9d112`, and zero source diff between the reviewed head and merge. The four delivered producer files match my signed handoff digests. I have high confidence in the delivered behavior exercised by the fixtures and in the source identity. [PR #205](https://github.com/kburson/aitm/pull/205)

Signed by Codex (`/root/claude_revision_source`), original #199 Claude source implementer, November 10, 2026 (America/Chicago).
