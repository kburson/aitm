# #158 independent SPR of endpoint measurements

Reviewer `codex-collaboration:/root/prep139`. Author `codex-collaboration:/root/spike158`. Reviewed the exact bounded M08/M09 endpoint evidence in `/tmp/aitm-158-spike.FKrlkZjB` against the accepted #158 planning bytes at `b62000a647dccd1343573deaddf436ca179a5177`.

| File | Physical lines read | Raw SHA-256 |
| --- | ---: | --- |
| `github-merge-fence-spike.md` | 1–56 | `360f23907cef25a4501b9d104fd1f815546bb2ddaa6e5249a48e9722b30b5454` |
| `github-merge-fence-rules.json` | 1–416 | `cba8161cc2cde8a94d2c228ba637d1dd2ff536c4e2b984975d8b8abf2714c8b2` |
| `raw-sha256.txt` | 1–14 | `85e55f31a65b30e569aef3d2592aa061984ad95e7e24afa0222df61951d42976` |
| `offline-replay.txt` | 1–39 | `1cf17a6f147dac2ccc5c9193b097951af2d405d165f3c97e241917f601e773d2` |

## Evidence checked

- Verified all 14 files against the raw manifest. Parsed all 249 observation lines and all nine preflight lines. Reconciled the 24 rule observations with the raw transcript by GitHub request ID, route, selected API version, timestamp, status and response. The observed OAuth owner had admin and push rights. The private fixture returned 403 for rulesets and legacy protection, branch readback showed protection disabled, and the App-installation read required GitHub App authorization. The artifact records the account plan as undisclosed and the dedicated App policy as unconfigured.
- Verified exactly two synchronous merge PUTs under version `2026-03-10`, one per case, with the recorded `sha` and method `merge`. Both returned terminal responses. The transcript contains no async merge request. GitHub documents the request SHA as the expected head and exposes no expected base OID or stop version for this operation. [GitHub synchronous PR merge contract](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#merge-a-pull-request)
- M08 transcript lines 81–122 record the two test merges, a same-tree fast-forward of the head, HTTP 409 request `CD2C:11366D:5A1C33:11807AB:6AF39805`, and the original target in REST and Git after the attempt. PR #1 remained open and unmerged. The bundle independently yields reserved test `92d5284b32849b493d936d662980d39ba5535ee0` and refreshed test `34d870350098de40862ecd271d4d8fb87b42e761`. Their second parents are the old and new head, respectively, and both use tree `6eff4325a02cdfc98e09e55852643092492f4405`.
- M09 transcript lines 153–232 record the original test merge, the ancestor advance, the host test merge on the changed target, and HTTP 200 request `CEB9:88BDA:615BBF:12EBA1C:6AF398B8`. The immediate pre-dispatch REST and Git target reads both identify `7c83794ccc8eede0394abca3bc58a4c1e4bc910a`. PR #2 closed as merged. GraphQL, REST ref readback, Git and the merge response agree on landed commit `685e186e4a087ed66cad085f0d2781a5163db967`. The first parent is the intervening base and the second is original head `e8ba388261eaceac49013f1fe67ec2ecd42af78b`. Reserved test, changed-base test and landed commit all use tree `f95616d2421689b30c37666fdce6f387ddadada6`. The original reservation required first parent `ac75c69f3933386fdc156664d71599fd1a96c930`.
- Replayed the pack directly from the exact bundle bytes in memory. Checked the pack checksum and reconstructed 18 object hashes and 21 ref targets. The five test or landed merge commits independently yield the reported ordered parents and tree IDs. Also ran read-only `git bundle verify` and Git object readback from the retained bare replay. Raw custody was unchanged.
- Authenticated fixture GETs during review returned repository ID `1453246444`, private visibility, the original trunk and M08 target, the landed M09 target, and the PR states above. The fixture still existed at that readback. The reviewed report records teardown as a separately authorized action pending verification.

## Scope of acceptance

Accept the exact endpoint evidence and its stated limitation. The stale head was refused and the moved-base case merged in the private owner-token fixture. The accepted App-backed matrix remains unrun because fixture ruleset access and the dedicated roles were unavailable. #158 remains pickup held and #159 remains blocked on #158 and #157. The evidence establishes the outcome of these two bounded controls.

## Decision

accepted
