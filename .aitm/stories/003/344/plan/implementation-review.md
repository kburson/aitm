# #344 independent source review

The independent Codex reviewer passed [PR #346](https://github.com/kburson/aitm/pull/346) on the exact gate-control tree below. The reviewer inspected this tree read-only with separate context. This disposition covers the source and gate-control changes. Hosted suite and trusted verification are separate prerequisites.

| Identity | Value |
| --- | --- |
| Base | `625b5407978675ac3b906990c8bb0713dcae18fd` |
| Head | `4074d31da90f31e5a47445ca3112733672519512` |
| Tested merge | `de6a7a9684415bb56e0068122d01c35eb7e70b85` |
| Reviewed tree | `456a155fbe7d10cb7daafd2bf46f134be78366a8` |

The reviewer held the two earlier heads. The delivered revision compares the isolated base and candidate selections, refuses malformed no-run evidence, expires consumer declarations after changes to shared setup or the canonical invocation, and requires successful attestation before a future push can reuse the full-suite stamp. Restore checks the exact key, PR, base, target, prior workflow blob, successful run and attested job step. The prior head's workflow bytes must match the trusted base. The reviewer exercised restore with trusted workflow bytes, changed bytes, a different target and a cancelled run using a mocked provider API.

Both mapped declarations were checked against the replacement tree. The legacy base selector chose full validation for the control-changing PR. All 228 exact-head CI helper tests passed in independent replay. Actionlint and the Git whitespace check passed. The implementation checkout measured 1,036 of 1,109 policy helper lines covered (93.42%) on the prior revision with the same Python changes. The final hosted attempt supplies the release-gate coverage.

This change uses an exact-key GitHub Actions artifact for the stamp. Publication follows the signed evidence in the attestation job, and lookup requires the producer's completed successful canonical run. An older, failed or superseded attempt cannot act as a full result for a later attempt.

[Final exact-head hosted run](https://github.com/kburson/aitm/actions/runs/43877292106)
