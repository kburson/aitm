# #100 specification self-review

Review level SAR. Author and reviewer are the same Codex session. Reviewed at `2026-11-10T02:53:58Z`. The two evidence spikes were published and closed before this review.

| Evidence | SHA-256 |
| --- | --- |
| Draft input | `f0e5f6ebe632b57185ae6d61a8fdaf0f96529844f7e110570240c88fec8fb53b` |
| SAR result | `5f81246590556e8207ff193db524267d235a7a7a31c63e1d28ee947d2bb656c1` |
| Grok report | `34a27af1e20669f5ec5bd23dc0c1424d3ba3a5750f33c7d3fd1f132b529e2164` |
| Linux report | `3edaf8c02ca28a6695eae4783983522320e88725587b28819b03bacc0f5a7f7a` |

## Findings and dispositions

- **SAR-1, evidence and cost.** The previous draft still described the Grok authentication block. Record the verified 1.0.77 whole-turn join and stable replay. Keep scope proposal authority, provider tick pricing and release qualification separate.
- **SAR-2, routing lease and failure isolation.** The first draft specified one service but omitted a service-wide writer lease and a bounded response to an unavailable destination. Specify the lease, preserve durable claims, and defer without advancing a cursor across unstaged evidence. Other projects stay available.
- **SAR-3, scope authority and freshness.** Differentiate an owner-approved scope proposal from a wake event and native proof. Document the OS-account trust boundary. Correct the handoff example so it allocates usage on either side of the boundary consistently.
- **SAR-4, repeatable reporting and recovery.** Add precise time-window semantics and a pinned snapshot identifier for drilldown. Require coordinated backup and reject mixed restore state.
- **SAR-5, platform scope.** Preserve exact Linux user-service, ACL, watch and publication obligations from #102. Host qualification is specific to provider surface and evidence, including the Codex CLI marker.

All SAR findings were resolved in the result above. Independent SPR and XPR apply to the resulting exact artifact and subsequent accepted revisions.
