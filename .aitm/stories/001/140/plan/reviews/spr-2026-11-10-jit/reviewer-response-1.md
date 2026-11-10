---
schema: "aitm.review-response/v0"
story: 140
round: 1
level: "spr"
execution: "declared-manual"
input_commit: "832fe128c86d911618e9fc41419411fc3fbd0c28"
inputs: {"plan": {"path": ".aitm/stories/001/140/plan/2026-11-10-140-resolve-exact-git-changes.md", "sha256": "0fec62f26a3689aae0486b57146e8b6c4cf2c419363ddd73c4486ffa6480e1a5", "lines": 70}, "jit": {"path": ".aitm/stories/001/140/plan/2026-11-10-140-jit.md", "sha256": "a42c653e39204905e7a50a1d152678d3d391d638c7d7cff192341fa93300f0de", "lines": 45}}
role: "reviewer"
role_session: "codex-collaboration:/root/plan138"
finding_ids: ["R1-F001", "R1-F002"]
---

# #140 Plan and JIT · Independent SPR round 1

Route: declared-manual Codex SPR. I authored the separate #138 draft.
The reviewed #140 candidate is `832fe128c86d911618e9fc41419411fc3fbd0c28`.

## Exact input retrieval

I independently hashed the raw files and counted physical lines in
the assigned isolated review checkout. The numbers match the candidate
receipt. I read all returned numbered lines in these ranges.

| Artifact | Raw SHA-256 | Physical lines | Numbered retrieval |
| --- | --- | ---: | --- |
| `.aitm/stories/001/140/plan/2026-11-10-140-resolve-exact-git-changes.md` | `0fec62f26a3689aae0486b57146e8b6c4cf2c419363ddd73c4486ffa6480e1a5` | 70 | 1–35, 36–70 |
| `.aitm/stories/001/140/plan/2026-11-10-140-jit.md` | `a42c653e39204905e7a50a1d152678d3d391d638c7d7cff192341fa93300f0de` | 45 | 1–23, 24–45 |

I checked both against the full own design, SHA-256
`29b5525d07b63789496f789e5faad07cdd60f8a4c2a257b3e222104db7a26248`,
and the accepted #133 T03 section at lines 204–215. The normalized
section with one trailing LF hashes to
`e32dead37553daa9b2dda1850688f4ec780517b4fd028345544e794f4872a101`.
The parent plan raw digest matches
`ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7`.
I ran no Git commands in the review checkout.

## Scope and evidence

- Native readback placed #133 in Dev and #140 in Planning. #140 has
  no inbound dependency and blocks #141 and #147. The two-file write set
  is disjoint from #138. The intended isolated branch targets literal
  `trunk`; implementation is a separate authorized step.
- Source object and GitHub ref agree on trunk
  `d769b3169724eeb9ef4b4aee47d3ab4c4489072d`, tree
  `57e46ef74951a44b21533816171aa3057502178e`. I checked the workflow,
  policy, verifier, file checks and pinned control blobs read-only from
  the source objects outside the review checkout. The exact successful
  push and GitHub Actions check suite `116159440625` cover the existing
  delivery route. The focused fixture proofs and the six current PR
  jobs remain future exact-candidate evidence. The four-file helper
  denominator and explicit test list exclude both additions.
- The current branch is protected by ruleset `26821811`. Its GitHub
  rules and the manual #103 gate are treated separately. Both new
  paths trigger the verifier's gate-defining control classification.
  The JIT correctly retains the exact-tested-tree owner disposition,
  independent review, trusted verifier, fresh base/head and hold rules.
- I reproduced the planning-host flag difference without a source
  mutation. Apple Git 2.54.0 accepts the three global observation
  flags and PATH Git 2.42.1 refuses `--no-lazy-fetch`. This confirms
  the need to qualify the executable at pickup. It gives no evidence
  that a future resolver handles promisor or alias cases correctly.
- Three implementation agent-hours, M, P1 is consistent with T03,
  with an explicit two-hour checkpoint and four-hour hold. The hosted
  and local TDD slices exercise actual Git and public entry points.
  The planned green proof is separate from current route evidence.

## Findings

### R1-F001 — Bind the snapshot identity in the output and its test

Plan lines 33–35, 41–44 and 52–57 define the input bindings and verify
them before comparison. The plan never requires the output snapshots
and their canonical records to carry each of the repository identity,
mode, ref role, endpoint identity and baseline identity. The positive
tests check paths and content, and only one digest assertion changes
the endpoint. An implementation could pass these checks by validating
identity on input and then returning a canonical path/change record
without the context that #141 and #147 need to bind it. The accepted
design at line 17 and the parent plan Snapshot contract at line 104
require these fields in the record.

Name the fields on `Snapshot` and in its canonical record, identify
which values differ before and after, and add positive assertions for
both modes. Assert that canonical evidence binds a changed applicable
identity even when the path/content comparison is otherwise the same.

### R1-F002 — Refuse a stable but unaccounted ignore input

Plan lines 53–57 and JIT lines 24–25 and 32 cover positive ignored
membership, the repository-only rules and ignore drift. They do not
define a refusal test for a stable unaccounted ignore source or known
relevant ignored path. A stable observed path list cannot establish
complete membership if a required ignore rule or known ignored input
could not be read and bound. The design at line 54 explicitly requires
uncertainty in that case.

Add a local test that makes a consulted ignore source unaccountable
while Git returns a parseable membership list, and a case for a known
relevant ignored input whose observed absence or bytes cannot be
established. Specify typed uncertainty and no pair in both cases. Keep
ordinary proven absence distinct from inability to account for it.

## Limits

This review covers the exact planning artifacts and read-only route
evidence. It does not establish implementation authority, candidate
test success, or a source-delivery verdict. The installed peer-review
help exposed the SPR concept but returned no skill path. This response
uses the requested declared-manual route and claims no native assurance.

## Decision

revisions-requested
