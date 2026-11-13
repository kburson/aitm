# #148 formal independent SAR

**Verdict: ACCEPTED.** No blocking findings. The reviewed advisory change is eligible for merge on these exact identities under the existing #103 delivery controls.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the accepted plan and exact candidate independently of implementation. My testing used a private Git archive export and a separate locked environment.

## Exact binding

- Repository and pull request: [kburson/aitm #280](https://github.com/kburson/aitm/pull/280)
- Literal target branch: `trunk`
- Base: `766504a02aaeb9dda339d588172dd7d5bdbd2b3f`
- Candidate head: `7c5eef3b6f584d97923831db3a56dd7541d6133f`
- Tested synthetic merge: `9877cd1dab21b645b8a1d0c7070ea836157051b9`
- Reviewed source and tested tree: `68c7e46c9220aad7d7218192ac49114675072e36`
- CI: [run 43401045905, attempt 2](https://github.com/kburson/aitm/actions/runs/43401045905/attempts/2)
- Trusted #103 verifier pass SHA-256: `113001dcf7b21009c314862305daa9ef2dd4ddb481291a628afb888ecb0624b8`
- Approved exact tree disposition SHA-256: `416878b1eaa99e7e330a44e1c60ec21928ac606ba8454c8f09bec39e14baab2c`

GitHub showed #148 In review and the exact PR open in draft at verification time. I independently verified the current PR head, base and synthetic merge, the merge's ordered parent commits, and the shared candidate/tested tree. The live run and trusted verifier agree on the exact pull_request event and six successful jobs in attempt 2: `python` 131809987868, `python-base` 131809988105, `quality` 131809988023, `file-checks` 131809987574, `collect-evidence` 131813633381, and `aitm-ci` 131813733966. Attempt 1 reached the base job timeout before base artifact upload. Attempt 2 produced the complete signed evidence.

The trusted verifier, approved tree disposition, live artifact metadata and signer log agree on artifact `14026641077`, archive digest `sha256:da8c7771ef87fadf97e2d37a495e8688a91a155f4bd89d572c875e6ab773688d` and subject digest `e2569967feec2c5e1526ed010d2da0bc8921c1ab7c66fede7dbfe63339e4c51e`. I checked the recorded trusted verifier pass and independently reconciled the identity and digest fields with GitHub. Cryptographic verification was performed by the trusted verifier. [#103](https://github.com/kburson/aitm/issues/103)

## Source review

I read both added files, `tools/ci/tia/shards.py` and `tools/ci/tests/test_tia_shards.py`, and traced the T02 inventory and T05 identity contracts. The source satisfies the reviewed advisory plan, SHA-256 `8c60c0ccf5628d8bd325cc96a5b0b297638f4663f68b0eb75199ed0dbb118e27`. The plan review SHA-256 is `590d9e83f4c453e7a2f3c0cf87b312005149d0f52d705cb0369987c02f56402b`.

Before assigning any requested work, the planner validates the expected inventory digest, reclassifies the supplied normalized collection under the full T02 workload policy, requires identical canonical inventory bytes, and checks the independently supplied binding and lanes. T02 classification covers required profiles, runner compatibility, mandatory IDs and obligation metadata. Collection completeness remains a property of the supplied expectation and collection evidence.

Requested keys are unique and must be present in the inventory. Timing hints use inventory obligation keys and nonnegative integer milliseconds. Placement keeps provider, owner, profile and platform lanes separate and preserves isolation groups within each lane. The largest estimated groups are placed first with deterministic ties. Unknown timings use the lane's upper median of known requested durations or a fixed fallback. The output retains exact obligation keys and the inventory digest, which binds optional dispositions and required-child metadata. The cap allows one or two shards per lane. The output is advisory data without dispatch, execution, receipt or merge authority.

## Independent validation

An exact-head archive in a separate locked uv 0.10.6 environment with CPython 3.13.9 passed **59 pytest cases**. This covered 12 focused shard cases and 47 neighboring inventory cases. Ruff lint and formatting passed for both added files. Git whitespace validation passed for the exact base-to-head range.

A separate fixed-seed control passed 100 selections against a complete three-lane T02 inventory with two product platforms and a CI helper lane. It covered optional-skip IDs on both product lanes, reversed request and timing orders, zero timing hints, both caps, stable isolation-group placement and exact disjoint coverage of the requested keys.

No critical or important findings. A change to the candidate, target base or tested tree requires fresh evidence and review binding.
