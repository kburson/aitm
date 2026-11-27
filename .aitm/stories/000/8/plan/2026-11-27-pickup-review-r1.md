# #8 initial plan review

Grok 4.7 Build Fast requested changes. The amended plan follows the delivered C54 schema registry for ownership and the accepted design for evidence recovery. C55 applies the binding observation and retains generation authority. Idea/draft records do not have C54 schemas in the pinned base and are explicitly descriptive in this slice.

CHANGES REQUIRED

The pickup plan under-specifies C54’s ownership, mis-assigns who starts a recovery generation, and contradicts C02’s idempotent same-ID delivery. It also drops named producer contracts, several required failure distinctions, and test cases the story card already fixed.

1. **Ownership map.** C54 owns lifecycle, relationships, and document state (`core.state.changed`, `core.link.changed`, `core.description.set`, `core.doc.accepted`, and the idea/draft/graduate/kind family). C55 owns attempt, execution, and clock types, including `core.attempt.reopened` and `core.attempt.clock.changed` for evidence-only recovery. C56 only registers those owners in `core_reducers()` and implements evidence, action, and provenance. A C56 evidence binding is a causal fact in the same validated batch; it does not start the recovery generation. Session start/end and expansion/trip/pivot facts need an explicit owner in that same map so they are not silently absorbed by the evidence reducer.

2. **Operation identity.** Keep C02 as stated: the same operation ID and payload digest replays the recorded outcome; the same ID with different bytes is an integrity failure; append order is next sequence plus prior-log digest. Remove the conditional rejection of reused operation IDs. Noncontiguous or gapped sequence fails closed. Same-bytes duplicates stay successful. Buffer one causal batch, validate it, then expose state. That batch still has to produce `fold_evidence(state, event) -> StoryState` and `core_reducers() -> ReducerRegistry`.

3. **Failure distinctions.** A missing or disabled action owner stays unavailable under the stable key `(operation, owner, action-id, target-version)`. It is not completed or dropped. Identical usage receipt identity with conflicting data fails closed; identical bytes dedupe.

4. **Test-first gaps.** Drive `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c56.py -q`, the affected contract suites, locked installed Core replay, and Ruff. Add cases for `core.doc-review.opened` source identity and time, missing opening remaining Unknown, review-turn and outcome provenance without a second authority, raw `core.review.recorded` versus later activation/invalidation, idempotent same-bytes replay versus conflicting bytes, and the unavailable action owner.
