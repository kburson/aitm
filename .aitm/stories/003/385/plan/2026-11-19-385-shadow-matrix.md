# #385 hosted Ubuntu shadow matrix

Run the unchanged probe from trunk `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9` in an isolated, read-only GitHub Actions workflow on a dedicated branch. Bind each same-repository draft PR to its literal base, head, GitHub tested merge, and tested tree. Execute the base-owned path map and separately time probe collection plus full, graph-selected, and mapped pytest execution on the same runner and locked environment for each case. Match per-node outcomes to a complete independent full run. Record any retries or unavailable evidence. Only the required workflow supplies required status.

| Case | Input | Expected before hosted execution |
| --- | --- | --- |
| real-source | Edit the Grok hook source without changing behavior | Probe full because the trunk graph has unbounded imports. The existing map may also fall back because its consumer digest drifted. A useful real narrowing is required for promotion readiness. |
| real-shared | Comment-only edit to the package pytest conftest | Probe full for the shared collection input. Record the map decision. |
| real-rename | Rename a real product test module while preserving its contents | Full for both selectors. Capture changes and any old/new graph witnesses. |
| real-config | Comment-only edit to the product pytest/package configuration | Full for both selectors. |
| fixture-green | Tightly bounded static graph, behavior-preserving direct/transitive dependency edit | Narrow, with direct and transitive witnesses. Full and assigned tests pass. |
| fixture-red | Same static graph with one leaf regression that affects both consumers | Narrow. Selected and full runs both fail exactly the two intended tests. |
| fixture-missing | Remove the configured service obligation from the controlled tree | Probe unavailable, with an empty assignment. |
| negative controls | Wrong tree, stale head, truncated full phase receipt | Refuse mismatched Git inputs and reject incomplete full outcome evidence. |

Keep the required workflow, map, verifier, branch protections, and #355 unchanged. The experiment branches and draft PRs are qualification inputs only.
