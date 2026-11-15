# #289 formal independent SAR for the shadow toolchain repair

**Verdict: ACCEPTED for shadow deployment.** No blocking findings for the exact repair PR. The planned genuine scheduled run and separate qualification review remain required before #289 closes.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the complete repair diff, sourced and verified the same GitHub CLI artifact independently, tested the exact candidate and reconciled hosted #103 evidence.

- Repository and pull request: [kburson/aitm #307](https://github.com/kburson/aitm/pull/307)
- Literal target: `trunk`
- Base: `59a92a8797d47bae6c9026cbfe145b9c95a4aff0`
- Candidate head: `2a990e506abe57642c0b60b9bdd4e3d147582994`
- Tested synthetic merge: `07d4f209a71dd10c674fd30202a81a1e7860af67`
- Reviewed candidate and tested tree: `ddd8a3ca53c336a5c0e1d2c5d40724e7156159d4`
- CI: [run 43671088390, attempt 1](https://github.com/kburson/aitm/actions/runs/43671088390/attempts/1)
- Trusted #103 verifier pass SHA-256: `9b1f196078829f92c028599e4ff1e3fb333fc78490dfdffc6ad794573600ed4f`
- Exact tree disposition SHA-256: `802f246a16e0d247c2ed11f4c2ab5696d70cfc57c7881261f94eaa29973a4bbc`

I independently verified #289 In review, the open draft PR, and the synthetic merge's ordered base/head parents and matching candidate tree. The six hosted jobs all succeeded and match the verifier: `python` 132681067370, `python-base` 132681067541, `quality` 132681067593, `file-checks` 132681067618, `collect-evidence` 132682609125 and `aitm-ci` 132682646887. The final artifact metadata and signer log match artifact `14144059397`, archive digest `sha256:0d0bbe76495a2e81d44e24eb4a1aa1514e6e4a2fb6e7242fc9ea8c2b41252d54` and subject digest `7de57d0de4bf464d49f986092b0f5cb48edecddca32d5fcebc8648b743d0fd85`. The trusted verifier performed cryptographic verification. [#103](https://github.com/kburson/aitm/issues/103)

The original protected-trunk diagnostic passed 1,215 product tests, then produced four helper failures and 34 setup errors caused by the existing verifier's pinned GitHub CLI requirement. I independently verified that authentic failed attempt surfaced as a verified diagnostic red with no artifact. The repair plan SHA-256 is `a5357feba265a65bd3600dbb7727a7117bf75b4273386f31755cb8df6a51b199`. The signed source assessment SHA-256 is `810f066fd22b72a1418dc8e6996a767d7b6784adfa065b81e4be40dc3d4da119`. [Original diagnostic](https://github.com/kburson/aitm/actions/runs/43670107921/attempts/1)

The correction reuses the #103 helper job's identical release URL and archive SHA-256 for GitHub CLI 2.97.0 ARM64. It verifies archive bytes before extraction inside a private runner scratch directory, then selects that executable on the job's PATH for the helper profile. I downloaded, verified, extracted and executed the same binary independently. **200 tests passed** in the isolated exact candidate with the pinned executable, including scheduled verification, recovery and existing offline verifier tests. Ruff, Bash syntax and exact Git whitespace checks passed.

The cron and verifier agree on the revised daily 03:47 UTC slot. I checked the boundary immediately before and at that slot, along with the scheduled tests' 45-minute missing-slot grace and separate dispatch route. The production #103 workflow and authority remain unchanged. A genuine scheduled green on exact protected trunk and separate evidence review remain the story-completion criteria. [#289](https://github.com/kburson/aitm/issues/289)
