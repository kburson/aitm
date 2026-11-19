# #370 suite-level hosted integration decision

**Continue isolated hosted Ubuntu shadow qualification. Hold routine hosted integration.** The suite-level approach has demonstrated useful narrowing while preserving outcomes in the declared cases. The current declarations cover fixed, tightly reviewed inputs. Routine hosted advisory integration needs a repeatable way to admit fresh changes and detect when a base advance invalidates an earlier boundary. The required gate continues to use the current path map and workflow.

| Evidence | Qualified scope | Same-tree result |
| --- | --- | --- |
| [#393](../../393/story.md) | An edit confined to one declared test body | 33 tests in 3.564 seconds versus 1,776 in 274.003 seconds. The seeded failure matched, and shared fixture and source inputs selected full. |
| [#398](../../398/story.md) | Two exact reviewed versions of the headless decoder source on one pinned base | 33 tests in 4.316 seconds versus 1,776 in 338.504 seconds. The seeded failure matched, the shared adapter edit selected full, and raw coverage attributed decoder execution to the replay target. |

Both experiments used #383's exact PR snapshots, preserved full outcomes on the same tree, and produced no missed failures or mismatched selected outcomes in their declared cases. Both caught invalid PR identity and incomplete evidence. The #398 rule uses exact reviewed candidate hashes and rejects other bases. The two pilots qualify their pinned inputs. They leave ordinary PR and base turnover unqualified.

## Next story

[#402](../../402/story.md) will qualify a reusable declaration for the same suite on a fresh bounded production edit and after an unrelated base advance. Verify the evidence that permits reuse, and prove fallback on relevant input or dependency drift. Compare assignment, outcomes, and lane time with full Ubuntu controls and the current path map. A successful result informs a separate decision on routine hosted advisory integration. Promotion to merge authority remains a separate decision.

[Hosted #393 findings](2026-11-19-370-grok-suite-shadow-findings.md) · [Hosted #398 findings](2026-11-19-370-bounded-production-shadow-findings.md)
