# AITM #138 independent source review 1

Reviewer: independent Codex source-review agent `/root/source138`; not the source author.

Source verdict: accepted with one nonblocking P3 finding. No P0/P1/P2 findings. This is a source-review disposition only. Terminal acceptance remains pending the coordinator's authenticated exact-candidate hosted evidence and required delivery dispositions. This record does not authorize merge.

## Exact review scope

- Candidate head: `b5c9cc0d9b586d7c22324dd9b660d522f7751484`.
- Candidate tree independently resolved: `4d16a3123bc79abc07797b43a461a8d0cb03921a`.
- Literal `trunk` comparison base: `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`.
- Full diff read: `tools/ci/tia/baseline.py` (1,098 added lines) and `tools/ci/tests/test_tia_baseline.py` (717 added lines), with no other changed paths.
- Read the accepted #138 design, own Plan and JIT; draft `private review workspace`; and the private historical projection/replay script.
- Tests and probes used immutable Git-object exports in `private review workspace`. No source-worktree, board, remote, or PR mutation.

## Finding

### P3 — Categorize malformed helper-command parsing errors

Location: `tools/ci/tia/baseline.py:776` (`argv = shlex.split(command)`).

The accepted Plan and public function promise `ValueError` with a stable reason category for malformed inputs. Starting with the complete passing synthetic pair, setting `roles.helper_collection.command` to a single double-quote causes the public `build_baseline` call to raise `ValueError: No closing quotation`. This bypasses the module's `helper:`/`input:` category because the public exception wrapper deliberately does not catch ordinary `ValueError`. A dangling escape similarly comes directly from the shell parser. The input is safely refused, so this is a nonblocking diagnostic-contract issue, not evidence acceptance or trust escalation.

Reproduction against the exact exported candidate:

```python
import runpy
m = runpy.run_path("tools/ci/tests/test_tia_baseline.py")
proof = m["proof"].__wrapped__()
proof[0]["roles"]["helper_collection"]["command"] = '"'
m["project"](proof)
# ValueError: No closing quotation
```

Suggested change: catch `ValueError` immediately around `shlex.split` and re-raise a stable `helper:` category, with one regression through the public function. No source edits were made by this reviewer.

## Independent verification

From the exact scratch export, using the source checkout's existing locked Python environment read-only:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD/tools/ci "$review_python" -m pytest -q -p no:cacheprovider tools/ci/tests/test_tia_baseline.py
```

Observed: `48 passed in 0.13s`, exit 0. Scoped Ruff check passed and Ruff format check reported `2 files already formatted`. Exact base-to-candidate `git diff --check` passed.

Independently called the exact exported implementation twice on retained `138-private-ci103-input.json` and `138-private-timings-input.json`. Both byte strings equal the retained `138-private-serial-baseline.json`. SHA-256 independently reproduced:

`f085f922a6fffadf98900a514b6129aa7bc9315ecd1029cf9a219213fce47731`

The output and report agree on the independent 630 candidate / 592 base / 630 push classified outcomes, 22 product sources, 182 advisory helper IDs, role-specific coverage and timing, and measured warm versus explicit Unknown cold slots.

An additional recursive one-field shape probe replaced each synthetic envelope value with `None`, `False`, `[]`, `{}`, and `1`: 5,040 calls, 4,932 `ValueError` refusals, 108 accepted substitutions (including valid/no-op replacements), and zero non-`ValueError` exceptions. This is a robustness probe, not a claim that every substitution was invalid or that acceptance of all malformed combinations was exhaustively tested. Counts retained in `138-independent-shape-probe-counts.json`.

## Review assessment and limits

The source joins exact role/attempt identities, repeated base custody, independent PR/push dispositions, receipt SHA-256 values, signed candidate subject fields, job IDs, source inventory, classified outcomes, scoped raw coverage, normal child exits, wheel smoke, and file-check evidence. Duplicate JSON keys are refused at all decoded depths; canonical envelopes, non-finite numbers, unsafe path prefixes, unsupported declared receipt shapes, duplicate IDs, and cross-attempt references are checked. Legitimate pytest parameter text remains opaque after the source prefix. Local helper collection remains advisory and does not gain hosted per-node outcomes. Timing derives distinct job/collector/feedback/consumption boundaries and checks the exact cache observation; Unknown metrics do not replace required proof.

The module has no network or credential behavior and explicitly trusts closure-owner authentication. Its checks validate supplied joins; they do not authenticate a caller who fabricates a complete envelope. The report accurately labels historical retained premerge verification separately from later corroborating replays. The two added source paths do not change the active #103 workflow, verifier, policy, helper denominator, or merge authority. The validation code is long for a projection, but its helpers remain organized around the evidence contract and introduce no framework or shared changes.

Coverage limits: focused tests cover the accepted historical pair and key refusal classes, but not every supported skip/branch-coverage/cold-profile alternative. No broad product suite was rerun here while the coordinator investigates inherited monitor failures. This reviewer has not independently authenticated the new delivery run or completed terminal merge-authorizing acceptance.

Tooling note: installed `peer-review help --json` returned no `skillPath`, and `peer-review primary inspect --json` rejected the unsupported `primary` command. No review session or recovery was launched. The explicit independent source-review assignment supplied this local review route; no formal broker acceptance is claimed.

Private original SHA-256 `be4c08ab39e2eb3bbd887c3737e7cf57077a2cd7f0329b32a1635136e90c34b6`. Local paths were removed or replaced with public source links.
