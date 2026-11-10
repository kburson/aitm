# TIA build optimizer deployment follow-on plan

Proposed work after base product proof. Use the
[enhancement design](../design/independent-deployment-enhancement.md)
and [accepted implementation plan](test-impact-analysis-implementation-plan.md)
as separate inputs.

| Candidate story | Result and verification |
| --- | --- |
| Independent distribution | Stage a versioned optimizer artifact and configuration. Install into a clean non-AITM test repository, without Core. Prove selected witnesses, full fallback, qualified sharded receipts and compatibility across upgrade. Exercise approved hosted authority separately on a disposable target. Split hosted and CLI proof if needed to stay within the four-hour leaf cap. |
| Optional Core adapter | After independent distribution and the released Core extension contract are proven, qualify committed opt-in against pinned versions. Exercise disabled and enabled modes, stale/mismatched candidate or policy, unavailable authority, and a live-stop rollback. Preserve exact evidence and fail closed where policy requires it. |

Refine and review this enhancement separately after base qualification.
Choose the release channel, compatibility range, supported runner
matrix and release authority then. Deployment, required-gate activation,
and workspace enrollment each need their own evidence and authorization.
