# #285 Behavior audit kickoff

Pinned protected trunk at `a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2`. Collected with CPython 3.13.9 and the locked pytest 9.2.0 environment. The separate product/installed-CLI and required CI-helper profiles collected 1,216 and 196 IDs. All CI helper modules collected 525 IDs, including the CLI smoke already counted with product. The combined unique inventory covers **1,740 IDs in 42 modules**, including **1,412** in the current gate's direct product/helper test paths. This is an inventory observation. The audit has additional behavioral work to complete.

[Inventory and matched timings](audit-inventory.json) preserve exact IDs, direct gate membership, counts and any matching hosted phase durations. The source is [trunk CI run 43418827344, Python job 131863407499](https://github.com/kburson/aitm/actions/runs/43418827344/job/131863407499). The runner reported the 15 slowest phases, so unreported durations remain unknown. The product test stage completed 1,216 passes in 353.42 seconds in that run. The local helper collection initially lacked the CI helper import path and produced two import errors. The corrected collection included the path, and all three profiles completed. [Collection recipe](start-audit.sh) · [Inventory and timing join](audit_inventory.py).

## Initial source triage

| Family | Observed behavior and cost | Initial disposition |
| --- | --- | --- |
| Install and upgrade | The launch-agent/upgrade test took 25.02s. The scope-launcher upgrade test took 17.06s. Their source covers an owned installation and recovery after upgrade, plus separately retained receipt/queue behavior across an upgrade. | Preserve these distinct witnesses. Inspect shared fixture/build cost before considering consolidation. |
| Native service | The crash enrollment test took 12.14s and exercises the actual service process and durable private state after a crash. | Preserve the real-process witness. Look for cheaper setup with the same observable crash and recovery behavior. |
| Monitor journal | 136 collected IDs. Two branch-dispute cases took about 9.5s each. Six of the slowest listed setup phases were in this module. The cases include distinct protective triggers such as wrong ownership and a regressing counter. | Inspect repeat setup and parameter boundaries first. Map each trigger to the assertion that would detect a regression before proposing any consolidation. |
| Other large families | Scope has 149 IDs, Codex 115, PR verifier 91, Claude 88. | Classify by supported behavior and protective case next. Counts alone say nothing about duplication. |

No test changes are part of this checkpoint. Continue with behavior mapping and independent review. A consolidation proposal should name the before/after witnesses, show a representative regression is still caught, and provide matched timing. The separately ranked consolidation story owns test edits under #103.
