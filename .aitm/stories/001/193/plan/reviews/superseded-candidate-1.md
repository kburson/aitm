# #193 delivery checklist

Attempt 1. Implementer is the assigned Codex agent. Closure owner is the coordinating Codex agent. Target trunk. Pickup base `fec3d8f685fd1d133bb9797d47c02552805e6bc1`. Predecessors #191, #192 are delivered. File ownership is defined by the exact pickup.

- [x] [Design, Plan and JIT](jit.md) and [independent acceptance](jit-review.md).
- [ ] Local verification, applicable hosted CI and independent source acceptance.
- [ ] Verified merge, implementing-agent sign-off, and issue/Project closure.

## Candidate 1

[Source PR #222](https://github.com/kburson/aitm/pull/222) targets trunk base `fec3d8f685fd1d133bb9797d47c02552805e6bc1`. Exact head `937d38b15682945d48a7f958fe896ab5b0ec58b8` and tree `ec5f072082adc5010c2326f7e3d8c77a85fc3a05` contain only the reviewed story paths. Focused dashboard tests, the full dashboard suite, Ruff, and whitespace checks passed on the clean checkout.

- [ ] [Hosted CI](https://github.com/kburson/aitm/actions/runs/42965221943), delivered verifier and independent source review.

## B02 clean-reader qualification

The independently cloned Git reader was detached at the delivered source and was clean before and after the work. Historical and post-pilot pins were read using the two documented CLI commands and exact UTC cutoffs. Two historical builds gave identical snapshot, validation and HTML bytes. The validation artifacts bind their snapshots. Only normalized snapshot fields were embedded. The rendered files have hashed inline assets and no remote asset references.

At 1280 and 390 CSS pixels, both pinned views opened in Chrome offline with zero automatic web requests and no page exceptions. Epic, State and Actual coverage filters and both drilldowns passed. #111 preserved its estimate, partial Actual, implementation elapsed, Unknown all-phase elapsed, timing watermark and basis. #100 preserved direct versus descendant Actual and observed working wall time. The later view exposed one attributable #191 pilot contribution, partial Actual and an Unknown owner wait with the missing-response reason. Cost remained Unknown in both views. Refresh preserved exact historical reproducibility.

| View | Planning commit | As-of UTC | Snapshot SHA-256 | Validation SHA-256 | HTML SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Historical backfill | `17761cc1928fd916cf32a9c078d4a742bfcb32b8` | `2026-11-11T04:23:16Z` | `e46da18999caf132dcc451e9ae8e7b12dd5517a49113f85931c48d93c5e3772a` | `3497de8b8d908759aa0e62bd313de3bced70e4fba6bd82e6aaa2dfa227821ab6` | `19995aa7a55e636a9c58a40a04942cc7e512f349661b26c27839550ff5e83e1c` |
| Live capture pilot | `527dce9bd7847181a67dc23c6bb2c9844f15c87f` | `2026-11-11T04:45:27Z` | `94a2c286b3de1bce4e49eb38cc1b35128ce470de83c644e65f843809a33f6fe9` | `80a1adbe65515b073b01aa49bf02c5e2982b93a8af32f75527fdff724afa7803` | `4b3c1143bdedb532ddafc51821e499c3fe483d71573fcdebbc68c75451a40fb7` |

The later view contains receipt SHA-256 `8d3bf226f4e47fac1153dad67b4ecae5fdbabb24ccbc73ebaf8ed9ae7d13076c` and 4,891 ms of Actual through `2026-11-11T04:43:35.855000Z`. Both JSON and HTML remained local.
