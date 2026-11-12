# #209 local exact verification and native fixture investigation

Candidate `dab76d25ffdce10d5782e14b5b1ea02f617b235c`, literal base `56266ed30bbc572b7e56bc64777e802be264c23f`.

The first local three-worker attempt passed 1,099 tests and held on three inherited tests: the registry disable case `vacant-before-arm-omitted`, scan origin change under append, and the real service crash enrollment fixture. All three passed in focused, isolated, exact-base and exact-candidate runs.

A second local three-worker attempt on a separate fixture root passed 1,099 tests and held on three different inherited tests: activation receipt `held-without-target`, cloned scope proof refusal, and the late Claude revision retaining original scope. All three passed in separate focused runs on both exact revisions. All six test sources are unchanged relative to the literal base. The local failures included empty native discovery, unavailable capture and lost held-source observations. The precise local perturbation is unverified. The result is consistent with the already reproduced sensitivity of native custody to concurrent fixture ancestry changes.

The fresh exact local serial base completed 1,071 product and CLI tests and 196 helpers with both raw coverage floors. The scratch wrapper was edited during its execution for the candidate rerun and returned a shell error after producing those results. A separate verification rechecked the clean detached base SHA, raw pytest status and test count, helper count and both coverage floors.

The hosted three-worker candidate and serial base passed the delivered workflow. The trusted verifier authenticated the signature and the raw replay retained every applicable baseline outcome. The local serial candidate retains full package, CLI, child and helper coverage measurement. Local runner differences are retained as evidence, with the hosted tests and gates unchanged.

The local candidate passed 1,102 product and CLI tests and 196 helpers. The 196 helper IDs match the current literal base. Trunk replaced the old single child-evidence helper ID with serial and parallel parametrizations and added worker reconciliation and rerun identity cases. All previous product IDs remain.
