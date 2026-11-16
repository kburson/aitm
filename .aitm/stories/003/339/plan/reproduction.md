# #339 Evidence reproduction

The exact artifact archive contains native GitHub records, canonical logs, all retained trial artifacts, both complete fixture diffs, untouched verifier source, the SHA-bound disposition, the local pytest receipts, and code to replay the witnessed outcomes. Its internal manifest binds each file. Use GitHub CLI 2.97.0 for Sigstore replay.

```bash
unzip exact-pr-feedback-evidence.zip -d feedback-339
cd feedback-339
shasum -a 256 -c SHA256SUMS
PYTHONDONTWRITEBYTECODE=1 python3 recipe/replay.py > replayed-summary.json
cmp replayed-summary.json qualification-summary.json
```

The replay recomputes the clocks from the original edit events, GitHub run registration and job timestamps, artifact metadata and live verifier receipts. It authenticates signed subjects for each successful endpoint against the retained public Sigstore trust root. It checks the provider's archived check IDs, candidate identity, artifact custody, full Python collection and phase outcomes, required coverage, and wheel-smoke job evidence. The prior live verifier receipts establish the checks that depended on current PR references. Replay uses those receipts rather than reconstructing prior live states.

The shared source was public [production trunk at the frozen base](https://github.com/kburson/aitm/tree/755fa2ece56cfa8c70a460b269d947ec6e958b2f). The recipe contains the setup, measured arm launcher, bounded local recovery, independent tree-disposition wrapper and read-only capture scripts. The GitHub Actions runs link against [disposable lab repository](https://github.com/kburson/aitm-feedback-339). The evidence can be reproduced from the retained archive without reopening the pull requests or writing to GitHub. Fresh mutation would require a newly authorized disposable repo and a new exact disposition.

The live launcher missed one immediate PR readback after the control's corrected push while GitHub was updating the PR endpoint. The failure trace, original push and later exact native readback are retained. The reproduction launcher now records readbacks and allows bounded provider propagation. The live measurement uses the original push and continuing run. It has no extra registration or clock restart for this readback.
