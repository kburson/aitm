# Verified integration correction for #500

[PR #566](https://github.com/kburson/aitm/pull/566) landed on the integration ref.
It releases the exact evidence-only generation without authored sync or planning
publication. The installed proof confirms that the old lease remains fenced
and a new planning holder can bind after release.

- Base `16560373b2b7056117627d2c23a0f6f5487cd472`
- Head `ef090350e544c77473bd3949ed35030e5d41230b`
- Synthetic merge `758138ba442597c326e73914e026d29f0360e1d8`
- Reviewed and landed tree `d6b2490cefa6f70edbb458564795ab67af3c7ddf`
- Landing `a0cf28c88c4315b478343e4b557ee3b21e0771c4` at `2026-11-27T23:21:05Z`

[Hosted and trusted verification](../plan/2026-11-27-pr-566-ef090350-verification.md) and the
[independent Grok 4.7 review](../plan/2026-11-27-pr-566-ef090350-source-sar.md) passed before admission.
The live target, ordered parents, landed tree, and native Linked PR were verified.
#500 stays In review pending separate exact aggregate admission and trunk verification.

## Agent Cost

| Agent and observed work | Cached input tokens | New input tokens | Output tokens | Verified billed cost |
| --- | ---: | ---: | ---: | --- |
| Codex correction and coordination | Unknown | Unknown | Unknown | Unknown |
| Grok 4.7 candidate `ef090350` | 2,432 | 8,613 | 3,543 | Unknown |
