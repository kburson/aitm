# Formal independent SAR — #142 / PR #263 — round 1

Date: 2026-11-12

**Verdict: ACCEPTED. Ready to merge: Yes, subject to the coordinator's fresh delivery-gate check.** No blocking findings.

Signed: Codex independent reviewer `codex-collaboration:/root/sar142`, GPT-6-based Codex (the exact runtime model variant is not exposed to this reviewer). This is the formal off-platform review seat, independent of the implementer/coordinator. No subdelegation, source edits, GitHub writes, merge, or issue/board mutations were performed.

## Exact review identity

- Repository / PR: `kburson/aitm` / [#263](https://github.com/kburson/aitm/pull/263), story #142, Wave 40.
- Literal parent: `trunk`.
- Base: `011342493399ed6e8a12ba0e9c2a4a1e9efaf294`.
- Candidate head: `4e752acaf311c42c4173fc532977502b88ba398a` (`codex/aitm-wave40-142`).
- Tested synthetic merge: `2f0634f5322feb1ef03a5bcc52c5d67a18970c3a`.
- Tested and source tree: `61eeabeed1362d5c39188dd6aade2b6549515b01`.
- [CI run 43233860026, attempt 1](https://github.com/kburson/aitm/actions/runs/43233860026/attempts/1).
- Review admission publication: `cc688e6f5868e1594733ae56e6b49ec355418c9f` on planning.

## Requirements and scope inspected

Read the accepted leaf design, implementation Plan and JIT in `wave40-142/`, and independently verified their raw SHA-256 values:

- Design: `849e2eb8f742ee79a241703f311f50e4efb325cba300d92d25657a2c2e71ae98`.
- Plan: `2d9d2d9105c9ff0b883815138251c3455b766768f5834ef1680fd9dd7411747b`.
- JIT: `de66a1bfafcad9d82575d5717851d5c96be8245fd92b060c031dfee111b3ee59`.

Read all 860 lines of `tools/ci/tia/selection.py`, all 813 lines of `tools/ci/tests/test_tia_selection.py`, and all 20 lines of `tools/ci/tia/edges.json`. The exact diff consists of those three additions only. Examined the relevant T02 canonical parsing, policy, scopes, row projection and obligation rules; T03 snapshot identity, content-reader and digest interface; and T04 policy validation, graph construction, scopes, import and pytest edges, and unresolved records. Traced the production declarations to `pricing.py`'s monitor default version and resource read, and the smoke test subprocess plus `pyproject.toml`'s `aitm-usage = "aitm_usage.cli:main"` entry point.

## Strengths

- Candidate validation is independent of baseline agreement: exact digest, canonical bytes, full workload, complete expected lanes, source membership and exact T02 reprojection precede executable selection. Invalid candidate evidence yields `unavailable`, while unavailable impact evidence yields the independently validated complete candidate inventory.
- Hosted baseline collection identity uses its own protected-target ref/run/attempt rather than borrowing the candidate binding. Both hosted roles and advisory local snapshot identities are covered.
- The two reverse graphs retain byte-exact path identities, deterministic shortest witnesses, former consumers and side-specific evidence. Before-side obligations join the surviving exact qualified key set; removed keys and same-key row changes force full selection.
- Mandatory and new obligations have separate reasons, allowed-skip rows remain accounted for, and unchanged-policy mandatory omissions yield unavailable with explicit missing keys. Verified whole-file removals survive candidate refusal.
- Missing declaration endpoints and unresolved scopes are evaluated against reached paths. Known edges do not erase independent uncertainty. Manifest validation rejects malformed shapes, duplicate identifiers, ambiguous path rules and non-exact paths. No filename similarity or unsupported docs-only shortcut creates evidence.
- The focused tests exercise genuine T02 projections and T03/T04 interfaces, including platform-qualified all-lane fallback, raw non-UTF-8 Git paths, cycle handling, stable ties, and missing graph scope.

## Issues

### Critical

None.

### Important

None.

### Minor

None recorded. No optional cleanup is being treated as a delivery blocker.

## Evidence and validation

Independently queried live PR metadata: open, non-draft, unmerged, base/head/synthetic merge match the exact identities above. Queried candidate-associated workflow runs and all six run jobs; `python-base`, `python`, `quality`, `file-checks`, `collect-evidence`, and `aitm-ci` are completed successfully. A read-only REST query independently confirmed run attempt 1, pull-request event, candidate head and `.github/workflows/ci.yml`. Another read-only REST query confirmed the synthetic merge's ordered parents are the exact base/head and its tree equals the source tree. Local Git independently confirmed the source head/tree/base relationship.

Inspected admission receipt files `142-pr.json`, `142-hosted.json`, `142-owner-disposition.json`, `142-admission-signature.json`, `142-verifier-pass.json`, and `142-review-board.json`. These agree on the candidate and run. The signature readback is correctly diagnostic and requires the separate trusted verifier; the separate receipt records `status: pass`, exact reviewed/tested tree, inherited control blobs, artifact `13950884798`, archive digest `sha256:7591a4102f5ad79c2858d0c0ce4887c1a998fff5f20bbb17882af9e90c376eb6`, and subject digest `c3e3d1ecc63fd59eb62a241fc7689aae4b42a7df18b9a29655f507925b23868b`. The owner-delegated disposition approves only the three-file candidate. The planning publication records Test → Review, with the story Open and board In review, and keeps this independent review pending. I inspected these admission receipts and their publication; I did not independently rerun the cryptographic verifier or substitute a diagnostic signature readback for that gate.

Created an isolated archive of the exact candidate head in a temporary directory outside the implementation checkout. Ran the focused suite with a private virtual environment and private pytest basetemp:

```sh
PYTHONPATH="$review_root/tools/ci" UV_PROJECT_ENVIRONMENT="$review_root/private-venv" uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_selection.py --basetemp "$review_root/private-pytest"
```

Observed **41 passed in 45.29s**, exit 0, CPython 3.13.9, uv 0.10.6. Independently ran `git diff --check` for the exact base/head range: exit 0. The implementer's 147 combined tests and Ruff checks were reported in the supplied evidence; this review does not claim to have independently rerun those broader checks. The implementation checkout remained clean.

## Declined to judge

- Scheduling/execution, hosted inventory custody acquisition, runtime skip outcomes, downstream inventory disposition approval and testmon measurement: explicitly assigned to later leaves or trusted callers by the accepted design. Their interfaces and preserved uncertainty were reviewed; their future implementations are not part of this PR.

## Recommendations and assessment

No revision request. Preserve the independent review artifact and perform the normal exact-candidate delivery check immediately before merge. Acceptance is tied to the four identities above; it is not authorization for a drifted candidate or evidence that delivery/Close already occurred.

**Reasoning:** The implementation satisfies the accepted T05 leaf contract and uses conservative fallback without deriving executable selection from an invalid candidate inventory. The full source review, independent 41-test run, and matching live hosted/admission evidence revealed no user-visible correctness or performance blocker.
