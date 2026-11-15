# #287 formal independent SAR

**Verdict: ACCEPTED.** No blocking findings. The exact reviewed change is eligible for delivery under the existing #103 controls.

Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the complete source diff, used separate frozen archives for collection and performance checks, and verified the counterfactual and hosted evidence.

## Exact candidate and hosted evidence

- Repository and pull request: [kburson/aitm #299](https://github.com/kburson/aitm/pull/299)
- Literal target: `trunk`
- Base: `a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2`
- Candidate head: `9a50c675a3d0180eb91c16bd13024a6f6e6d1f95`
- Tested synthetic merge: `dc8d1fd15f0ad58bb8bd92acbaf20ee9c71e5b2e`
- Reviewed candidate and tested tree: `acd6409a2722558c82c62dfe4647c36c8439dc90`
- CI: [run 43666917870, attempt 1](https://github.com/kburson/aitm/actions/runs/43666917870/attempts/1)
- Trusted #103 verifier pass SHA-256: `8241ee74fed2e581f782bf6e99b29e8ec12975d7ff99c178ad8a8caec80a63ab`
- Approved exact tree disposition SHA-256: `2739008827bea1a1bcc9144ec89a5c2470cce3b1cdf9784d5c8dc050aa97a3e3`

I independently checked that #287 was In review and PR #299 was open in draft. GitHub's synthetic commit has the ordered base and head parents above and the same tree as the exact local candidate. All six live CI jobs succeeded and match the verifier: `python-base` 132668232754, `python` 132668232975, `quality` 132668233074, `file-checks` 132668233001, `collect-evidence` 132670133507 and `aitm-ci` 132670193967.

GitHub artifact metadata and the signer log match the trusted verifier and exact disposition on artifact `14142951760`, archive digest `sha256:969b05a3141f47fb4d69da91ac9275ca844a368d7ac0d99d39aac84a556dffbc` and subject digest `0cec88e03a441961ec0a06c6c7a6b362e9e66c0d56c6d97086575a99e73cd5e5`. The trusted verifier performed the cryptographic verification. [#103](https://github.com/kburson/aitm/issues/103)

## Source and independent native evidence

The reviewed plan SHA-256 is `cfb877dab7883b347676b54e752c182ff69bf6f4ba1312523ed938cf497464a2`. The independent plan review SHA-256 is `565be8e2d0afeb77f6b0fe8bf87a6e9304125578f0f082bcab525647f3c92c27`. The signed source assessment SHA-256 is `42aff64167651eb1da5ef7d24a9f6808d2a3d981b0d0efea5ab2c1b931befa04`.

The only source change reuses one read-only post-settlement snapshot in the three contiguous assertions for settlement, disputes and claims. The test retains the historical snapshot, both revised cursors and holds, scope bytes, durable progress rows and the separate read after the idempotent replay. Both swap tests remain. The production implementation and #103 controls are unchanged.

Independent collection from frozen parent and candidate archives matched the exact ordered 1,216 product/CLI and 525 all-helper IDs, totalling 1,740 unique IDs. The exact candidate's entire native monitor journal module passed **136 tests with zero deselections**. Ruff lint and formatting and exact Git whitespace checks passed. An isolated test-only counterfactual dropped the recorded settlement from the returned post-settlement view and the existing exact node failed at the intended assertion.

The five reported matched pairs consistently measured seven direct reads in the parent and four in the candidate. I recalculated the medians from the raw logs at 113.51 to 59.69 ms inside those reads and 2.73 to 2.68 s for the focused pytest run. The timing summary SHA-256 is `76672179bf15956fe495c18e315966da3f4a5270e1ea1d0a792c4388431519b1`. An independent five-pair rerun using exact Git archives replicated the direct read counts on every pair, with medians 87.62 to 46.24 ms for those reads and 2.29 to 2.17 s for focused pytest. Total elapsed ranges overlap in both sets. These observations quantify the local test only. [#287](https://github.com/kburson/aitm/issues/287)

The verdict binds the exact identities above. A changed head, base or tested tree requires fresh evidence and review binding.
