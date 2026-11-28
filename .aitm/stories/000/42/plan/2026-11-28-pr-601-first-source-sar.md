# Independent source SAR for #601

Grok 4.7 completed one read-only call after readiness. The full submitted packet was verified in the transcript.

CHANGES REQUIRED

`CandidateVerification.__call__` drops the pass identity. `candidate_guard` returns `GuardDecision("pass", "exact-candidate-verification-current")`, so that text is `code` and `reason` stays `None` (`machine/guards.py` `GuardDecision`). On the only pass path, `verification/guards.py` rebuilds the decision as `GuardDecision("pass", decision.reason, reads=...)`, so the configured port records `code=None` and never emits `exact-candidate-verification-current`. `services.py` dispatches `core.dev.review-candidate-current` to this wrapper. `tests/unit/test_c35.py` calls `candidate_guard` only, so the rewrite is untested. Hosted CI does not cover it.

The rest of C35 holds. Captured-export uses the sealed export and locked inventory, `uv --no-config run --no-sync --offline --no-python-downloads`, scratch separate from the read-only source, `PYTHONDONTWRITEBYTECODE`, and a redirected pytest cache. Stdout and stderr hashes and the transformed argv are on `VerificationReceipt`. A drifted capture or environment becomes `diagnostic` and is not effective. `select_lane("contained")` loads only `containment_macos` / `containment_linux` or `UnavailableLane`; doctor and `run_verification` pending `lane-probe` before admission, with no export fallback. `InstallationDoctor`, `cli/doctor.py`, and the executor all use `select_lane`. Launch `Popen` is inside C32 `dispatch` after the single-use claim; only an effective `passed` outcome stays `completed`. The guard requires story-tagged or composed source, resolved expansion, exact local proof, and an echoed `HostedCandidate` (repository, pull request, target, base, source, tested). Live provider and lifecycle wiring remain C76/C79; OS adapters remain #43/#44; aggregate admission remains #505; C95 still owns selection policy.

Floors: aitm-core 1,115/96/1,211 → 1,123/97/1,220 (8 unit tests + 1 integration); aitm-usage stays 1,644/142/1,786. Strict ratios still hold (9,700 < 9,760 and 14,200 < 14,288). The integration test is the real Git, uv, and child-process contract; the unit module is deterministic. Readiness is not draft. Verifier attempt 1 passed on the same synthetic merge and tree before readiness (`reviewed_tree` null on that artifact). Seven gates succeeded on attempt 1.

Identities: repository kburson/aitm, story #42, PR #601, base `734695d6c591ac5a73a579703bac6d6832765e0b`, head `e53d3d6bb11af6f33921ac960f76fd7e216429be`, synthetic merge `719cf051f3cd6561e215fbb19ea8839f6f9aa5fb`, ordered parents those two, tree `bcc0aaf2ec281e5976f55e48000e04565f4b7c9f`, repository run `46181558471` attempt 1, core run `46181558596` attempt 1.

REVIEW COMPLETE
