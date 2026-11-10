# #140 Task 1 hosted snapshot review

**Disposition** Changes requested on the frozen hosted slice. The findings are independently reproduced.

| Item | Verified identity |
| --- | --- |
| Hosted checkpoint | `82b4bac72ea1419b2ada5c7a12197e198b41729b` |
| Tree | `56d07f9f2dd1efcc4cd981f5445565d95c8af58f` |
| Parent | `d769b3169724eeb9ef4b4aee47d3ab4c4489072d` |
| Accepted design SHA-256 | `29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248` |
| Accepted plan SHA-256 | `ff4bcab51fa2fcbeccda377c63582f387c87e975b60e3b99c7bd7fffe46ca924` |

## Findings

1. **P2 · Require the qualified trunk ref for the trunk-tested role.** The non-PR branch validates any syntactically valid `refs/heads/*` ref. A matching request and binding with `refs/heads/unrelated` returned a snapshot with role `trunk-tested`. The hosted full route in the accepted design is a trunk comparison, and the canonical workflow only handles pushes to `trunk`. Require `refs/heads/trunk` for this role and exercise a self-consistent nontrunk binding as a refusal. [Hosted authority validation](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tia/snapshot.py#L517) · [Full comparison fixture](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tests/test_tia_snapshot.py#L165)
2. **P2 · Validate the trusted run and attempt types before comparison.** The strict integer checks apply to the request only. Dataclass equality treats `True` as equal to `1` and integral floats as equal to integers, then the snapshot serializes the original binding. A request with attempt `1` and binding attempt `True` resolved with JSON `true` in trusted provenance. Validate both binding numbers as positive exact integers before matching and add a binding-side boolean or float regression case. [Binding comparison](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tia/snapshot.py#L501) · [Canonical provenance source](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tia/snapshot.py#L563)
3. **P2 · Reject the first contradictory header after the commit parent list.** Iteration consumes the first non-parent header and skips it during the duplicate or late identity check. A real pinned commit written with `git hash-object -t commit --literally -w --stdin`, with correct ordered parents followed immediately by a second, conflicting `tree` header, yielded a PR snapshot. `git fsck --strict` rejected that object. Validate the entire post-parent header suffix, including the terminating line, and add a literal duplicate-tree commit fixture. [Commit header parser](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tia/snapshot.py#L328)
4. **P2 · Validate diff status against the pinned endpoint shapes.** The parser compares the old and new records to the independently observed endpoint entries but trusts the status label once it matches the allowed grammar. A successful Git result injected with `T` in place of `M` for two `100644` versions of a file returned a type-change record. A delete and add for that same modified path also passed. Under this fixed profile, require `M` and `T` to agree with endpoint type, and reject false add/delete status for an existing path on both sides, while preserving genuine independent moves and renames. Add a semantically contradictory record to the existing damage fixture. [Diff status handling](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tia/snapshot.py#L433) · [Injected diff tests](https://github.com/kburson/aitm/blob/82b4bac72ea1419b2ada5c7a12197e198b41729b/tools/ci/tests/test_tia_snapshot.py#L255)

## Evidence

- Read code from frozen Git objects and ran the focused suite from a Git archive of that exact tree, with CPython 3.13.9 and Apple Git 2.54.0. The command `PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_snapshot.py -k hosted` exited 0 with 10 passed in 5.59 seconds.
- Original object behavior, replacement commit/blob refusal to substitute, raw non-UTF-8 paths, true rename/mode/deletion cases, truncated and valid-prefix diff rejection, and pre-object refusal when offline Git controls are unavailable were exercised by the checkpoint suite.
- In a separate temporary repository, injected inherited `GIT_DIR`, `GIT_WORK_TREE`, `GIT_CONFIG_*` and `GIT_EXTERNAL_DIFF`, and set repository-local diff ordering, rename, external driver and fsmonitor overrides. The snapshot digest and the rename matched the baseline profile, and the marker driver stayed untouched.
- The subprocess helper terminated a sleeping command at a reduced 0.10-second timeout and rejected combined stdout and stderr exceeding a reduced byte cap. This was a direct helper probe using temporary inputs.
- Review scope was limited to the two Task 1 files and the accepted #140 inputs. No local implementation, delivery evidence, branch mutation, or board action was part of this review.

Private original SHA-256 `3ead0e355e95e186ca90ce8e55b59cde037c0c77a64b509d25123798b42138b4`. Local paths were removed or replaced with public source links.
