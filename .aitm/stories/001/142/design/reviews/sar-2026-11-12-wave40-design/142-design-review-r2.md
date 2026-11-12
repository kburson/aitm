# #142 independent design and refinement review, round 2

2026-11-12 · Wave 40 · Independent builder check and manual review

**Disposition** — Changes requested. Round 2 resolves the central proof-binding and removal questions. The remaining questions concern supported routes and exact witness and acceptance behavior.

| Reviewed artifact | SHA-256 before and after |
| --- | --- |
| `versions/r2/2026-11-12-142-select-test-impact-design.md` | `2d990b96a6b94db303d9cf9f19919adde01b7838a8a28cde36f85316ed4f4f4a` |
| `2026-11-12-142-refinement.md` | `1e59e88020b404501d85775d61a6209e8cb1e0f0b767addc3e6eddb5e1929ce9` |

Read all 37 design lines and all 19 refinement lines. Compared against the accepted #133 design §3 at `2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9`, T05 at `dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84`, and the delivered T02/T03/T04 contracts at `011342493399ed6e8a12ba0e9c2a4a1e9efaf294`.

Lines 11–19 now give each inventory an independent expected raw digest, full policy and lane identity, identify the candidate and independently established protected-target collection tuples, and keep exact local snapshot digests advisory. They define candidate-only validation ahead of pair checks and distinguish unavailable from full fallback. Lines 25 and 33 now define every known exact removal as full pending downstream disposition and distinguish a missing required candidate row under unchanged policy from a formerly mandatory case removed under independently reviewed candidate policy. These choices resolve the central findings from [round 1](142-design-review-r1.md).

1. **P2 — Close the supported hosted route and remaining row disposition decisions.** Lines 13, 15 and 25 leave the `trunk-tested` route and allowed-skip/same-key changes implicit. T03 accepts hosted PR-tested and trunk-tested endpoint roles. State whether this leaf supports both. If both, require an independently qualified before collection for each and exact candidate identity for the corresponding role. State that full/selected obligation accounting retains policy-scoped allowed skips as qualified obligations, and which treatment applies to same-key disposition or policy metadata changes. T10 and later leaves own authorization and disposition. [T03 hosted roles](https://github.com/kburson/aitm/blob/011342493399ed6e8a12ba0e9c2a4a1e9efaf294/tools/ci/tia/snapshot.py#L581) · [T02 obligation disposition](https://github.com/kburson/aitm/blob/011342493399ed6e8a12ba0e9c2a4a1e9efaf294/tools/ci/tia/inventory.py#L592)
2. **P2 — Pin transitive declaration relevance and the inventory-side witness join.** Lines 23–27 still leave “matched declaration” undefined for a missing endpoint on a reached chain. Say whether an input reached after one valid hop counts and how the other endpoint's absence affects that side. Specify that traversal maps reached nodes to the inventory on the same side and intersects before witnesses with exact surviving candidate keys. The full fallback can retain valid witnesses and a stable uncertainty reason in the same path disposition.
3. **P2 — Distinguish the genuine docs-only case from the focused empty case.** Lines 36–37 still leave this distinction implicit. T02 requires mandatory CLI and child-process cases in every genuine full projection. The docs-only genuine integration should select its required cases and name the positive rule. An isolated decision fixture can exercise hypothetical no-tests with no mandatory or new obligation. [T02 mandatory policy requirements](https://github.com/kburson/aitm/blob/011342493399ed6e8a12ba0e9c2a4a1e9efaf294/tools/ci/tia/inventory.py#L393)

The unchanged refinement's exact three-file scope and four-hour ceiling still fit those clarifications. A native hosted qualification route remains outside this leaf.
