# #2 governed PR and working-branch lifecycle SPR author disposition

The independent manual SPR requested six changes at
`123e08304bdfe94ae4eac83f6b93a9a3e2822c79`. The revised source
commit is `73bcd9ed37fc3f6967a9af5bc4aafb50c0480271`.

| Artifact | Revised SHA-256 |
| --- | --- |
| Specification | `c1a9e4b6122871a66e02aac1b9ad9f762df2f52b6ba848d035f354e4f066370f` |
| Plan | `56bf58bd263c5e451dfa30e02d74cf8050b0a7bd68ff18dbb958da21c61fd3bc` |

| Finding | Author disposition |
| --- | --- |
| SPR-PR-01 | Follow #133's draft convention with readiness ordered at broker dispatch. Reconcile an earlier sent request against actual status. Core owns independent readiness qualification and holds integrated repair if it is unavailable. #158 retains host mutation enforcement. This replaces the stronger provider-ready ordering considered during SAR. |
| SPR-PR-02 | Use one CAS lifecycle slot and exclusive literal host resource ownership. Distinguish unsent from outstanding effects and fence old writes before reuse. |
| SPR-PR-03 | Apply the target's policy when roles overlap. Use C41 for reviewed component delivery and a separate expected-head, provenance-bearing admission for authorized refresh or permitted owner work. |
| SPR-PR-04 | Define separate Backlog, resource and delivery relations. Include the designated upstream delivery in required epic scope, with a positive acyclic stage order and explicit scope resolution or replacement. |
| SPR-PR-05 | Separate the #158 synthetic host boundary from the end-to-end CI test that consumes delivered #133 producers. Add an explicit negative readiness dependency trace. |
| SPR-PR-06 | Require verified conversion to draft before an already-ready PR can retarget. Reconcile ambiguous effects and require fresh target-specific admission and CI. |

The published #133 and #158 artifacts are review context and retain
their exact bytes. This records a Core planning proposal.
