# #7 envelope compatibility supplement review

Grok 4.7 Build Fast reviewed the narrow allowlist amendment and returned PASS. Core names still require a registered reducer at replay. The review comment about a three-segment lookalike refers to its syntactic validity only.

PASS

The supplement is the right fix. Keep the three-segment grammar and admit only the accepted wire literal `core.attempt.clock.changed`. Do not rename it to a three-segment form such as `core.attempt.clock-changed`; that would drop the accepted design's durable-boundary identity.

Findings the change must satisfy:

1. Put the exception inside the existing anchors as one alternation: `^(?:<three-segment>|core\.attempt\.clock\.changed)$`. The literal is escaped. An anchor on only one side, or an unanchored `|`, would accept prefixes, suffixes, and other four-segment names.

2. Segment count is the only exception. `core`, `attempt`, `clock`, and `changed` already fit the lowercase token class. Do not widen token length, case, or separator rules.

3. Unknown-extension behavior stays as it is for every other type. A three-segment lookalike such as `core.attempt.clock-changed` remains a valid unknown extension. Reject only non-matching values: other four-segment names, a fifth segment, case variants, and strings that merely contain the literal.

4. `#7`'s allowlist growth is only `packages/aitm-core/src/aitm_core/models/events.py`, and the diff there is only that anchored alternation. No second grammar change in the same file. `test_c55.py` carries the new coverage.

5. Prove both directions on real `EventEnvelope` validation, not on a copied regex and not in the reducer: accept the exact literal, reject the lookalikes above, and still accept an ordinary three-segment type. Fold that validated literal through standalone `fold_attempt` and pin story identity the same way C54 and C02 do. Leave installed composition to C56.

6. Dispatch, unknown-field policy, and other schema constraints stay unchanged. If the envelope pattern is the schema source, this alternation is the schema change. If a hand-written schema repeats the pattern, it needs the same single anchored alternation in this change.
