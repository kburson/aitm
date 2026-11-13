# #267 independent advisory evidence review

**Verdict: ACCEPTED.** The exact measurement report, recipe and supporting evidence satisfy #267 for advisory use. No blocking findings.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the predeclared plan before the experiments and independently reconciled the final outputs with retained local receipts. The measurement implementer ran the test matrix. I used a separate checker to read the raw data and reproduce the result sets.

## Reviewed identities

- Source commit `766504a02aaeb9dda339d588172dd7d5bdbd2b3f` and tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`.
- Predeclared plan SHA-256 `59ed77a36a4252ea7435ec1a3134ed4579d7ff80d3c9251206a56709ce3291e7`.
- Independent plan review SHA-256 `2674df2ce472839fea0ff810eb03b6d2f0667013d2855de97caa411d513ca930`.
- `report.md` SHA-256 `6c45e1c5cbf8e65385c934cb947394dacddcfbeb4e7093b2b7a405588b19b5a3`.
- `evidence.json` SHA-256 `7edc9e3e109786b5fb00eb11961dd3c4947898886642196e94e4d005cfff11c5`.
- `recipe.md` SHA-256 `c242d03aa4f8dcf40a44790ca9025ddc2a1d03270f8f51e1b0ef9a8d5bd07426`.
- `raw-manifest.sha256` SHA-256 `eeda386c6b9b4486f631724b83e27e9565ba0b177b940d02fc0a0148b776ca41`.
- `publication.sha256` SHA-256 `0073c31fc0cc5e726e27546237822e32219aece401e379b5b3f6125a1f16545f`.

## Independent checks

Both disposable checkouts resolved to the pinned revision and tree. The measured environment reported Darwin 26.6.2 arm64, APFS, Python 3.13.9, pytest 9.2.0, coverage 7.17.2, uv 0.10.6, and pytest-testmon 2.3.0. The recipe scripts passed shell syntax checks. All 16 publication and 158 retained raw-file digests matched. I regenerated the report byte for byte from the reviewed JSON. The inspected public artifacts contained no private scratch or user-home paths.

The unchanged reference collected 1,412 obligations, 196 CI helper and 1,216 product/CLI. The product reference retained the complete traceback of one unchanged native setup failure. Its exact node passed three isolated reruns and the clean full no-select training run. The latter observed the same 1,412 IDs. The evidence retains this nondeterminism and keeps the original reference denominator. The suspected ancestor-churn cause remains a hypothesis.

I independently recomputed the per-node phase outcomes, child labels and exits, wall times, source-patch hashes, Testmon history and expected/observed set differences. I matched warm Testmon databases' recorded executions to frozen unchanged history, checked that the cold case used new history, and used actual pytest session items to count Testmon omissions. For #143 I checked advisory provenance, exact plan/run equality and canonical plan digest, actual execution counts and exit statuses.

| Seed | Independent result |
| --- | --- |
| CLI | Serial recorded 18 pass-to-call failures. The actual #143 full fallback executed all 1,412, reproduced the 18 failures and recorded both required child labels with exit 0. Warm Testmon selected 136, caught eight of the failures, and missed the predeclared CLI smoke and nine other observed failures. |
| Non-code | The serial reference recorded zero pass-to-failure deltas. #143 suggested all 1,412 due conservative import uncertainty. Warm Testmon selected zero. |
| Uncertain fixture | The serial reference confirmed one failure at the predeclared Grok fixture ID. #143 full fallback included it. Warm Testmon selected zero and missed it. |
| Unavailable history | #143 plan and run exited 2 with zero execution because the base was unresolved. Cold Testmon selected all 1,412 and reproduced the 18 CLI failures. |

The repeatable recipe and sanitized evidence state the host and fixture conditions, the separate training and execution costs, the exact omitted and extra IDs, and the bounds of a single local measurement. The reports carry local advisory provenance. The existing #103 merge controls remain in effect. [#267](https://github.com/kburson/aitm/issues/267) · [#103](https://github.com/kburson/aitm/issues/103)
