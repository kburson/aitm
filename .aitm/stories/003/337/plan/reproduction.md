# #337 Evidence reproduction

The production archive includes its own manifest, capture scripts, public Sigstore trust root and byte-reproducible metrics. Follow the [production readout](production-readout.md) from a fresh extraction using pinned GitHub CLI 2.97.0. The provider and test data gathered there remain read-only.

To check the four retained lab attestations, extract the [rollback evidence](rollback-evidence.zip) in another scratch directory, extract the trusted root from the production archive, and run the archive's replay script.

```bash
unzip -p production-evidence.zip raw/trusted/gh-trusted-root.jsonl > gh-trusted-root.jsonl
unzip rollback-evidence.zip -d rollback-replay
python3 rollback-replay/replay-lab-attestations.py --trust-root gh-trusted-root.jsonl
```

This verifies the signed lab repository, workflow, source ref, exact synthetic merge, candidate SHA-256 and run identity against the retained pre-merge verifier receipts. Each artifact ZIP and provider record is in the corresponding case directory. The historical signature replay does not require open PR state or use a production credential. The retained trusted live verifier passes were recorded while their exact claims were current. The earlier restore's final refusal is retained separately with both native synthetic commit documents.

Lab scripts were executed only on `kburson/aitm-rollback-337`. The archived native rule suites, readbacks, protected commits and timestamped receipts allow inspection without repeating the live mutations. The rehearsal signing key was kept outside the archive. Its public verifier and signature are included. The applied forward repair changed a disposable mode file only and retained the canonical workflow and verifier bytes.
