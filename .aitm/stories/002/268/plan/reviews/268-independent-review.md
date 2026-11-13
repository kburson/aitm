# #268 independent review of the macOS/APFS spike

**Disposition — Accepted as evidence of the bounded synthetic #268 trial.** The one authorized job demonstrated a separate worker principal, scoped receipt custody and external outcome checks for the fixed three-case catalog on the observed hosted runner. Publish the result with the limits below. Production qualification for #146 remains blocked. [#268](https://github.com/kburson/aitm/issues/268) · [Reviewed #146 replan](https://github.com/kburson/aitm/blob/10992dc57915f84adafcb5ffb90f1ab04c70c856/.aitm/stories/001/146/plan/2026-11-12-146-trusted-observation-replan.md)

## Reviewed identity and custody

| Evidence | Verified value |
| --- | --- |
| Repository, trigger and ref | `kburson/aitm`, same-repository `push`, `refs/heads/codex/spike-268-macos-observation` |
| Source commit and tree | `8a7c7ea8c77046371cee6bf282b7b2dd4c869535` / `1a6ab37ad05b1c0b82d2b1ba84926c6974da614d` |
| Source parent | `766504a02aaeb9dda339d588172dd7d5bdbd2b3f` |
| Run, attempt and job | `43349372876`, attempt `1`, one successful job `131636416255` (`observation`) |
| Runner and toolchain | GitHub-hosted `macos-26`, macOS `26.7.2` arm64, image `20261102.0473.1`, Python `3.15.2` recorded by the controller |
| Artifact | `14002573302`, `spike-268-43349372876-a1`, 1,712 bytes |
| Artifact ZIP SHA-256 | `e39f55b8e26da312f3dedb6e122a9512f72b21ced9d360b660fe6fb3c8ab461b` |
| Controller receipt SHA-256 | `88815f2bbc656de8a047e0c36f3d0a8459c3e934fe1bed929ae93dfa1d19ab7e` |
| Controller SHA-256 | `be3c16d59d962e6c9d3467ba3131da40a90655f288d44621c937eda548004d05` |
| Fixture SHA-256 | `ab5a90bc9a11b1c13c27eaef03bd7992622467e54b380be2ef7d440535d54107` |
| Workflow SHA-256 | `20ef521e3be2ef71bc4a4c276eb69a6b3df96f5ab36ca47f91453a3b72c65424` |
| Canonical catalog SHA-256 | `cc268e5538d5decd5b3a9a7865760cc41c202e6793fc57fb97ba861bb39f10bc` |
| Canonical policy SHA-256 | `813929add2dc318d2dbd6afe59474bb4ea559280c0ea08f143f03915cffe4c46` |

I queried the live GitHub run, attempt, jobs, artifact and commit records and read the job log from the job endpoint. GitHub listed one workflow run for this branch and one job for this attempt. I downloaded the artifact in memory and confirmed byte equality with the retained ZIP, its published GitHub digest, its sole `receipt.json` entry with Unix mode `0600`, and the extracted receipt digest printed by the controller in the job log. I read all three changed source files at the exact commit and independently recomputed their hashes, the canonical catalog, policy and assignment hashes, and the expected stdout hashes for all seven receipt rows. The workflow pins the checkout and upload actions, limits the job to the designated repository, branch and first push attempt, checks the checkout head, declares `contents: read`, disables checkout credential persistence and retains the staged receipt. The reviewed tree adds only the controller, fixture and spike workflow. [Commit](https://github.com/kburson/aitm/commit/8a7c7ea8c77046371cee6bf282b7b2dd4c869535) · [Run](https://github.com/kburson/aitm/actions/runs/43349372876) · [Job](https://github.com/kburson/aitm/actions/runs/43349372876/job/131636416255) · [Artifact](https://github.com/kburson/aitm/actions/runs/43349372876/artifacts/14002573302)

## Boundary observed on this job

- Before fixture execution, the controller resolved the fixture directory's device and required `diskutil` to report APFS. `sudo` and `id` observed controller UID `501` and `nobody` UID `4294967294`. The worker groups were `4294967294`, `12`, `61`, `100` and `701`, excluding the checked admin and root group IDs. One noninteractive elevation probe failed. The worker environment probe observed only `HOME`, `LC_ALL`, `PATH` and `TMPDIR`.
- The controller copied the fixed fixture into its own directory and set the copy to `0444`. Worker readability and non-writability were checked with `test`. Worker attempts to read and overwrite the private marker failed, and the controller verified the marker content and fixture digest after execution. The controller checked its private receipt directory for mode `0700` and controller ownership. Worker attempts to create the future private and staged receipt files failed, and the controller verified that the files had stayed absent.
- After the fixture calls, the controller created both receipt files exclusively and set mode `0600`. It required unsuccessful worker read probes against both completed files before logging the receipt digest. The successful job and matching artifact establish that this code path completed. The JSON records the two pre-creation denials but has no dedicated fields for the post-creation read probes. Source shows the staging directory was created with requested mode `0700` and tested at the staged receipt path. The explicit owner and mode assertion covers the private directory only. The probes cover these named paths and operations. The fixture write check was a permission test, and there was no post-creation receipt overwrite test or comprehensive audit of credentials, accessible storage or privilege paths. [Controller source](https://github.com/kburson/aitm/blob/8a7c7ea8c77046371cee6bf282b7b2dd4c869535/.github/spikes/268/controller.py)

## Observation matrix

The trusted controller owns the case catalog, assignments and expected output. It invokes the fixed shell fixture as the worker and evaluates each invocation using its captured exit code and exact stdout bytes. The receipt's positive rows cover all assigned cases. The negative fixture returns exit `0` with deliberate wrong output, which the external controller marks `fail` in both modes.

| Check | Full | Selected |
| --- | --- | --- |
| Exact assignment | `alpha`, `beta`, `gamma` | `alpha`, `beta` |
| Assignment SHA-256 | `a3e185260009ab5be7bb16f3bed296075f27322fb87d99209710a28ef3e8d99e` | `138bf4722f7ae17122c7282d0eb156499d349940e129bd4cdf27c8ffdcbb3d25` |
| Actual normal subprocesses | `alpha`, `beta`, `gamma` pass | `alpha`, `beta` pass. `gamma` stays `unobserved`. |
| Actual negative subprocess plus omitted evidence | `alpha` fails. `beta` and `gamma` are missing. Overall `fail`, incomplete evidence. | `alpha` fails. `beta` is missing. `gamma` stays `unobserved`. Overall `fail`, incomplete evidence. |
| Removed `gamma` catalog entry | Refused for inventory identity mismatch | Refused for inventory identity mismatch |
| Same-shape worker result | Refused for lack of authority | Refused for lack of authority |
| Claimed pass with empty observations | Refused with all assigned cases missing | Refused with both assigned cases missing. `gamma` stays `unobserved`. |
| Stale result at attempt `0` | Refused for attempt mismatch | Refused for attempt mismatch |

The five normal and two negative fixture subprocesses were real calls on the hosted worker. The missing siblings were intentionally omitted from the negative observation map. No sibling process crashed or lost finalization in that row. The four refusal rows in each mode were in-memory controller checks. The harness constructed the reduced catalog, worker-attributed result, claimed pass and stale attempt, without accepting an on-disk worker result or a real prior-attempt artifact. The `controller-observed` authority string is a model input. In the missing-catalog check, the controller assessed the reduced catalog after executing the fixed assignment from its own source. This establishes an identity check for the supplied model input. A live external inventory ingestion and refusal before dispatch remain untested. [Controller assessment](https://github.com/kburson/aitm/blob/8a7c7ea8c77046371cee6bf282b7b2dd4c869535/.github/spikes/268/controller.py#L133-L182) · [Fixture](https://github.com/kburson/aitm/blob/8a7c7ea8c77046371cee6bf282b7b2dd4c869535/.github/spikes/268/fixture.sh)

## Qualification and issue disposition

The GitHub artifact and receipt hashes bind bytes to this evidence set. The job provides no cryptographic per-test attestation. The native probe demonstrates launching a command under the separate principal. The fixture provides no required native child activity or independently verified child coverage. Arbitrary pytest collection, including dynamic inventory completeness, per-obligation execution, live receipt authentication and hostile-code containment remain unqualified. These omissions keep the production observation contract for #146 open. The existing #103 PR gate continues to govern. [#144 requirements](https://github.com/kburson/aitm/blob/24f8eaafe600aa6e947cc0ed8015d38db72fda43/.aitm/stories/001/144/design/2026-11-11-144-trusted-pytest-observation-design.md) · [#103](https://github.com/kburson/aitm/issues/103)

Live readback confirmed #268 as the native sub-issue of #146 and open at Rank 50 in Project 24 `In review`. #146 remains open at Rank 50, `Backlog / BLOCKED`, with historical blockers #144 and #145 and open dependents #149 and #168. #148 and #267 remain open at Rank 60, `Backlog / BLOCKED`. Their issue bodies record the owner's pickup hold until #146 is resolved. I reviewed the single completed run and performed read-only evidence checks. [#146](https://github.com/kburson/aitm/issues/146) · [#148](https://github.com/kburson/aitm/issues/148) · [#267](https://github.com/kburson/aitm/issues/267)

Signed **Codex / sar268**, independent evidence reviewer.
