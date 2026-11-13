# #278 formal independent SAR

**Verdict: ACCEPTED.** No blocking findings. The exact reviewed change is eligible for delivery under the existing #103 controls.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the complete change, validated an isolated exact-head archive, and independently reran the operator-facing shadow rehearsal.

## Exact candidate and hosted evidence

- Repository and pull request: [kburson/aitm #283](https://github.com/kburson/aitm/pull/283)
- Literal target: `trunk`
- Base: `b1ff8ce027608da942ec8ac1c7bc124500c5f145`
- Candidate head: `e7fba46767bdad188d432f23584bb2c8e53f5381`
- Tested synthetic merge: `4a6c463b5e9088378c052f54c81cbf3a83508196`
- Reviewed candidate and tested tree: `b2355e454752baf77d71293fed539e966e796cbc`
- CI: [run 43414933254, attempt 1](https://github.com/kburson/aitm/actions/runs/43414933254/attempts/1)
- Trusted #103 verifier pass SHA-256: `355819938eb566f8e1f0d97fd67294889b8670a14eba18f67434e3c3d965cbd4`
- Approved exact tree disposition SHA-256: `b538ce96af85282cef6816db17db8627db856eb33efd82ad8ecb15c3721a31cb`

I verified #278 was In review and PR #283 was open in draft at verification time. GitHub's synthetic merge has the exact ordered base and head parents and the same tree as local Git for the candidate above. The live CI attempt succeeded on all six jobs and the IDs match the verifier: `python-base` 131850474844, `python` 131850475031, `quality` 131850474991, `file-checks` 131850474641, `collect-evidence` 131853900249, and `aitm-ci` 131853987291.

The trusted verifier, approved tree disposition, artifact metadata and signer log agree on artifact `14031707496`, archive digest `sha256:c3300ce76d0793e36e436815164ef4adb544afc9051445eb4878a2d111278912` and subject digest `2c26d75095e8f902e09fdff657963fb96890b7fc5b857a3b140cf430f5c99f1d`. I reconciled these fields against live evidence. The trusted verifier performed the cryptographic verification. [#103](https://github.com/kburson/aitm/issues/103)

## Source, focused validation and shadow evidence

The reviewed plan SHA-256 is `426dec2c7aa47166cf9b1fe8f4127d9608e12e5a4af793694ac91408ec906166`. Its independent review SHA-256 is `d37ef87acb77ef660e63e3746e245d3f50b123c472bfc2aa0dd38d8238966632`. The signed source assessment SHA-256 is `65273fc89f409978d064c981ce3b6a6d1d1e9dae63f42db1c65369df5d558d0f`.

SQLite serializes live intake and state updates. The incident binds any repair nomination to the active version and invalidates stale nomination or recovery when a newer unresolved result or confirmed no-run head arrives. Exact retained observation bodies preserve authenticated failure/job binding across reordered deliveries. The current warning distinguishes inherited and observed failures, and late historical deliveries do not activate a stale warning. Shadow and live state and warning identities are segregated.

The bound operator directory requires private ownership and permissions. Delivery writes the stable attempt file atomically, syncs the file and directory and reconciles the persisted content digest before recording acknowledgment. A retry after write-before-ack can acknowledge the existing content. The warning requests a manual pause and one repair owner. The implementation keeps the warning and nomination advisory and #103 remains the merge gate.

An isolated locked CPython 3.13.9 environment passed **174 tests** across incident, advisory, policy and verifier suites. Ruff lint, Ruff formatting and exact-range Git whitespace checks passed.

My independent real-directory shadow replay reproduced the saved output byte for byte. It generated an operator-readable warning from the historical #277 red, recovered a simulated lost acknowledgment after reopening, and retained one identical warning for that attempt. A newer incomplete attempt created the next warning and invalidated the stale repair nomination. The saved result SHA-256 is `5af53a0e23927dc28fc4fc7a136e859dbd06502783515176558b10e8d2e33477`. The posted warning SHA-256 is `7a8d01538658558dcf20cfaa21eca9809f585b1b02342af491452b4510c5daf3`. [#278](https://github.com/kburson/aitm/issues/278)

The verdict applies to these exact identities. A changed head, target base or tested tree requires fresh evidence and review binding.
