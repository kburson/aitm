# #104 ordinary PR signing probe result · November 9, 2026

**Passed.** The verified GitHub Actions certificate independently bound the authorized probe on draft PR #107 to its exact synthetic merge and run attempt. The selected attempt used the Public Good Sigstore instance. This is diagnostic evidence only.

## Exact input and run

- [Reviewed JIT](../plan/signing-probe-jit.md) · [Exact pre-push review](../plan/signing-probe-pickup-review.md) · [Accepted replan](../design/github-tested-merge-binding-replan.md).
- [Draft PR #107](https://github.com/kburson/aitm/pull/107) received one fast-forward source update from `d34921e0dd604abb2af5b710031d8e4a85c76cee` to `6f428770c41352fa0de8935a882fa10317ce6039`. The only changed file was the diagnostic workflow, blob `caff1cdd59a12722d13fe9757277c9a8a35347d6`, SHA-256 `51f877d7e372483799c25af376500c6e2673e782f2a88bbb77439e73c53ffb62`.
- [Run 42756762134, attempt 1](https://github.com/kburson/aitm/actions/runs/42756762134/attempts/1), ordinary `pull_request` synchronization, workflow ID `412848571` and check suite `115798031539`. Authenticated run, attempt, suite and both GitHub Actions checks named the PR head. The [collector](https://github.com/kburson/aitm/actions/runs/42756762134/job/129632824237) and [isolated signer](https://github.com/kburson/aitm/actions/runs/42756762134/job/129632864763) both ran and passed in attempt 1, with start times after the attempt started. The collector verified its checkout and ordered parents before upload. The signer validated the exact same-run raw archive before signing. Hosted job elapsed times were 5 and 8 seconds. Exact active agent engagement was not measured.
- GitHub's PR merge field and `refs/pull/107/merge` both returned `d6166a5026cc1989b0b4ce493060119a868ffd24` before and after verification. Its authenticated raw Git object has tree `a4382ac4dfbe0b64ceeb0517f522c8ee6af1e0fd` and exactly two parents in order. They are trunk `f80f22645e2008c4cac9dc6e4003640bba976b5f` and the PR head `6f428770c41352fa0de8935a882fa10317ce6039`. The live target and authenticated event association matched both.

## Evidence and verification

| Evidence | Identity |
| --- | --- |
| Collector archive | `13735438141`, `aitm-ci-collector-a1`, SHA-256 `e7304b49b0336619b61314d8ec03b1929d4779446f2ec4166a4436fed871e05c` |
| Final archive | [13736260404](https://github.com/kburson/aitm/actions/runs/42756762134/artifacts/13736260404), `aitm-ci-binding-probe-a1`, SHA-256 `6c86732c4f91d001a071325d14994cc3fc3d887cd3aebe07bd39c028fd53e9f6` |
| Fixed subject | `candidate.json`, SHA-256 `d52a11585018f61be6a506077abe1f7f955a662894e4dac482f2faa576acde4c` |
| Sigstore bundle | `attestation.sigstore.json`, SHA-256 `a6554cd5da6ab54fc9ea5bf88453ce5ce437daf564ec57e4110b1c219381c652` |
| Public record | [GitHub attestation 65657247](https://github.com/kburson/aitm/attestations/65657247), Public Good Rekor log index `3777887507` at 10:35:07 p.m. Central |
| Verifier | GitHub CLI `2.97.0`; independent Public Good trusted-root JSONL SHA-256 `3c2cc7f357dc064ec527fdcd78da6e9245c21a381e1abaa0f2b62b186bcac1a1` |

The raw final archive matched GitHub's digest and the run association. It contained exactly two bounded regular files with the expected original names. GitHub CLI verified the signed subject with trusted public roots and a Rekor timestamp. The verified certificate named issuer `https://token.actions.githubusercontent.com`, repository ID `1450406435`, hosted runner, `pull_request`, and `refs/pull/107/merge`. Its source, build configuration and signer digests all matched the temporary merge SHA. The configuration and signer URI named `.github/workflows/ci.yml@refs/pull/107/merge`. The certificate invocation URI matched run `42756762134` attempt `1` exactly. A second read-only verification obtained the same bundle from the public repository attestation record.

To reproduce the fixed subject after the workflow archive expires, write the literal line `{"probe":"aitm-104-ordinary-pr-binding-v1"}` followed by a single LF. Verify using `gh attestation verify candidate.json --repo kburson/aitm --signer-workflow kburson/aitm/.github/workflows/ci.yml --source-ref refs/pull/107/merge --source-digest d6166a5026cc1989b0b4ce493060119a868ffd24 --signer-digest d6166a5026cc1989b0b4ce493060119a868ffd24 --cert-oidc-issuer https://token.actions.githubusercontent.com --deny-self-hosted-runners --predicate-type https://slsa.dev/provenance/v1 --format json` and compare the verified certificate invocation against the attempt URI above. Historical verification cannot satisfy a current PR gate.

Local behavioral checks refused wrong or malformed artifact IDs, the wrong run or attempt-qualified name, an expired archive, unexpected and NUL-suffixed archive members, a modified subject and the wrong archive digest. After the live run, cryptographic verification refused the PR head as the expected tested SHA. The verified attempt-1 invocation was refused when compared with attempt 2. There was one live probe and no rerun.

At this checkpoint #104 remained in Planning and PR #107 was open, draft and unmerged. The probe produced no `aitm-ci` result or production coverage claim. The 90% line floors and meaningful behavioral tests remain delivery requirements.
