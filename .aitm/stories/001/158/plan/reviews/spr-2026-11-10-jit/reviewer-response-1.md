---
schema: "aitm.review-response/v0"
story: 158
round: 1
level: "spr"
execution: "declared-manual"
input_commit: "28083f277b96e2c259ea67fb537ecd3d906015cd"
inputs: {"design": {"path": ".aitm/stories/001/158/design/2026-11-10-158-qualify-github-merge-fence-design.md", "sha256": "45e0e365d87a3c5f46154c16d7c26c42277e9d0d1f645b3f2b06ca27435ca8a8", "lines": 118}, "plan": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-qualify-github-merge-fence.md", "sha256": "d3d0dbb77b0a4be1a9543add36ae8220270f23c2153af81a83d06fe8e62bde57", "lines": 162}, "jit": {"path": ".aitm/stories/001/158/plan/2026-11-10-158-jit.md", "sha256": "ee647c591f4583785f1aa49bbece533a4eb792885ae37e9ed843321abf75af7c", "lines": 104}}
role: "reviewer"
role_session: "codex-collaboration:/root/prep139"
finding_ids: ["R1-F001", "R1-F002"]
---

# #158 independent SPR, round 1

Reviewer `codex-collaboration:/root/prep139`. Candidate `28083f277b96e2c259ea67fb537ecd3d906015cd` in physical checkout `/Users/kpburson/.codex/worktrees/aitm-158-jit-review/trunk`. Verified HEAD and clean status and read all physical numbered lines in each of the three exact files.

| Document | Physical lines read | Raw SHA-256 |
| --- | ---: | --- |
| `.aitm/stories/001/158/design/2026-11-10-158-qualify-github-merge-fence-design.md` | 1–118 | `45e0e365d87a3c5f46154c16d7c26c42277e9d0d1f645b3f2b06ca27435ca8a8` |
| `.aitm/stories/001/158/plan/2026-11-10-158-qualify-github-merge-fence.md` | 1–162 | `d3d0dbb77b0a4be1a9543add36ae8220270f23c2153af81a83d06fe8e62bde57` |
| `.aitm/stories/001/158/plan/2026-11-10-158-jit.md` | 1–104 | `ee647c591f4583785f1aa49bbece533a4eb792885ae37e9ed843321abf75af7c` |

## Evidence and scope

- Recomputed the accepted #133 design, parent plan and T21 section hashes from their published Git objects. All match JIT lines 17–24. Read the accepted actual-boundary merge requirement and T21/T22 dependency. [Accepted design §6](https://github.com/kburson/aitm/blob/2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9/.aitm/stories/001/133/design/test-impact-analysis-design.md#L394) · [Accepted T21](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L507)
- Authenticated repository ID `1450406435`, public personal ownership, disabled auto-merge, active trunk ruleset `26821811` with no bypass and the three rule types recorded in JIT, and live trunk `a495d60a87ac4ca764f019dc266e579f13f1787e`. #158 was open in Project Backlog with parent #133, no blocked-by issues and #159 as direct successor. [Issue #158](https://github.com/kburson/aitm/issues/158) · [Effective trunk rules](https://api.github.com/repos/kburson/aitm/rules/branches/trunk)
- GitHub documents `sha` as the synchronous PR-head condition. The request does not accept an expected target ref, base OID or stop version. Async acceptance can precede rule evaluation, and async `enqueued` is terminal for the enqueue request while the queue may still land the PR. The plan correctly treats the App ruleset configuration as a hypothesis and distinguishes the tested tree from the landed commit OID. [Synchronous merge contract](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#merge-a-pull-request) · [Async merge contract](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#merge-a-pull-request-asynchronously) · [Async result contract](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#get-the-result-of-an-asynchronous-merge)
- The own-design and JIT pickup holds are explicit. They distinguish leaf planning acceptance, execution authority, the named disposable repository and immutable ID, scoped actor/access grants and the host result. The available inputs are planning evidence. They do not establish a sandbox grant, a live probe or merge-fence feasibility.

### R1-F001 — Pin the final send seam and prevent a false in-flight pass

Required. Plan lines 113–133 name the dispatch boundary but M10 only requires a pause after reservation. That lets a driver pass after a stop cancels the reservation while leaving a second race between its last authority read and the first external send. Specify an adversarial barrier at the last possible point after the final admission check but before any request bytes can reach GitHub. If stop is recorded first, release the barrier and show zero outbound merge requests. If the candidate relies on a serialized boundary that makes this interleaving unreachable, force contention and record the actual ordering primitive and transport event. A request that may already have reached GitHub belongs to M11 and retains durable intent.

For M11b, make the evidence distinguish an unknown client response from a provider operation that could still commit when stop is recorded. M11a already tests a known earlier host commit with an acknowledgment withheld. A response-only delay or another provably completed-before-stop observation must not qualify the overlapping case by itself. Require a causal overlap probe or a documented and independently verified host-enforced invariant covering an already-sent, possibly in-flight request. Where neither can be shown, record the gap and refuse qualification while leaving any unresolved live intent fenced. This operationalizes design lines 71–87 and accepted T21 lines 516–526.

### R1-F002 — Declare the evidence delivery branch and non-source acceptance route

Required. JIT lines 80–86 correctly exclude a product branch, but plan lines 142–162 stop at an evidence directory and generic repository closure rules. The executor lacks a declared delivery target, source-of-truth evidence candidate and acceptance route. The repository checklist expressly calls for a verifiable target and applicable gates for a non-source deliverable. Declare a dedicated isolated evidence worktree/branch based on authenticated `origin/planning`, with `planning` as the delivery target and the exact base, branch and evidence commit or digest recorded at authorized pickup. Keep the disposable fixture checkout and its target separate. Pin real matrix evidence validation, independent review of the exact sanitized report/rules pair and verified publication/readback before closure. Apply the existing planning publication route. No AITM trunk source PR or substitute hosted product CI is implied. [Manual delivery checklist](https://github.com/kburson/aitm/blob/93ac3a8e3ccc228762395cde87ea2aca109d32bc/.aitm/manual-delivery-checklist.md)

## Decision

revisions-requested
