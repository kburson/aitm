---
kind: draft
slug: peer-review
title: ai-peer-review — caller-chosen output location, possible rewrite on the new stack
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: peer-review
package: aitm-peer-review (bridge) + ai-peer-review (separate repo)
depends-on: [aitm-core]
---

# Draft: ai-peer-review integration

## Known

- Designs and plans are reviewed at several levels: SAR, SPR, XPR (assumed: single-agent, same-provider peer, cross-provider).
- ai-peer-review must let each review session write to a caller-chosen location, so collateral lands in `.aitm/stories/<bucket>/<id>/{design,plan}/reviews/`.
- Each review records the `planning` commit SHA of the document it reviewed.
- Because the user does not read designs or plans, these reviews are the safety net before delivery; XPR matters most.
- A rewrite of ai-peer-review on the new stack is a candidate first enforcing consumer of the released core.

## Open

- Refactor in place, or rewrite in Python?
- Confirm the SAR / SPR / XPR definitions.
