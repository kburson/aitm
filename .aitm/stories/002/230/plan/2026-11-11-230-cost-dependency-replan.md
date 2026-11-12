# #230 Cost integration dependency replan

## Decision

Move #230 from Usage Monitor Epic #100 to Core Epic #2. #230 remains Backlog with its preliminary 3.25 h estimate and direct prerequisites #51, #123 and #124. It qualifies the live integration after the monitor producer and Core receiver are delivered. It retains its own refinement and reviewed, accepted JIT requirements at pickup.

The owner requires #100 and #133 to complete before any Core child begins. #51 additionally waits on its existing #28, #36 and #49 prerequisites. #230 is a separately estimated Core consumer qualification. It adds no prerequisite to #72 or to the accepted M1 release scope.

## Completion boundary

| Owner | Deliverable | Required evidence |
| --- | --- | --- |
| #100 M13 #123 | Fenced monitor publication and pinned story reports | Report, scope, cutoff, rate and reconciliation behavior from the accepted monitor plan. |
| #100 M14 #124 | Versioned monitor export and compatible-delivery behavior | Deterministic export, receipt and reconciliation verified against the approved receiver fixture described in M14. |
| Core #2 C44 #51 | Core receiver and usage/outcome ingestion | The existing accepted C44 prerequisites and Core contract. |
| Core #2 #230 | Monitor-to-Core story Cost integration | Verify the real Core receiver against the released or otherwise qualified monitor producer under replay, delayed evidence, rate revision and ambiguous delivery. Preserve exact story scope, rate basis, coverage and provenance. |
| M6 #259 and #260 | Viewer and board Cost parity, then viewer release | #259 still requires qualified #230, M2 Cost projection/readback and its own predecessors. #260 still depends on #259 and its other accepted predecessors. |

The accepted monitor decomposition already assigns producer acceptance to #123/#124. In particular M14's fixture is the stated compatibility proof until a real approved receiver exists. #100 can therefore complete its accepted monitor scope independently of #51 or #230. Splitting #230 would duplicate the monitor-side acceptance already owned by #123/#124.

Before the move, #230 was the only direct child of #100 with a native dependency on Core. Counting every child toward #100 completion produced the loop #51 → #230 → #100 → #51. With #230 under Core, the order is #100 and #133 complete → Core pickup permitted → #28/#36/#49 and #51 qualify → #230 qualifies. #123 and #124 remain explicit dependencies of #230 to preserve the producer evidence. Core release, M6 parity and lifecycle status retain their existing scope.

## Publication and verification

- Reparent the existing GitHub issue and mirror the move in the append-only planning story records. Preserve the issue ID, original C04 source and all native prerequisite edges.
- Verify #230 has one parent, #2. Verify #100 no longer lists it and has no direct child waiting on Core. Confirm the native #2 blockers and #51 prerequisites and #230 Backlog status.
- Preserve the accepted source plans and reviews by digest. Link this scoped amendment from #100, #2, #230, #247 and #259. Resolve only the former #100 completion-accounting hold; normal Cost and release gates still apply.

[Accepted monitor plan, M14](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#m14-versioned-exports-and-immutable-receiver-compatibility) · [Reviewed C04 scope](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c04-bind-cost-and-compatible-usage-ingress) · [Prior M6 cycle finding](https://github.com/kburson/aitm/blob/c7608f69cc3ef9aa424a8e7370f5dc1b5a6e0051/.aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md#open-dependency-affecting-cost-and-release)
