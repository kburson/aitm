# Independent review: AITM PR #245

**Verdict: PASS.** I found no blocking findings. This exact candidate is eligible under the existing #103 gate. Before merge, confirm that trunk is still at the reviewed base (F4).

## Reviewed identities

| Item | Value |
|---|---|
| Base (literal target trunk) | `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5` |
| PR head | `65a9d70e01def9b81307773975ae8ea7ec86da98` |
| Tested (GitHub test merge) | `ebd6341b9d5b1f52c836ab5199565dec45199a4f` |
| Tested tree | `1b4859c42c61b379e68a5bd20af5d077a54f209b` |
| Workflow blob, base → candidate | `96424d88…` → `7314705a…` (matches the diff index line) |
| Canonical run | `43085566452` attempt 1, all six jobs passed |
| Signed subject / artifact | `f76551ad…` / `sha256:49569047…` (id `13886472350`) |

The signed payload's `base`, `head`, `tested`, `tree`, `run` and `attempt` all match the identities above. I reviewed only the supplied evidence and modified nothing.

## Assessment against the requested checks

- **Scope is clean.** The patch touches only `.github/workflows/ci.yml`, and only the two pytest invocations: `ci.yml:71-75` (`python-base`) and `ci.yml:167-171` (`python`). The candidate blob is reported byte-identical to the #231 `d1916b81` source patch. Nothing touches #197 or #159 surfaces, so #197 stays on hold and #159 stays blocked.
- **Isolation from system temp is correct.** `--basetemp` moves pytest's `tmp_path`, `tmp_path_factory` and `tmpdir` roots off `/var/folders/…` and onto `$RUNNER_TEMP`.
  - On macOS `$RUNNER_TEMP` sits under `/Users/runner/work/_temp`, which avoids the `/var` → `/private/var` symlink for fixture paths.
  - The fixture filesystem is now the same one that `capability.json` already asserts is APFS (`ci.yml:144-149`). This is a small improvement in evidence fidelity.
- **Isolation from evidence and coverage output is correct.** The fixture roots `aitm-base-fixtures.*` and `aitm-python-fixtures.*` are siblings of `$out`, not inside it:
  - they cannot leak into the uploaded `…/evidence/` directories (`ci.yml:88`, `ci.yml:225`);
  - they cannot collide with `COVERAGE_FILE="$out/.product"` or with child coverage data files.
- **The basetemp deletion hazard is avoided.** pytest deletes an existing `--basetemp` before use. Pointing it at a not-yet-existing `pytest` subdirectory of a fresh `mktemp -d` means pytest can never delete `$out`, `$RUNNER_TEMP`, or the mktemp root. The path is never cwd or an ancestor of cwd, which pytest would reject anyway.
- **Path handling and portability are sound.**
  - All expansions are quoted.
  - The template has eight trailing `X`s and works with BSD `mktemp -d` on `macos-26`.
  - The default `bash -eo pipefail` shell fails the step if `fixtures=$(mktemp …)` fails.
  - Absolute basetemp works with `--rootdir "$root"` and with the `cd packages/aitm-usage` at `ci.yml:162`.
- **Exact job inputs are preserved.**
  - Base identity fields (`ci.yml:78-83`) and expected-base fields (`ci.yml:137-142`) are unchanged.
  - Test selection, `-p pytest_evidence`, `--junitxml`, `--durations` and `COVERAGE_FILE` are unchanged.
  - `-q` moved position on `ci.yml:169`, which has no semantic effect.
- **No obligations are weakened.** These controls are all untouched:
  - inventory, outcomes, product inventory, product and helper coverage, child evidence;
  - the capability gate, the wheel smoke test (`ci.yml:201-220`);
  - custody checks (`ci.yml:309-343`), the collector schema, archive validation, the attestation, and `overwrite: false`.
- **Signed result is consistent.**
  - `passed: true` with no failures.
  - Child labels `cli-help` and `service-one-shot` are present.
  - The wheel digest is recorded.
- **Timing qualifies.** The `python` job took 374 s against the 480 s limit (`ci.yml:94`), leaving about 106 s (22 %) of headroom.

## Findings (all non-blocking)

**F1 (Low): the signed excerpt does not show `controls` or `timings`.**
The supplied "verified" payload omits `controls.workflow` and `timings.hosted_seconds`. The 374 s figure and the `7314705a` workflow blob therefore come from your prose, not from the signed excerpt.
- The workflow is still bound transitively, because the signed `tree` `1b4859c` determines the workflow blob.
- **Action:** confirm that `git rev-parse 1b4859c:.github/workflows/ci.yml` equals `7314705a…`.
- **Action:** confirm that the signed `timings.hosted_seconds` equals 374, and record `timings.cache` (warm or cold).

**F2 (Low): timing qualification rests on one sample.**
There is a single attempt with about 106 s of headroom, and the cache state is unknown. If that run had a warm uv cache (`ci.yml:197-198`), a cold-cache run will be slower. This does not block the change, but note it for #197 and #159 planning.

**F3 (Info): the test counts differ by one (1070 vs 1071).**
This is consistent with the candidate lane also running `tools/ci/tests/test_cli_evidence.py` (`ci.yml:171`), which the base lane does not run (`ci.yml:75`). That difference already existed and is not caused by this patch, since the patch adds no tests.
- **Optional:** confirm that the last trunk run shows the same +1 delta.
- **Optional:** confirm that product `num_statements` (11604) matches trunk. A match would rule out fixture files entering coverage measurement.

**F4 (Info): trunk may have moved.**
Eligibility is tied to base `b0f8ac79`. If trunk has advanced since run `43085566452`, the test merge `ebd6341b` is stale, and this attestation does not cover the new merge. Re-run before merge in that case.

**F5 (Info): the helper suite does not get `--basetemp`.**
The pytest run at `ci.yml:193-196` still uses system temp. This matches the #231 source patch and the owner's scope, so it is not a defect here. Any follow-up belongs in a separate change.

**F6 (Info): macOS socket path length.**
The new fixture prefix (about 63 characters before the per-test directory) is shorter than the default `/private/var/folders/…/pytest-of-runner/pytest-N/` prefix. The macOS 104-byte `AF_UNIX` limit is no tighter than before, and the hosted run confirms this.
