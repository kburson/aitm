# #186 independent source review

**Verdict — accepted.** Reviewed and signed on 2026-11-10 by Codex `/root/pickup186`, a separate agent from the implementer. Off-platform review. Native GitHub approval absent. No actionable blockers for this source revision.

[PR #196](https://github.com/kburson/aitm/pull/196) targets `trunk`. Reviewed head `8475b124f921bd0742d04b228c0a44824369b441` against base `c4ea6b0d6c548830a3ad05d0bb76ec48625d1ca2`. The reviewed source and hosted tested tree are `6107d353b1b5d40b1f5e050acbef53f57cae6e3b`. The hosted tested merge is `637c061712a0e17653d22653604eb68c5452c308`.

Reviewed all three candidate changes, `tools/story_dashboard/evidence.py`, `tools/story_dashboard/tests/test_evidence.py` and `tools/story_dashboard/capture.md`, against the accepted #186 packet at planning publication `5f801e8a7150a41ea57d1eda7ac232c2d48817f3`, SHA-256 `04504fb07d672d14f476f281bd0f04fb5336824ad4db9516d8fc79e261f34a21`, and the accepted #181 design and A01 plan. Scope covers offline pinned reads, registered evidence validation and capture instructions. Timing aggregation, Cost assurance and the live pilot remain assigned to the later #181 leaves.

## Findings resolved

1. Both the pinned reader and prospective command require a v0 manual-bootstrap event with a supported actor kind for new v1 registrations. The original #181 digest-pinned seed and its retry still pass.
2. Prospective validation requires reconciliation when an existing matching registration is held. The regression reproduces the earlier timestamp problem and verifies readback after appending a retry.
3. Each explicit observation recording time bounds that observation's occurrence endpoints. The chronology regression and distinct future-receipt cutoff test both pass.
4. Excessive nesting in an individual header's updated, parent or state field produces its scoped gap. The regression confirms a separate story remains readable.

The earlier changes-requested verdict is preserved as `source-review-r4.md`, SHA-256 `0fbfe27a30562a7aff8aca1102bd9fddcfda4cbcd076ac9e9231799cdd066c0e`.

## Verification

- Confirmed the clean local checkout matches the reviewed head and tree, the base diff contains only the three accepted additions, and `git diff --check` passes. Independently reran all 11 focused Python 3.13 tests successfully.
- The exact candidate log matches the reviewed head and tree and records focused tests, Ruff check and format, guide validation, publication readback and idempotent replay.
- The delivered trunk verifier returned pass for canonical run 42918480605 attempt 1. Its PR, head, base, tested merge and tree match this review. Its signed evidence covers `python-base`, `python`, `quality`, `file-checks`, `collect-evidence` and `aitm-ci`. The verifier record identifies evidence artifact `13810458722`, archive SHA-256 `b52c3b1fc6431486791e4ffff4952622c405c75842c99a101d2caae9f0fc3e53`. [Hosted run](https://github.com/kburson/aitm/actions/runs/42918480605/attempts/1)
