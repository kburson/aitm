<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-f07dbc2d2f9b704a70c2cb872586d1dc"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md"
artifact_commit: "6e9eb06220c70186c0146bc9d29af65196fa9e16"
artifact_blob: "f20446fb08341308f40c3ff0a430860522aa6746"
artifact_digest: "sha256:c0eb6620d0eb7ae7dc922cafe5975d030718acf244b095db86494fc12bb6056c"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:5fd002c0d6ba48119db5a190bc420a12968335ffedbe4e46983bb5a6666383d1"
  identity_source: "runtime"
started_at: "2026-11-16T21:58:30.172Z"
submitted_at: "2026-11-16T22:03:24.946Z"
finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent review of `.aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md` at blob `f20446fb08341308f40c3ff0a430860522aa6746` (artifact SHA-256 `c0eb6620…056c`, matching the plan SAR's accepted digest), commit `6e9eb062`. I reviewed the whole plan, lines 1–39.

**Read coverage.** I read story #354, the plan SAR, the accepted #352 finding, the #352 round-2 independent verdict, the #352 machine probe `2026-11-16-352-selection-probe.json`, and the `cases.*.test_inventory` entries of the #344 receipt `344/plan/tia-proof/receipt.json`. The `812bc918…` inventory is the 30-call `test_grok_scope_receipts.py` case. I read the product controls read-only from the local trunk checkout `/Users/kpburson/projects/aitm-workspace/trunk`. Git was out of bounds for this review, so I did not verify that checkout's exact ref against `8799c5a4`. The files were `tools/ci/tia/snapshot.py` (in full), `tools/ci/tia/local.py` (`_request`, imports), `tools/ci/path_map.py` (`read_tree`, `consumer_digest`, `_path_disposition`, `select`, `select_trees`, `select_candidate`), `tools/ci/path_map.json` (grok rule), `tools/ci/python_gate.py` (imports, coverage denominator), `tools/ci/policy.json` (`helpers`), `tools/ci/file_checks.py` (JSON handling), `.github/workflows/ci.yml` (Python job, helper pytest step), `docs/ci.md` and `tools/ci/tests/test_tia_local.py` (import convention). This review ran only the join command and will run only the submit command. I executed nothing else.

**What holds.** The plan stays inside the #352 handoff. It reports pinned obligations, not candidate IDs. It labels `candidate_inventory` and `impact_completeness` as `unqualified`, executes nothing, and returns `unavailable` rather than an empty set. The resolver supports the plan's design. `resolve(LocalRequest)` already makes two full captures and refuses on drift (`snapshot.py:1087-1093`). Effective entries carry raw SHA-256, and the Git blob identity is a separate value (`snapshot.py:984-988`, `1056-1058`), as the plan says. Untracked files become effective `A` changes, so "extra path" refusal covers them. Index-only and staged-then-reverted paths are visible through `staged_changes`. `path_map.select` hashes the consumer digest over the *base* entries only, excluding the input path (`path_map.py:140-153`, `179`). Candidate bytes cannot influence the digest check, so with the pinned base the plan's "reuse `path_map.select`" step reproduces the probe's mapped result. The map rule at `path_map.json:44-47` names exactly `test_grok_scope_receipts.py`. No `__init__.py` exists under `tools/`, `tools/ci/` or `tools/ci/tia/`, so `python -E -m tools.ci.tia.working_tree_report` resolves as a namespace module from the trusted root.

**What does not.** The supported-edit predicate is not specified at byte level, and the plan's own wording admits an executable payload (F001). The report omits the "authority" field that the #352 handoff requires, and the plan never says what repository identity it passes to `LocalRequest` (F002). The import path under `-E` is unstated, although #352 found exactly this startup defect (F003). The delivery gate "normal story CI" does not execute the new tests or count the new module (F004). Exit code 2 is ambiguous with argparse usage errors (F005).

## Findings

### R1-F001 — The "ASCII comment" suffix predicate admits a carriage return, which Python treats as a line break, so appended code can pass as a comment

**Where.** Plan line 14: "The supported bytes are the exact audited base file followed by LF-terminated blank lines or ordinary standalone Python comment lines … Restrict the suffix to ASCII comment text or blank LF lines."

**Problem.** ASCII includes `\r` (0x0D), `\f`, `\v`, NUL and the other C0 controls. Python's tokenizer treats a lone CR as a physical line terminator. So `# note\rimport os; os.system("…")\n` is a single LF-terminated line that starts with `#` and is entirely ASCII, yet it executes on import. A NUL byte makes the module fail to import ("source code cannot contain null bytes"), which is also behavioral. "Blank lines" is ambiguous too: a line of spaces, tabs or form feeds may or may not count. The predicate also never requires the base file to end with LF. Without that, the first appended line merges into the base file's last line.

**Failure scenario.** A worktree edit that appends `b"# x\rimport subprocess\n"` to `grok_scope_hook.py` passes a check written to the plan's wording ("starts with `#`", "is ASCII", "is LF-terminated"). The report then emits `pinned-mapped-obligations` with 30 IDs for a behavioral edit, which is the case #352 says must not be admitted.

**Required change.** State the exact byte grammar in the plan. For example: base blob bytes `B` with `B.endswith(b"\n")`, then a suffix of one or more lines, each matching `[ \t]*(#[\x20-\x7e\t]*)?\n`, with at least one comment line. Explicitly exclude CR, FF, VT, NUL, DEL and every other control byte. Add red tests for a CR-embedded comment, NUL, form feed, a CRLF-terminated comment, a base without a trailing LF (fixture), a whitespace-only line and a suffix with no comment.

### R1-F002 — The report contract omits the "authority" the #352 handoff requires, and the `LocalRequest.repository` identity is unspecified

**Where.** #352 finding line 41: "The report must name its current effective snapshot, pinned trusted base, **authority**, changed path, mapped module and the reviewed inventory identity." Plan line 17 lists the positive fields: base commit and tree, snapshot digest, path, mode, raw SHA-256, consumer reason, mapped module, `inventory_sha256`, `inventory_source` and `node_ids`. It has no authority field. Plan line 16 says to "use `snapshot.LocalRequest` and `resolve`", but `LocalRequest.repository` must match `[^/\s]+/[^/\s]+` (`snapshot.py:1068-1073`), and the plan does not say where that value comes from.

**Problem.** The only existing derivation is `local._request`. It reads `remote.origin.url` from the *inspected* checkout's config and falls back to `"local/checkout"` (`local.py:85-95`). That value comes from the target checkout and the caller does not control it. It is also part of `Snapshot.canonical_bytes()` (`snapshot.py:186`), so the emitted snapshot digest varies with the target's remote config. The plan does not say whether this string is the "authority", whether it is trusted, or whether the report pins it.

**Failure scenario.** Two scratch clones of the same pinned base with identical edits, one with `origin` set to GitHub and one without, emit different `snapshot` digests and different implied repository identities. Neither report states what admitted the 30 obligations. A caller re-validating per plan line 15 cannot tell which identity is authoritative, and the #352 handoff contract field is missing.

**Required change.** Add an explicit `authority` object to the v1 schema. It should name the admission record that authorizes the pinned transfer, for example the #352 finding and independent-verdict digests plus the admitted baseline, path and inventory. Specify the `LocalRequest.repository` value. Either use a constant taken from that admission record, or document that the target-derived value is informational and excluded from authority. Pin the choice with a test that varies `remote.origin.url`.

### R1-F003 — The `-E` entry path does not say which modules it imports, although #352 found exactly this startup failure

**Where.** Plan line 16: `python -E -m tools.ci.tia.working_tree_report …`. Plan line 24: "Reuse snapshot and map APIs." #352 finding line 15 and probe `local.bare_*` record `ModuleNotFoundError: No module named 'path_map'`.

**Problem.** `tools/ci/tia/local.py:20` imports `tools.ci.python_gate`, and `python_gate.py:9` does `from path_map import SELECTION_SCHEMA` as a top-level module. Under `-E`, `PYTHONPATH` is ignored, so any import of `tia.local`, `python_gate`, or anything that imports them fails as #352 recorded. The existing tests import production code as `tia.*` with `tools/ci` on the path (`test_tia_local.py:9-10`). The command imports it as `tools.ci.tia.*`. If the new module imports its peers in a form that only one of those layouts resolves, tests can pass while the documented command fails. For example, `from .. import path_map` fails when the module is loaded as top-level `tia`, and the bare `path_map` import fails under `-E`. The two layouts can also load distinct `SnapshotUncertain` classes, so `except` clauses may silently miss.

**Required change.** State that `working_tree_report` imports only `tools.ci.tia.snapshot` (relative `.snapshot` is fine) and `tools.ci.path_map`, and never `tia.local`, `python_gate` or `inventory`. Add a test that runs the exact documented `python -E -m tools.ci.tia.working_tree_report` as a subprocess from the source root with a hostile `PYTHONPATH` set. It should assert the positive and `unavailable` outputs and that `sys.modules` contains no `pytest`, `aitm_usage` or `path_map` (top-level) module.

### R1-F004 — "Normal story CI" executes neither the new test module nor coverage for the new helper

**Where.** Plan line 38: "Run normal story CI and independent source review on the exact resulting tree before delivery". Plan line 13 and 38: hosted workflow and suite policy bytes untouched.

**Problem.** The hosted Python job runs an explicit list of five helper test modules (`ci.yml:338-342`: `test_python_gate`, `test_pytest_evidence`, `test_verify_pr`, `test_file_checks`, `test_path_map`). The helper coverage denominator is `policy.json:6` `helpers`, which does not include `tools/ci/tia/*`. Because the plan correctly leaves both untouched, hosted CI will not run `tools/ci/tests/test_tia_working_tree_report.py`, and the 90% helper floor will not see `working_tree_report.py`. The PR will run the full product suite because it touches `tools/ci/`, which can read as green evidence for code it never exercised. Step 3's "focused and adjacent" local run is the only execution, and the plan gives no exact command or receipt for it on the delivery tree.

**Required change.** State in the plan that hosted CI does not execute this module or its tests. Name the exact locked local commands that do, run from the repo root with the project environment: the `PYTHONPATH=tools/ci` pytest invocation for `test_tia_working_tree_report.py`, `test_tia_snapshot.py` and `test_path_map.py`, plus the `ruff check`/`ruff format --check` on `tools/ci` from `docs/ci.md:16-17`. Require their receipts on the exact delivery tree as a delivery gate, alongside "normal story CI".

### R1-F005 — Exit 2 means both "unavailable" and argparse usage error

**Where.** Plan line 17: "Explicit `unavailable` exits 2 with a stable reason and no node IDs." Plan line 32: `main(argv)`.

**Problem.** `argparse` exits 2 on a missing or invalid `--repo`/`--base` and prints only usage to stderr, with no JSON. A caller that branches on exit code cannot tell a contract `unavailable` from a malformed invocation. The contract promises a stable machine reason, but the most common caller mistake produces none.

**Required change.** Define usage-error behavior. Either emit the v1 `unavailable` JSON with a stable reason such as `invalid-arguments`, or reserve a distinct exit code and document it. Add a test for each choice.

## Required changes

1. **R1-F001.** Replace the prose suffix predicate with an exact byte grammar: base ends with LF, then one or more lines of `[ \t]*(#[\x20-\x7e\t]*)?\n` with at least one comment, and no CR/FF/VT/NUL/DEL/other controls. Add the listed red tests.
2. **R1-F002.** Add an explicit `authority` field to `aitm.tia-working-tree-report/v1` that names the admission record. Specify the `LocalRequest.repository` value and its trust status, and test it against varying `remote.origin.url`.
3. **R1-F003.** State the permitted imports for `working_tree_report` (no `tia.local`, `python_gate`, or top-level `path_map`). Add a subprocess test of the exact `python -E -m` command under a hostile `PYTHONPATH` that also asserts no pytest or candidate module is imported.
4. **R1-F004.** Record that hosted CI does not run the new tests or count the new module. Name the exact locked local pytest and ruff commands and require their receipts on the exact delivery tree.
5. **R1-F005.** Define and test the exit code and JSON for argument errors so exit 2 always carries a v1 `unavailable` reason, or move usage errors to a distinct code.

## Optional suggestions

1. **Selector identity.** The report applies the *trusted tooling checkout's* `path_map.select` to the *base's* map. Hosted CI uses the base-owned selector (`source: base`). They are byte-identical at delivery because this story leaves the selector untouched, but they can diverge later without failing closed. Consider requiring the tooling `tools/ci/path_map.py` blob to equal the base's selector blob, or emitting the selector digest in `authority`.
2. **Entry adapter.** Say explicitly that the report must not call `path_map.read_tree`/`select_trees`/`select_candidate`. Those use PATH `git` with the trusted checkout as cwd and none of the resolver's protections (`path_map.py:128-137`). Build the `{path: {mode, type, sha}}` tables from `Snapshot.entries` with `ls-tree`-equivalent metadata: `blob` for 100644/100755/120000, `commit` for 160000, and UTF-8 decode failure → `unavailable`. Add a test asserting that the adapted base table reproduces the rule's `consumer_digest`.
3. **Field naming.** The positive report has a top-level `mode: pinned-mapped-obligations` and a per-path file "mode". Name the latter `file_mode` to avoid confusion.
4. **Practical scope.** Version 1 requires HEAD == `8799c5a4`. Once #354 lands, every ordinary trunk checkout returns `unavailable`. State this in `docs/ci.md` and in the story's delivery note, so readers do not take "an agent can read the report before commit" to mean general use.
5. **Fixture seam.** Make sure no `argv` or environment input can reach the test-only admitted-baseline fixture. A test that `main()` refuses the fixture baseline would pin that.
6. **Interpreter hygiene.** Consider documenting `python -E -s` to also exclude user site-packages, since `-I` would drop the cwd entry that `-m` needs. Document that ignored files are outside the observation (`relevant_ignored=()`), which is consistent with `impact_completeness: unqualified`.

## Decision

revisions-requested
