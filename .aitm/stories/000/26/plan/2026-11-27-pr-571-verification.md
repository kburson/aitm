# #571 draft qualification

The red test failed at the missing C22 module. The draft implements atomic construction of a numbered story and scoped graph changes, resumes retained external identity through C20, and keeps resource creation at pickup. The extra preflight check pins the committed workflow bytes as well as policy settings so workflow-only drift cannot publish the wrong initial state.

Base `d5662440356b911383c4135cffc25305777577af`, head `69c94e961bb85a95edfd121e5035c9fa523eb299`, synthetic merge `f4153864d2630a26a9797f524f71b99e2ec1dcb7`, tree `7347fb28c2bf3306f6b932dd1aa20ff8dfcd48bb`. Draft [repository CI](https://github.com/kburson/aitm/actions/runs/46098928324) and [Core CI](https://github.com/kburson/aitm/actions/runs/46098928267) apply to this exact candidate.

## Compatibility correction

The initial full Core run found six C08 preflight fixtures with a read-set-only operation shape. The workflow fence now applies to typed graduation operations while preserving the existing preflight path. No existing test changed. All 42 local C08 and C22 cases passed, including the workflow-only drift rejection.

Revised draft head `ffa741b13ae950eae1c2eeee4250ac6830ea46da`, synthetic merge `6ed39292740b2e03758beaf72cbc343fc81a6344`, tree `49f7278caec15162a9d7b473633f58c306d74d25`. [Repository CI](https://github.com/kburson/aitm/actions/runs/46099245295) and [Core CI](https://github.com/kburson/aitm/actions/runs/46099245549) apply to this candidate.

Both exact hosted workflows and trusted verification passed while #571 was draft. The full hosted Core suite passed 971 product and one tooling case, with 894 of 971 classified as unit. The 92% floors and signed repository controls remain in force. The PR was marked ready before requesting independent review. [Trusted verifier](2026-11-27-pr-571-ffa741b1-verifier.json)
