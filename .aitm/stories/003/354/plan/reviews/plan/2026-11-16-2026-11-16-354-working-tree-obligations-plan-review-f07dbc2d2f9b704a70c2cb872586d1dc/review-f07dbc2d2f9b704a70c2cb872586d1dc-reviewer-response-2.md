<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-f07dbc2d2f9b704a70c2cb872586d1dc"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md"
artifact_commit: "0fbf65b9244e0dfe7d7a0301707d59b0a5cddabd"
artifact_blob: "c4b40426a7293295e5332439be2fafadc2a50589"
artifact_digest: "sha256:0267141e5b25ee88112e23b081e8d392aca09d0142ad8f6b4d1b1e1dabab0530"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:5fd002c0d6ba48119db5a190bc420a12968335ffedbe4e46983bb5a6666383d1"
  identity_source: "runtime"
started_at: "2026-11-16T21:58:30.172Z"
submitted_at: "2026-11-16T22:06:56.494Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is round 2 of the independent review, covering `.aitm/stories/003/354/plan/2026-11-16-354-working-tree-obligations-plan.md` at blob `c4b40426a7293295e5332439be2fafadc2a50589`, commit `0fbf65b9`, lines 1–51. I read the whole revised plan and author response 1. I re-checked the revisions against the same read-only trunk sources as round 1: `tools/ci/tia/snapshot.py`, `tools/ci/path_map.py` (`_EXTRA_CONSUMERS`, `consumer_digest`, `select`), `tools/ci/path_map.json` (`full_prefixes`, `full_names`, grok rule), `tools/ci/python_gate.py` imports, `.github/workflows/ci.yml` helper step and `docs/ci.md`. Git was out of bounds and I executed nothing except the required submit. That has two consequences. I did not independently recompute `review_sha256` `7d0dfd66…ef8d`. I did confirm that `finding_sha256` `887517ab…f5c` matches the finding digest recorded in the #352 round-2 verdict.

**Round-1 dispositions.**

- **R1-F001, resolved.** Plan line 14 now gives the exact byte grammar `[ \t]*(#[\x20-\x7e\t]*)?\n` and requires the base to end in LF and at least one comment line. It explicitly excludes CR, FF, VT, NUL, DEL and all other bytes. Line 33 adds red tests for CR-embedded, CRLF, NUL, form feed, a missing terminal LF, a blank-only suffix and allowed whitespace. A lone CR can no longer smuggle in a physical line.
- **R1-F002, resolved.** Line 15 fixes `LocalRequest("kburson/aitm", "local-effective", ANCHOR)`, taken from the admission rather than the target's remote config. Line 19 defines an `authority` object with the anchor commit and tree, finding and review digests, inventory, map and selector digests, bound to the one path and module. Line 33 tests that a remote URL change leaves authority and the snapshot identity stable.
- **R1-F003, resolved.** Line 17 restricts imports to `tools.ci.path_map`, `tools.ci.tia.snapshot` and the standard library, and names the excluded modules. Line 34 adds exact-command subprocess tests under a bogus ambient `PYTHONPATH` and an import trace that forbids pytest, `aitm_usage`, bare `path_map` and the stock planner. There is no `__init__.py` under `tools/`, so the namespace imports resolve from the trusted root under `-E -s`.
- **R1-F004, resolved.** Line 40 states that hosted CI does not execute the new module's tests or count it in the helper floor, which matches `ci.yml:338-342` and `policy.json:6`. Lines 43–51 name the exact locked pytest and Ruff commands, which are required on the exact delivery tree in addition to hosted CI.
- **R1-F005, resolved.** Line 17 makes `argparse` failures emit v1 `unavailable` with `invalid-arguments` on exit 2. `--help` is the only exception, and line 18 enumerates the stable reasons.

**New material checked.** The four-path delivery-tree qualification (line 15) is sound for the report's inputs. The map, selector and audited base bytes all come from the anchor through `before.read_content`. Selection is called with only the audited path and an anchor-derived table (line 20). The inventory comes from the trusted tooling checkout under a hash check. The three new files and `docs/ci.md` are outside the audited consumer digest. They are not under `packages/aitm-usage/`, not in `_EXTRA_CONSUMERS` (`path_map.py:15-19`), and their basenames are not in `full_names`. The committed delivery differences therefore cannot change the digest or the mapped result. The selector-bytes equality check and the adapter specification also address my round-1 optional suggestions 1 and 2.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Delivery-tree contents are shape-checked, not content-bound.** Line 15 qualifies HEAD on paths and modes only. That is safe while tooling and target are separate checkouts, because the report reads none of HEAD's delivery bytes. But if a caller points `--repo` at the same checkout it runs from, the executed tool *is* the inspected checkout's committed code. The "trusted tooling checkout selected by the caller" sentence covers this. Consider stating it explicitly in `docs/ci.md`, or emitting HEAD's blob IDs for the four delivery paths in the report so a caller can compare them.
2. **Single import layout in tests.** The test command puts both `tools/ci` and the repo root on `PYTHONPATH`. Have the new test module import only `tools.ci.tia.working_tree_report` (and `tools.ci.tia.snapshot`), not `tia.*`. Otherwise two `snapshot` module objects can coexist and `isinstance(request, LocalRequest)` in `resolve` (`snapshot.py:1142`) would silently route a test-built request to the hosted path.
3. **Practical reach.** Delivery-tree equivalence makes the report usable on the #354 branch. Any further trunk commit beyond the anchor still yields `unqualified-base`. Say so in `docs/ci.md` next to the example so agents do not treat a routine `unavailable` on current trunk as a defect.

## Decision

accepted
