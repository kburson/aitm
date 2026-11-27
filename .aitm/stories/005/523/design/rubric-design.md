# M8 design draft — Adaptive agent-effort estimation rubric

Issue [#523](https://github.com/kburson/aitm/issues/523) · Parent #1

## Goal and boundary

Ship aitm-rubric as a separately installable, opt-in extension. It reads committed planning evidence and a sealed history export, then proposes engaged agent-hours with uncertainty, provenance, and comparable stories. Core owns estimate recording, state guards, and the four-hour implementation leaf limit. The plugin can advise decomposition and has no authority to replace accepted estimates or change workflow state.

M8 requires [Core release #72](https://github.com/kburson/aitm/issues/72), [estimate and Close lineage #51](https://github.com/kburson/aitm/issues/51), a qualified Actual path, and [#522](https://github.com/kburson/aitm/issues/522)’s validated corpus. Track [#229](https://github.com/kburson/aitm/issues/229) as the native Actual prerequisite. [#228](https://github.com/kburson/aitm/issues/228) may substitute if it demonstrates a complete comparable pair under the same contract. Reconcile the native dependency explicitly if that route is accepted. One qualified pair proves the route. Numeric calibration still needs an adequate corpus. A comparable pair can qualify without token or Cost data.

## Corpus and label admission

A training observation is a completed story or applicable attempt with retained Refine/Plan/Close lineage, a pre-execution estimate revision, and a qualified implementation Actual for the same effort basis. Match story and attempt, phase, roles/actors, boundaries, and measurement basis. Exclude coordination rollups, incomplete and disputed Actual, owner wait, idle time, and late estimate revisions. Retain the reason each observation was excluded.

Extract only features available when the estimate is made. Candidates include kind, scope and acceptance criteria, dependency breadth, subsystem and verification intent. Pin the feature vector, estimate phase, feature version and source digest. Later trips, expansions, incidents, human pivots and lessons are outcomes or inputs for future stories. Separate intended owner pivots from planning error.

A legacy row may qualify through documented Refine, Plan, and Close equivalents when their source revisions prove the same pre-work estimate, completed applicable attempt, and qualified Actual. Mark incomplete, held, or ambiguous legacy mappings as ineligible. Use native and documented imported records with comparable units and verifiable provenance. New eligible Close results and corrections create versioned training snapshots. Preserve prior estimates, original records, and model versions.

## Estimation and learning loop

1. Build a rebuildable local index from a pinned Core projection and sealed M7 corpus. Record selected and excluded IDs, source hashes, cutoff, feature version, estimator version, and coverage.
2. Start with a simple robust baseline by supported story class and retrieve relevant comparable stories. When evidence is sufficient, evaluate quantile regression against that baseline. Generate P50 and, where calibrated, P80 engaged-hours with comparable IDs, model and snapshot version, applicability, and confidence.
3. Expose a typed proposal at Refine or Plan with evidence and assumptions. An authorized planner records the estimate through Core. Retain a human substitution or decomposition decision and the pre-work evidence that informed it.
4. As eligible Close outcomes arrive, build a new versioned snapshot. Retrain under a predeclared cadence and sample rule. Compare against the previous model and baseline before promoting a version. Preserve rollback and exact reproduction of earlier proposals.
5. With sparse or unsuitable data, expose insufficient evidence and return comparable examples or a supported baseline with uncertainty. Keep the existing estimate-entry route usable with the plugin absent.

## Evaluation and release gates

- Pre-register train and validation cutoffs and a later holdout. Group related stories and repeated attempts to prevent leakage. Report sample counts and failure reasons by provenance and phase.
- Compare median absolute error and bias with the simple baseline. Measure prediction interval coverage and show results for supported kinds. Establish minimum sample size and promotion thresholds before enabling numeric calibration.
- Prove deterministic input assembly, stable estimates for identical inputs, incompatible-schema refusal, reproducible retraining and rollback. Prove complete no-Cost pairs qualify, incomplete Actual and late estimate revisions stay out, and sparse data produces explicit fallback.
- Qualify the installed optional package against released Core. Run estimate entry with Core alone and with the plugin enabled.

## Proposed decomposition and decisions

Refine into four to six bounded children for corpus admission, deterministic feature extraction and index, the baseline and comparable-story retrieval, quantile evaluation, and the installed proposal and retraining loop. Keep each implementation child within four agent-hours. The feature set, source-quality policy, minimum sample size, and promotion thresholds require reviewed refinement and empirical evidence. A dashboard check against planning 3bc3dadc found zero eligible records among 363. This is an observation about that snapshot.
