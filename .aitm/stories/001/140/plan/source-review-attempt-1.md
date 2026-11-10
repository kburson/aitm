# AITM #140 independent whole-branch source SPR

**Verdict: accept the source candidate. No actionable findings remain.** This is declared-manual source review by the distinct `/root/source140` reviewer agent. It is not an authenticated hosted CI verdict, native protocol acceptance, owner disposition, delivery authorization, or merge/Close receipt. Those remain the coordinator's separate exact-candidate gates.

## Immutable scope

| Input | Verified identity |
| --- | --- |
| Candidate commit | `6397dd9a5ff7e26a3711651f871f846cb3ef60f1` |
| Candidate tree | `e89faf081d000fd8749430edd8ce47328e6703bb` |
| Literal trunk comparison base | `d769b3169724eeb9ef4b4aee47d3ab4c4489072d` |
| Accepted own design SHA-256 | `29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248` |
| Accepted Plan SHA-256 | `ff4bcab51fa2fcbeccda377c63582f387c87e975b60e3b99c7bd7fffe46ca924` |
| JIT SHA-256 | `7af140e2c2e9d1dee41e79406078d550d7220508895632e2e4e516fbf6429869` |

The entire candidate diff adds only `tools/ci/tia/snapshot.py` (1,144 lines) and `tools/ci/tests/test_tia_snapshot.py` (825 lines). I read both complete immutable files, the accepted own design/Plan/JIT, and the prior hosted task review. Source inspection and execution used a disposable archive of the exact commit at `private review workspace`. No source, index, branch, board, or GitHub mutation was performed in the author checkout.

## Prior findings disposition

All four findings in `140-hosted-task-review.md` are closed against this candidate; none is repeated as an open issue.

1. **Qualified trunk ref:** `snapshot.py:600-605` requires `trunk-tested`, literal `refs/heads/trunk`, and no PR head. `test_tia_snapshot.py:682-691` exercises a self-consistent unrelated branch refusal.
2. **Binding number types:** `snapshot.py:594-595` checks exact integer types on both trusted binding fields; the request already requires positive exact integers. `test_tia_snapshot.py:682-691` covers the boolean attempt alias. My additional independent probe checks boolean and integral-float aliases separately for both run ID and attempt; all refuse with `identity_mismatch`.
3. **Post-parent commit header:** `snapshot.py:385-391` retains the first post-parent header in the suffix scan. `test_tia_snapshot.py:694-715` exercises a literal duplicate tree header. My additional probe constructs a literal PR commit with the correct two ordered parents followed immediately by another tree header; it refuses with `malformed_data`.
4. **Status/endpoint consistency:** `snapshot.py:488-520` requires rename-only endpoint positions, absent opposite endpoints for add/delete, and the correct modified/type-changed status for modes. `test_tia_snapshot.py:718-742` verifies both a false `T` and split delete/add modification refusal. Genuine rename/mode/deletion fixtures still pass.

## Safety and contract assessment

- Hosted authority is supplied and matched explicitly; PR parents and object-derived tested tree are checked against exact bindings, and full comparisons retain an explicit baseline. The implementation does not obtain or substitute live authority. Caller freshness remains a caller responsibility as designed.
- Every Git call retains the no-replacement, no-lazy-fetch, no-optional-locks profile, stripped inherited Git overrides, isolated system/global config, disabled fsmonitor/untracked cache, fixed raw paths and diff controls. Unsupported offline capability refuses before object access. Original object payloads are rehashed, recursive trees are independently parsed, and diff completeness is checked against pinned endpoint entries.
- Local observation preserves HEAD/ref, stage entries, committed/staged/unstaged layers, ignored-input declarations, consulted ignore contents, verified absence, effective SHA-256 bytes and modes. Both captures must match. Reads use a pinned physical root and descriptor-relative no-follow traversal, exact directory-entry spelling, checked identities/metadata, and immutable retained content for later reads.
- Local symlinks are accepted only when their relative in-root target is captured and intermediate paths are observed real directories. Unsafe/unverifiable targets, unresolved stages, unsupported objects, unreadable input, malformed/partial output and detected drift refuse instead of producing an empty pair.
- The retained conservative refusal behavior is consistent with the accepted design: unsupported Git profiles, hard-link aliases, symlink chains and unverifiable targets may prevent narrowing. Local execution-time revalidation remains downstream responsibility. This source review establishes no numeric coverage claim for the resolver.

## Independent execution evidence

Runtime: CPython **3.13.9**, Apple Git **2.54.0 (Apple Git-157)**, current qualified macOS filesystem. The focused suite completed without skips.

From the exact archive root:

```sh
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_snapshot.py
```

Exit **0**, **38 passed in 24.35s**. This includes the existing APFS decomposition/alias, injected file/index/HEAD/membership/ignore drift, malformed/truncated diff, replacement-object, ignored-input and unsafe-path proofs. The archive's isolated environment was created by locked uv; no application code or test files were edited.

Additional reviewer probes are retained at `$review_probe`. Their temporary fixture repositories were private and automatically removed. Command:

```sh
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python $review_probe
```

Exit **0**, with all five assertions groups passing:

- Both trusted binding numbers reject boolean and integral-float aliases.
- Duplicate tree header immediately after ordered PR parents is rejected.
- A symlink target that tries to traverse a regular-file ancestor is rejected.
- Repository-local `diff.renames=false`, `diff.relative=true`, and an invalid `diff.orderFile` do not alter the fixed rename result; index and ref bytes remain unchanged by resolution.
- Detached HEAD provenance explicitly retains `HEAD`.

Broad suite, exact hosted tested-merge evidence and authenticated terminal acceptance are outside this source-review execution scope and remain with the coordinator. No delivery acceptance is inferred from the 38 focused tests.

## Procedure note

The generic installed skill wrapper requested `peer-review primary inspect --json`; the current CLI returned `APR_USAGE: unknown command: primary`. Its documented help recovery worked. The Codex wrapper's `peer-review help --json` returned the installed command index without a `skillPath`. I did not start, recover, or claim a native review session; the coordinator's explicit declared-manual independent source SPR assignment is the authority for this report.

Private original SHA-256 `6ede619e1dea7ab0b4c6d419e37ce5919f5605284b51b56a1ad3c87dc4ceff3b`. Local paths were removed or replaced with public source links.
