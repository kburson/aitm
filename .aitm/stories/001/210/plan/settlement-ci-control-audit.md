# #210 independent exact CI control audit

**PASS** by the independent Codex reviewer `exact_ci_control_audit` for literal trunk `22f265b6aa7c24050c2d798d7e16c1796701cf64` (tree `2f5169c7e1129f0cdb089b9d52ffe776de6af782`), head `ede095d8ce46d6d1dc5138a849259cfc74e34787` and reviewed tree `6f1ae4a5707f2344bbeb4c15efdb823480866feb`.

The reviewer executed the literal-base verifier's exact gate_controls function on both complete Git tree listings. Each tree has 76 control entries. Only three existing regular test blobs differ.

- `test_monitor_journal.py`: `c409c2c8ee9176febb07b0094bb204acebe7a47c` to `32e47074c649bb7a893c618e6274b15a6a2a62bf`.
- `test_monitor_journal_store.py`: `f1e7360e4df86136963025c5ef14156b9706c3c5` to `c68173f1e56a455fadd0e27c14237c7d9d136eec`.
- `test_monitor_scope.py`: `386f0c9def8b1fdea2f0bb8c6462adc311235ebf` to `d9af2cf2525abdb808b953c316d082f10058372e`.

The exact `git diff --binary BASE HEAD -- packages/aitm-usage/tests` was 53,501 bytes, SHA-256 `836371ae1415086f35e31edd708164c6ce70c75bd460993dbaccd01a8bd2806c`. No existing test functions were removed, and 19 were added. Two existing journal failure injectors forward the connection to the new private method signature and retain their predicates and assertions. Shared test helper defaults are retained. Added fixtures are opt-in and clean up their patches.

Workflow, observers, lock, configuration, verifier, policy, jobs, raw floors and signer are byte-identical. The hosted and local candidate inventories and trusted raw replay corroborate this audit. The exact reviewed tree satisfies the verifier's test-change review input. Authenticated attestation verification and source acceptance are separate.
