# #287 signed independent source assessment

**Source verdict: no material findings.** Signed by OpenAI Codex, independent review agent `/root/review148`. I reviewed the exact source, reproduced native test collection and execution and checked the measurement and counterfactual evidence. Formal acceptance remains subject to exact #103 evidence and Review admission.

- [PR #299](https://github.com/kburson/aitm/pull/299) targets protected `trunk`, base `a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2`.
- Candidate head `9a50c675a3d0180eb91c16bd13024a6f6e6d1f95`.
- Tested synthetic merge `dc8d1fd15f0ad58bb8bd92acbaf20ee9c71e5b2e`.
- Candidate and tested tree `acd6409a2722558c82c62dfe4647c36c8439dc90`.
- Reviewed plan SHA-256 `cfb877dab7883b347676b54e752c182ff69bf6f4ba1312523ed938cf497464a2`.
- Independent plan review SHA-256 `565be8e2d0afeb77f6b0fe8bf87a6e9304125578f0f082bcab525647f3c92c27`.

The one-file diff saves the latest journal view once in the existing successful paired-settlement test and uses that view in the three adjacent assertions about the settled result, unchanged disputes and retained claims. No write occurs between those reads. The historical view, both side-specific cursors and holds, scope bytes, persisted progress rows and fresh post-idempotent-replay sequence observation are still tested. Both swap nodes remain collected. I verified Git whitespace and Ruff lint and formatting.

Separate frozen parent and candidate archives collected identical ordered product/CLI and all-helper lists. The combined unique inventory remains 1,740 and the individual profiles remain 1,216 and 525. The complete monitor journal module passed locally at the candidate head (**136 passed**, no deselections). An independent disposable test plugin suppressed only the settlement projection in the direct post-settlement read. The exact candidate failed at `assert settled.settlements == (change,)` as expected.

I recalculated five coordinator pairs from raw logs. Direct reads were consistently seven versus four. Median observed read time was 113.51 ms versus 59.69 ms, and median focused pytest elapsed was 2.73 s versus 2.68 s. I also reran the frozen-revision recipe after it was updated to avoid mutable checkout input. Every new pair again counted seven versus four reads, with respective medians 87.62 ms versus 46.24 ms inside those reads and 2.29 s versus 2.17 s for the focused pytest session. The pytest elapsed ranges overlap in both sets. The available evidence measures the local test and the eliminated reads. Full CI performance remains unmeasured by this comparison.
