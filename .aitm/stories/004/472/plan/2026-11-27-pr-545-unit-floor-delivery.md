# Package unit-test floor remediation delivery

The usage remediation and shared hosted floor enforcement landed on trunk.
[Linked PR #545](https://github.com/kburson/aitm/pull/545).

| Full collection | Baseline unit / total | Delivered unit / total |
| --- | ---: | ---: |
| Hosted Linux usage with installed CLI pytest smoke | 1,555 / 1,786 | 1,644 / 1,786 |
| macOS usage product matched against the catalog | 1,553 / 1,780 | 1,642 / 1,780 |
| Hosted Core on the trunk candidate | 95 / 99 | 95 / 99 |

Linux includes the systems-integration node
`tools/ci/tests/test_cli_evidence.py::test_usage_console_help`. The separate
installed-wheel smoke step passed. Native and CI helper suites are excluded
from the product collections. The existing line coverage and branch gates
remain applied.

The first exact draft [failed the usage floor](https://github.com/kburson/aitm/actions/runs/46014191384).
A subsequent candidate preserved the ratio but the trusted collector refused
two renamed node IDs. The delivered head retains the original IDs. The
[initial source SAR](2026-11-27-pr-545-sar-r1.md) held the receiver assertions.
The [second review](2026-11-27-pr-545-sar-r2.md) identified additional lineage and
capture gaps, and the focused follow-up identified missing readback after
remote push denial. The final head restores those external contracts and
includes full export-case source context to qualify the producer-only
duplicate branch.

- Base `44ca79c17f80a657d6278cfd82cb988e8a19820a`
- Head `53aa174b979ebbd9bbcf852a5e8cdc6423cb630c`
- Synthetic merge `3b134536ec3bc0b8563e514987644f7cf7249a00`
- Reviewed and delivered tree `1c8d48998cea6f31bce2fdd2066d39f4eab3458f`
- Landing `c3cf04fcb7b210c76c4901b4db0501b3128ee276`
- Observed trunk tip `c3cf04fcb7b210c76c4901b4db0501b3128ee276`

[Repository CI](https://github.com/kburson/aitm/actions/runs/46021361468)
· [Separate Core CI](https://github.com/kburson/aitm/actions/runs/46021361502)
· [Passing Grok 4.7 source SAR](2026-11-27-pr-545-sar.md).

The trusted verifier passed from the exact base at `2026-11-27T15:13:48.566786+00:00`.
Signed artifact `15209280173`, archive digest
`sha256:3fee2811306648a1e0fe075f32e8208830820d99cd133b8e9b3f48bfaba73f5b` and attested subject digest
`9db673cf45be182e7af9dca182358dc8e6c7739f0e0b8ffcea60bd6ff1647205`.

## Sign-off

Codex delivery coordinator under Kendrick's authorization.
Verified the landing's ordered parents and tree against the exact reviewed
candidate and read back the trunk ref. Signed
`2026-11-27T15:15:07.456033+00:00` after that readback.

The Core integration remediation remains tracked independently in
[PR #546](https://github.com/kburson/aitm/pull/546).

## Agent Cost

| Agent and observed turn | Cached input tokens | New input tokens | Output tokens | Verified billed cost |
| --- | ---: | ---: | ---: | --- |
| Codex implementation and coordination | Unknown | Unknown | Unknown | Unknown |
| Grok 4.7 SAR 1 | 8,832 | 52,526 | 14,804 | Unknown |
| Grok 4.7 SAR 2 | 8,832 | 59,502 | 40,673 | Unknown |
| Grok 4.7 focused SAR 2 | 90,880 | 40,258 | 16,955 | Unknown |
| Grok 4.7 SAR 3 | 8,832 | 62,833 | 18,230 | Unknown |
