# Core unit-test floor on the #472 integration branch

[Linked PR #546](https://github.com/kburson/aitm/pull/546) restored Core's
unit floor with separate evidence-preserving tests. The exact branch for the
C08 pickup now qualifies in both hosted workflows.

| Full collection | Unit | Integration | Total |
| --- | ---: | ---: | ---: |
| Core on original integration base | 106 | 71 | 177 |
| Core delivered | 424 | 36 | 460 |
| Linux usage delivered, including the installed CLI smoke | 1,644 | 142 | 1,786 |
| macOS usage product catalog | 1,642 | 138 | 1,780 |

[Initial negative Core qualification](https://github.com/kburson/aitm/actions/runs/46014565949)
· [Independent rework verdict](2026-11-27-pr-546-sar-r1.md)
· [Corrected 178/204 floor rejection](https://github.com/kburson/aitm/actions/runs/46018320835)
· [Passing Grok 4.7 source SAR](2026-11-27-pr-546-sar.md).

The corrected suite retained the external contracts. With Kendrick's scope
approval, the additional independent unit nodes cover existing committed
policy, planning history, transaction authority, execution and review evidence
decisions. The second SAR required restoring all original C05 live Git test IDs. All 19
are present on the final head. The separate pytest tooling test is outside the
product inventory and ran in Core CI. No production source changed. The integration head contains
the same usage and repository-gate source as the [reviewed #545 delivery](2026-11-27-pr-545-unit-floor-delivery.md).

- Base `8d83fccae4fb101a9740257711588f46575c5b45`
- Head `d1a736f0d7ed0dee9c0bfcc3e19c58aa186b87f6`
- Synthetic merge `e78711ccfd14aed558e9e0ecf661ebf032e8a833`
- Reviewed and landed tree `6f29cfa50b37ea2860acf438864164a2ddb1a7c7`
- Landing `18cddc2f2715cf19a2d27d8a8e78fc00c23f5f5d`
- Observed integration tip `18cddc2f2715cf19a2d27d8a8e78fc00c23f5f5d`

[Repository CI](https://github.com/kburson/aitm/actions/runs/46023588836)
· [Separate Core CI](https://github.com/kburson/aitm/actions/runs/46023588729).

The trusted verifier passed from the exact integration base at
`2026-11-27T15:25:25.916452+00:00`. Signed artifact `15212145737`,
archive digest `sha256:dc9a3c244e802f83c1b3377fe550d2905ca0b29fca09a8ddc9391346ce83b07b` and attested subject digest
`85cd2079707f546e90ca210f1690ebbb6481f28d2b0500fde6d81a761ce2c666`.

## Sign-off

Codex delivery coordinator under Kendrick's authorization. The observed
integration ref contains the exact reviewed merge parents and tree. The four
prior sibling landings remain ancestors, with their original merge receipts.
Signed `2026-11-27T15:26:27.064623+00:00` after the landing readback.

## Agent Cost

| Agent and observed turn | Cached input tokens | New input tokens | Output tokens | Verified billed cost |
| --- | ---: | ---: | ---: | --- |
| Codex implementation and coordination | Unknown | Unknown | Unknown | Unknown |
| Grok 4.7 SAR 1 | 8,832 | 70,471 | 13,238 | Unknown |
| Grok 4.7 SAR 2 | 8,832 | 43,841 | 11,695 | Unknown |
| Grok 4.7 SAR 3 | 1,664 | 64,975 | 12,351 | Unknown |
