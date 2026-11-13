# Reproduce the #267 advisory comparison

Use a local AITM clone containing commit `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`. Run on macOS with APFS and native ACL support, uv 0.10.6, and Python 3.13.9 available to uv. The setup script verifies the repository lock and the [pytest-testmon 2.3.0 wheel](https://pypi.org/project/pytest-testmon/2.3.0/) before installation. `rg`, Git and the macOS timing utilities must be available. Place these recipe files in the same directory.

```zsh
recipe=/absolute/path/to/this/recipe
repo=/absolute/path/to/an/aitm/clone
scratch_dir=$("$recipe/prepare.sh" "$repo")
"$recipe/run-matrix.sh" "$scratch_dir"
"$scratch_dir/venv/bin/python" "$recipe/summarize.py" "$scratch_dir" "$recipe/evidence.json"
"$scratch_dir/venv/bin/python" "$recipe/report.py" "$recipe/evidence.json" "$recipe/report.md"
```

`prepare.sh` clones locally and installs dependencies in disposable private scratch under `~/Library/Caches`. It never runs a push or changes the source clone. The matrix creates another local clone for #143 to keep Testmon's data and runtime files out of the #143 effective tree. Keep the same scratch directory until diagnostics and evidence are reviewed. Select a quiet host for timing. In particular, avoid processes that write or replace files in an ancestor of the private fixture directory during a native test.

`seed.py` applies each change independently. `run-profile.sh` runs the same four CI helper modules and product test directory as the pinned full workload. It passes the CLI smoke module by file to both direct reference and Testmon. The pinned module contains one node, and the summarizer checks that node and the full inventory against #143. Invocations use one worker per profile and run serially. The missing-history case uses the unchanged CLI seed and its independent full reference, so this case changes only history availability for advisory observations.

The Testmon training profile uses `--testmon --testmon-noselect` and runs every node. The warm profile copies the unchanged run's matching profile database and invokes `--testmon --testmon-nocollect`. The cold profile verifies its database path does not exist and invokes `--testmon`. The matrix captures the exit, runtime, inventory, actual phase outcomes and child exits for each profile. The observer adaptation accepts anonymous deselection items emitted by Testmon 2.3.0. The standalone Testmon observer records its reported eligible deselections and the exact items remaining in pytest's session. Calculate actual omissions from the independently observed full inventory minus those items. The reporting hooks do not change the selected list or run outcomes.

`run-matrix.sh` calls the checked-out `python -m tools.ci.tia.local` command. The `--plan` command produces exact IDs and decision reasons. The matrix also observes `--run` for the CLI seed, any selected/no-tests plan, and the deliberately unresolvable base. For the other full-fallback cases, the plan records the complete suggested inventory and the separately executed full reference records the seeded outcomes. The matrix retains only advisory evidence. Run data cannot satisfy the merge gate.

Timing is process wall time. A direct serial or Testmon profile includes collection and test execution. `--plan` includes its own snapshot validation, dependency preparation and collection. `--run` repeats the plan before its execution stage. Report these separately. The one-run matrix provides comparable host conditions and observed elapsed times without sampling enough repetitions for a performance guarantee.

Raw output and setup/call/teardown or collection tracebacks stay in private scratch. The sanitized JSON uses repo-relative test IDs, phase outcomes, child labels and exit codes, and hashes for retained logs and Testmon databases. To check an intermittent unchanged native fixture error independently, run `recheck-baseline.sh` after resetting to the pinned source and after the observer files have been prepared by the matrix. Its three isolated node runs are a diagnostic repeat. The full serial receipt supplies the baseline timing and pass-to-fail calculations.
