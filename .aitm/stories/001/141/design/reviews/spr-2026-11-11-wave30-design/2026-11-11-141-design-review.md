# #141 independent leaf design and refinement review

**Verdict** Accepted. Zero blocking findings.  
**Reviewer** Codex, independent Wave 30 reviewer, owning #147.  
**Observed at** 2026-11-12T01:55:37Z.  
**Route** Coordinator-assigned off-platform artifact review. The installed peer-review CLI returned a help index without the skill path and did not support the registered primary inspection command. The packaged skill was read from the resolved local installation. This record represents the assigned manual review.

## Exact artifacts

| Artifact | Full lines read | Raw SHA-256 before and after |
| --- | ---: | --- |
| `derive-python-package-edges-design.md` | 164 | `86a3273d883a058675bd92241dd32133d00b9a4af6f8ff9639291e5608ab57be` |
| `2026-11-11-141-refinement.md` | 59 | `aa3de6371ce96597aac8f75eaa4f183b9589f6c355297827fe8d08d2415da2c1` |

## Review basis

- Read [accepted #133 design §3](https://github.com/kburson/aitm/blob/2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9/.aitm/stories/001/133/design/test-impact-analysis-design.md#L69-L144), [accepted T04 lines 217–229](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L217-L229), and its T05 consumer. Recomputed T04 SHA-256 `8834c6ab0466869c48e118e34b3064ff1ef86a362aaecc5e4db66a6f6c0b6165`.
- Read the planning story and delivery/closure records. Read back remote trunk `56266ed30bbc572b7e56bc64777e802be264c23f` with inspected tree `8028f12297fbb3ce6012ad238e2242cfd2f2e839`, verified as the #139 merge with #140's `a495d60a87ac4ca764f019dc266e579f13f1787e` as ancestor. GitHub's native #141 dependency readback returned #139 and #140. Both were Closed as completed and Project Done, with #141 Open and Backlog. [#141](https://github.com/kburson/aitm/issues/141) · [#139](https://github.com/kburson/aitm/issues/139) · [#140](https://github.com/kburson/aitm/issues/140)
- Inspected the delivered `Snapshot.entries`, bound `read_content`, byte path and digest contract, T02 inventory obligation and workload output, the product CLI invocation, and #103's explicit list of hosted CI-helper tests. The design keeps the test file graph distinct from node-level obligation reconciliation. T02 node IDs contain the source path prefix. [Snapshot](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/tools/ci/tia/snapshot.py#L164-L200) · [Inventory](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/tools/ci/tia/inventory.py#L631-L680) · [Workflow](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/.github/workflows/ci.yml#L154-L205)

## Disposition

The leaf specifies both T04 tests and requires a real T03 before/after pair. It preserves raw path identity, separates the snapshots, and records directed provenance through aliases, relative imports, package initializers, re-exports and cycles. Ambiguous namespace and module candidates retain represented potential edges and uncertainty. Qualified pytest scopes cover fixture ancestry, cutoff, config and the product CLI case outside the normal product test directory. The file-level scope is consistent with the T02 projection and T05 consumer.

Known edges coexist with uncertainty. Unsupported source, parse and runtime mechanisms and unqualified invocation scope remain explicit inputs to #142's fallback decision. The trusted policy can bound a recognized dynamic import by the reachable input paths. Unbounded uncertainty applies across packages. An independently verified full route is required when that uncertainty applies, and a failed exact endpoint read does not yield a usable graph. The design establishes no candidate authority and introduces no live selection or hosted workflow edits.

The 3.5 agent-hour estimate is credible for the conservative AST, two owned files and fixtures. The refinement names a 2.5-hour checkpoint and the four-hour cap. The leaf proof requires local focused and T02/T03 regression checks and the existing exact-candidate #103 delivery process. This verdict covers the two documents. Plan, JIT, Develop, source review and delivery have their own evidence.
