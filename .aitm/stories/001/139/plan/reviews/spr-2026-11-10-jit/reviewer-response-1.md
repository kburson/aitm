---
schema: "aitm.review-response/v0"
story: 139
round: 1
level: "spr"
execution: "declared-manual"
input_commit: "98e3c648bf2ca52cd8554de20b15555bda0c653c"
inputs: {"design": {"path": ".aitm/stories/001/139/design/2026-11-10-139-classify-pytest-inventory-design.md", "sha256": "1ab37e91852683887ea152c0623aea1f7c5d9c6d084819e6c06736380d02c2a9", "lines": 35}, "plan": {"path": ".aitm/stories/001/139/plan/2026-11-10-139-classify-pytest-inventory.md", "sha256": "393e941668da357d471062cd0290bd6f2d1b50a91c387dd573b4b130b0aed663", "lines": 68}, "jit": {"path": ".aitm/stories/001/139/plan/2026-11-10-139-jit.md", "sha256": "0599698e7363e7f1d89ca1446eb49b43ce16711da80d50e030379bbc6faede65", "lines": 44}}
role: "reviewer"
role_session: "codex-collaboration:/root/prep158"
finding_ids: ["R1-F001", "R1-F002"]
---

# #139 independent SPR round 1

Reviewer `codex-collaboration:/root/prep158`. Scope is the delegated
local independent planning review. Review worktree
`/Users/kpburson/.codex/worktrees/aitm-139-jit-review/trunk` was clean at
`98e3c648bf2ca52cd8554de20b15555bda0c653c`. I read every numbered line
and verified the physical files and frozen Git blobs against the
candidate manifest.

| Document | Physical lines read | Raw SHA-256 |
| --- | --- | --- |
| `design/2026-11-10-139-classify-pytest-inventory-design.md` | 1–35 | `1ab37e91852683887ea152c0623aea1f7c5d9c6d084819e6c06736380d02c2a9` |
| `plan/2026-11-10-139-classify-pytest-inventory.md` | 1–68 | `393e941668da357d471062cd0290bd6f2d1b50a91c387dd573b4b130b0aed663` |
| `plan/2026-11-10-139-jit.md` | 1–44 | `0599698e7363e7f1d89ca1446eb49b43ce16711da80d50e030379bbc6faede65` |

## Evidence checked

- Recomputed the accepted #133 design and plan hashes at `2ff1b49`
  and `dbe0d68`, and T02 lines 187–202 including the trailing LF. They
  match the parent acceptance and #139's hydrated section digest
  `ade97a158a01113fdd6c0651f09b46de587adb902a86e0d8908c371e4c5edd54`.
  Read downstream T05, T07/T08, T10, T11 and T12 interfaces.
- Authenticated GitHub readback confirmed #138 Closed as Completed
  and Project 24 Done, #139 Open and Backlog, parent #133, inbound #138,
  and downstream #141, #142, #144, #147 and #148. #138 merge
  `0175e77c398dc97c59db166fa64e2e9a673b4b40` is an ancestor of the
  authenticated trunk `a495d60a87ac4ca764f019dc266e579f13f1787e` with tree
  `47fa209c89e99e041f716d856c9ae59b3360c97e`. Sibling blobs match,
  the three proposed owned paths are absent, and the stated controls
  and four helper test blobs match between the historical and
  current trees.
- Read the #138 closure and delivery records, sanitized report, and
  canonical private comparison. Its raw digest is
  `f085f922a6fffadf98900a514b6129aa7bc9315ecd1029cf9a219213fce47731`.
  Independently reproduced 592, 630 and 630 exact unique nodes,
  the distinct role receipt hashes and equal candidate/push node
  digest, plus 182 separate local advisory helper nodes. The helper
  receipt establishes no hosted per-node result.
- Re-read #140's delivery receipt and archive 13805565772 in memory.
  The ZIP, pytest member and sorted node array digests match JIT.
  Verified 748 unique IDs, zero deselections, all reported phases
  passed with no xfail flags, both child labels and Darwin/APFS. The
  118 additions by module and zero removals match JIT. Read the
  current #103 policy, native ACL/firmlink test declarations, the
  one-shot and installed-console child reporting, and the Python and
  helper commands in the workflow. No candidate implementation or
  hosted TIA proof exists at this stage.

## Required findings

### R1-F001 — Pin a complete inventory scope for downstream consumers

Design lines 5 and 11 and plan lines 33–36 model a call as one of
`product-base`, `product-cli` or `ci-helpers`. The current gate has
product/CLI and the helper targets in the same applicable workload.
The accepted T05 full fallback consumes one Inventory, and T11
requires a disjoint exact union across owners and scopes. Each
one-profile result can currently look complete to a consumer even
when the other profile is missing. The only named required scope
domain also travels in the collection itself. Omitting a required
scope from both the declaration and rows can satisfy a set-equality
check unless the reviewed policy or separately pinned caller
expectation supplies the domain.

Keep the bounded classifier and specify the consumer-facing scope
contract. Either represent the required profiles in a complete result
or explicitly type profile outputs as partial components and name
which later owner assembles and validates the complete inventory.
Bind the expected profile/scope domain independently of the observed
rows. Pin a contract case that refuses omitted required helper scope
when full product/CLI plus helpers was requested, while preserving
the legitimate product-only baseline and advisory helper history.
The historical advisory helper IDs cannot fill a missing qualified
hosted component.

### R1-F002 — Exercise the hosted versus advisory provenance contract

T02 explicitly accepts both local and hosted collection inputs.
Design line 9 and plan lines 29–36 define two different snapshot
shapes, but the planned tests on lines 42–44 only require a generic
receipt/provenance change. Both historical and current replays are
unqualified #103 comparison inputs. A classifier that mishandles
the hosted variant can pass those cases and all replay.

Pin a focused fixture pair with identical obligation rows under
local advisory and caller-verified hosted input. Assert distinct
identities and preservation of hosted tree/ref/run/attempt and
scope receipt bindings. Include wrong-kind or incomplete hosted
identity and ensure it fails closed without silently downgrading.
This is a projection test. Native observation qualification remains
with T07/T08.

## Decision

revisions-requested
