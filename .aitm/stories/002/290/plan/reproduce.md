# #290 Reproducing the benchmark

Use the locked source at `4cfb41813199f9fa483447a61c65b9ca664fb97e` and a dedicated writable APFS volume. Use macOS ARM64, uv 0.10.6, Python 3.13.9, GitHub CLI 2.97.0 and the checked-in uv lock. The local comparison uses 10 cores.

Create one source export for width 1 and one for width 3 with `git archive`. In each export write the exact SHA to `source-sha`. Independently collect the product and helper profiles using pytest with plugin autoload disabled. Put the two ordered stdout logs in a control source export as `product.log` and `helpers.log`. The hosted ordered inventory hashes come from [#289's verified historical result](../../289/plan/scheduled-historical.json).

Run `benchmark.py manifest` with that control export and the #289 historical result. The output must equal the [fixed workload](workload.json). Run `check-workload.py` with the same inputs. Run `check-path-layout.py` under the locked control environment to verify the APFS ancestor property.

Run `benchmark.py measure <source> <evidence-root> <workload.json> <width> <cold-or-warm>` from the locked control interpreter. Run one layout at a time with cold before warm at each width. Keep the two source exports and evidence root separated from the dedicated native fixture subtree. Leave the common APFS ancestors stable during timed execution. Collect each layout's `summary.json`, coverage, pytest phase evidence, and diagnostic logs.

After all four timed cells run `replay-native-coverage.py <evidence-root>` to retain an independently repeatable focused witness for both required child labels. The measured revision checked child files before coverage JSON but a subsequent report operation removed those raw shards. The archived focused controls retain their own raw shards. The current harness uses `--keep-combined` so future benchmark runs retain the measured shards as well.

Use `exact-source-check.py <git-repo> <evidence-root> <sha>` to verify both exports against Git. Use `readout.py <evidence-root> <workload.json> <hosted-provider.json>` to reconcile the four samples. The hosted provider input is [the exact #289 attempt and job](../../289/plan/scheduled-historical-provider.json). Use `pack-evidence.py <evidence-root> <archive.zip>` and `report.py <readout.json> <archive.zip>` to produce the corresponding archive and report.
