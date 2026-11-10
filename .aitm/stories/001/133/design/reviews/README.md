# #133 design review intake

Candidate 1 was the initial review input. [Design specification](../test-impact-analysis-design.md) · [Story](../../story.md) · [GitHub issue #133](https://github.com/kburson/aitm/issues/133)

- SHA-256 `8d56991b0070da5255fe5c7365a2987f9fbd5ac38ed8c20bae898129da521e15`
- Git blob `8c24ad20bcff1545e8895a72b52b046e07e4cdfa`
- Status at intake: pending formal design review and acceptance.

Use this directory for SAR, independent SPR, and independent XPR
collateral. For each round, record the input path, exact commit or
blob and digest, reviewer identity and review level, confirmation of
full-file retrieval, findings and verdict, and author dispositions.
Keep superseded input revisions and their responses distinguishable.
The story acceptance event should point to the final exact digest and
review record after the team accepts it.

The preflight builder check identified the need to specify exact-base
outcomes after cutover and to handle a failed scheduled snapshot whose
repair has already landed. The candidate specifies both. Review the
proposed selected-mode coverage and outcome policy, the evidence
required for recognizing an already-landed repair, and the enforcement
proofs for merge and workspace restart. Preflight does not count as a
formal review verdict.

## Accepted revision

SHA-256 `2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928` · Git blob `82581ae31746d3ddfbd5701568533d476daa15d2`.

[SAR](sar-2026-11-10-tia-design/review-manifest.md) · [SPR](spr-2026-11-10-tia-design/review-manifest.md) · [XPR](xpr-2026-11-10-tia-design/review-manifest.md)

Each level binds its own exact input and output. The final XPR decision
binds the accepted bytes above.
