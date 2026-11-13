# Epic dependency maps: draft builder check

On November 12, 2026, an independent Codex builder checked the initial 57-line draft (SHA-256 `511b290c434ccf9fa03830a4e87a1444b2835d8d0cba42e1a1a06859d809c444`). This was a preflight to find decisions the design needed to make. It was not formal Design or Plan acceptance.

| Question raised | Disposition in the revised [draft](draft.md) |
| --- | --- |
| Which audience may see committed bundles and audit paths? | Generate privately; attach only a bundle reviewed for the same authorized audience as the epic plan. No CLI publishing mode. The M6 preview allowlist does not by itself authorize publishing graph data. |
| What does expansion mean for a flat epic, and how far can a focus view follow external dependencies? | Expand or collapse dependency branches within the selected epic, preserving shared nodes. Navigate to a nested epic's map separately. Stop at direct cross-epic links and follow approved links for further context. |
| Do static maps refresh automatically or gate acceptance? | Static refresh is on demand. The interactive graph redraws on the existing successful viewer refresh. The bundle is a standard review artifact, with no new automation or acceptance gate proposed. |
| Which gaps hold generation? | A missing or invalid in-scope input or a cycle holds replacement. An unavailable external record can be marked as an unresolved boundary when the link is known and visible to the audience. |

The reviewer read back the #133 pilot graph: 41 members, 64 child dependency edges, 55 displayed after reduction, no child boundary edges, and the separate #133 → #2 gate. The author also ran the existing planning reader at both candidate refresh pins. It reported #142 as Plan at `05d3330` and Develop at `ea4a838`; the epic had 41 children at both pins, and no dependency fields changed.

The proposed M6 follow-on placement, backlog attachment convention, and view behavior remain for design review. No issue, acceptance record, release dependency, or implementation change was made.
