# Continuous usage collector source delivery

[Protected trunk PR #97](https://github.com/kburson/aitm/pull/97) merged at 2026-11-09T22:06:39Z.

| Evidence | Exact value |
| --- | --- |
| Base | `4e896e049370df58fe870dc80790401056218b97` |
| Independently reviewed head | `00ccef89e1e0bd541981b4a367d005f699c63769` |
| Protected trunk merge | `c2f3582d07d0f3dfeb680ab565fb3a5c5339d2ac` |
| Reviewed and delivered tree | `f1aecf3ae46719f508f8ff6c88fc488b467060d0` |

Independent Codex Astra/high whole-branch source review passed specification and quality. All 39 changed paths belong to the standalone usage package. The exact integration passed 491 locked tests, Ruff and Git diff checks. The offline installed wheel passed 53 U10/U12 cases. Independent verification matched all 19 wheel package entries to the exact source bytes.

The source release is available on trunk. [#96 live project-Mac qualification](../../96/story.md) remains the gate for closing #83 and starting C01. The same collector and ledger are intended to remain in service through later Core adoption.

## Desktop carrier repair

[Protected trunk PR #98](https://github.com/kburson/aitm/pull/98) merged at 2026-11-09T22:29:23Z.

| Evidence | Exact value |
| --- | --- |
| Previous protected release | `c2f3582d07d0f3dfeb680ab565fb3a5c5339d2ac` |
| Independently reviewed repair head | `699bd901ffd761dfaf28eeac0be25d04791cb416` |
| Protected trunk merge | `e65c86ba4c7d19e7844a5d23a3aa33446a885f4c` |
| Reviewed and delivered tree | `15a22e275e20407bb6234bc5650b38e2b6737514` |

The repaired tree passed 501 locked tests, Ruff, lock and diff checks, independent specification and quality review, and a read-only replay of the original native boundary evidence. The replay matched the exact pending command, native output and following request. [#96](../../96/story.md) still requires fresh installed qualification on the repaired release.

## Claude startup scanner repair

[Protected trunk PR #99](https://github.com/kburson/aitm/pull/99) merged at 2026-11-09T23:00:50Z.

| Evidence | Exact value |
| --- | --- |
| Previous protected release | `e65c86ba4c7d19e7844a5d23a3aa33446a885f4c` |
| Independently reviewed repair head | `239a863c97bd7de3af66934f41fffcdacab985fe` |
| Protected trunk merge | `f80f22645e2008c4cac9dc6e4003640bba976b5f` |
| Reviewed and delivered tree | `418b1d6e681f65a0377472f4392be87076b6bad4` |

Exact independent source review, 530 locked tests and static verification passed. The isolated repaired-wheel diagnostic admitted one intended measured request from unchanged native input in both replay orders, with zero outside-scope observations. The 13 retained native startup chains matched. [#96](../../96/story.md) requires fresh installed qualification before activation closes.
