# #344 live test impact evidence

## Delivery

[PR #346](https://github.com/kburson/aitm/pull/346) delivered commit `8799c5a445dd4b51d499132e9a314b64796ae918` to trunk. Its tree `456a155fbe7d10cb7daafd2bf46f134be78366a8` matches the independently reviewed and tested tree. Both merge parents match the authorized base and reviewed head. The [trusted implementation receipt](implementation-verifier.json) records full validation on the control-changing PR using the previous trusted base. The [post-merge trunk run](https://github.com/kburson/aitm/actions/runs/43878715343) passed the full suite with 1,517 tests.

## Live comparisons

Every row uses the delivered trunk as its exact base. The [machine receipt](tia-proof/receipt.json) binds the full base, head, tested merge, tree, run and attempt for each row. It includes changed paths and consumer or fallback reasons, archived evidence digests, outcome counts, known timing fields, and the trusted verifier receipt. The referenced compressed inventories contain the executed pytest node IDs, including parametrizations.

| Case | Native run | Result |
| --- | --- | --- |
| Fixture-only positive #347 | [43878765256](https://github.com/kburson/aitm/actions/runs/43878765256) | `headless.json` selected `test_grok.py`. All 33 mapped tests passed. The separate full execution on the same tree passed all 1,517 tests in 208.54 seconds and the attester published the full stamp. Trusted verifier passed. |
| Superseded #347 head | [43880699536](https://github.com/kburson/aitm/actions/runs/43880699536) | Base, lint and file checks had completed. The next push cancelled the remaining run while Python was queued. It produced no successful stamp. |
| Same-selection fixture regression #347 | [43881192348](https://github.com/kburson/aitm/actions/runs/43881192348) | Restored the exact stamp from 43878765256 before testing. Of the same 33 node IDs, 32 passed and `test_headless_projection_is_only_corroboration` failed with `assert (0 == 2)`. The run published mapped diagnostics and no passing signed evidence. The trusted verifier held the red head. |
| Direct scope hook #347 | [43882437964](https://github.com/kburson/aitm/actions/runs/43882437964) | The exact delivered selector chooses the 30 scope receipt tests and a new stamp key. All 30 passed locally. The hosted Python job is pending, and the trusted verifier is holding that head. |
| Shared Ledger #348 | [43878780064](https://github.com/kburson/aitm/actions/runs/43878780064) | Ledger alone selected full. All 1,517 tests and the trusted verifier passed. |
| Control, fixture move, unknown executable and runtime data #349 | [43878789073](https://github.com/kburson/aitm/actions/runs/43878789073) | The receipt records every changed path, including the fixture pre-image and new name, and their full fallback reasons. All 1,517 tests and the trusted verifier passed. |
| Explicit documentation rule #350 | [43878801143](https://github.com/kburson/aitm/actions/runs/43878801143) | Checks-only on the README path, with its first full execution and attested stamp. Trusted verifier passed. |
| Same-selection documentation follow-up #350 | [43880030738](https://github.com/kburson/aitm/actions/runs/43880030738) | Restored the stamp from 43878801143. The short check and trusted verifier passed, with the extra full execution skipped. |

The independent full comparison exported the exact red merge tree `d93514160f9ba39b21f378953a2c5d7fb4c919a3` into a private APFS workspace. It used Python 3.13.9, uv 0.10.6 and three pytest-xdist workers. The final comparison reported 1,516 passes and the single intended Grok failure at the same assertion. The first comparison also caught the intended failure and encountered an unrelated local writer-lock setup error, which was absent on the clean retry.

## Replay

Run the trusted selector from the base checkout after fetching the tested merge object.

```sh
python3 tools/ci/path_map.py --map tools/ci/path_map.json \
  --base BASE --candidate TESTED_MERGE --pull-number PR
gh run download RUN --repo kburson/aitm --name aitm-ci-python-aATTEMPT --dir EVIDENCE_DIR
```

On the red run, download `aitm-ci-mapped-diagnostics-a1` for reconciled paths and raw controller and worker observations. Read `aitm-ci-evidence-aATTEMPT` on passing runs for the signed candidate. Use the delivered verifier while a proof head is live. The retained receipts preserve exact verifier outcomes after the drafts close.

To replay the red comparison, check out the recorded tested tree in a separate workspace on macOS/APFS. Create the fixture root outside the source checkout. Run the full comparison under the locked runtime.

```sh
cd packages/aitm-usage
uv sync --locked --python 3.13.9
uv run --locked --python 3.13.9 pytest --rootdir "$REPO_ROOT" \
  -q -n 3 --dist worksteal -p no:cacheprovider \
  --basetemp "$FIXTURE_ROOT/pytest" tests "$REPO_ROOT/tools/ci/tests/test_cli_evidence.py"
```

When a narrowed rule's consumer digest drifts, trace the consumers again and review the rule before requalifying it. From the staged audited tree, `read_tree` and `consumer_digest` in `tools/ci/path_map.py` calculate its updated value for the exact input path and trusted `full_names`. The map-changing PR always takes the full path.

The independent reviewer verified the completed proof cases and the exact-tree full red comparison. The direct source hosted result remains pending.

#344 covers ordinary pull-request TIA. #133 remains open for its broader scope.
