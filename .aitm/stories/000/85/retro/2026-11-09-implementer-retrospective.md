# #85 U02 · Scope inbox and provider-session binding · Late retrospective

I implemented U02 and wrote and signed this retrospective on November 9, 2026 (America/Chicago), after the historical Done checkpoint. [Story](../story.md) · [Planning events](../events.jsonl)

## Design, plan, and delivery

I implemented the amended scope contract on the reviewed #84 ledger base. The CLI published typed, project-authenticated commands while the collector held the writer lease. The collector committed each effect and its disposition together, acknowledged after commit, and replayed from the durable receipt. Fixture-proven request and turn boundaries governed scope, and explicit corrections preserved earlier as-of results. [Design](../design/design.md) · [Implementation plan](../plan/implementation-plan.md) · [Accepted amendment](../../83/plan/usage-capture-replan.md)

Independent off-platform agent review accepted the exact leaf head `67e888d720e67cb99e6e019fa1f0b6dc7510f40e`. My local verification passed 101 locked package tests, including 32 scope cases. U02 shipped in the integrated PR #97, whose independently reviewed head was `00ccef89e1e0bd541981b4a367d005f699c63769`. Later provider work repaired the Desktop carrier under #88 in PR #98 at reviewed head `699bd901ffd761dfaf28eeac0be25d04791cb416` and the Claude startup scanner under #87 in PR #99 at reviewed head `239a863c97bd7de3af66934f41fffcdacab985fe`. GitHub recorded zero CI checks and zero submitted native reviews on the three PRs. #96 separately verified the installed PR #99 merge on the project Mac, including both marker arrival orders on both providers. [Leaf source review](../plan/source-review.md) · [Protected source delivery](../../83/attachments/source-delivery.md) · [Installed activation](../../96/attachments/activation-summary.md)

## What worked, misses, and lesson

The CLI lease, publication race, and interrupted acknowledgment tests exercised the handoff through real SQLite state. My first candidate still let a plain development marker bypass the owner binding, mishandled generation order and pending boundary evidence, and made the common drain assume a single scope effect. The first repair also missed that an already admitted observation can gain request or message IDs after a rebind. The final repair follows the immutable admitted key and leaves ambiguous or newly seen old-stream observations Unknown. I would test delayed proof, cross-stream rebinds, and enrichment of the same admitted observation together before the first review. [Independent review and repair record](../plan/source-review.md)

**Confidence** 4/5. The exact source review, local replay tests, and subsequent installed qualification support the delivered behavior. The leaf itself established ordering with fixtures, and the separate-process crash proof belonged to U12. [Leaf source review](../plan/source-review.md) · [Installed activation](../../96/attachments/activation-summary.md)

**Timing** The original implementation interval was 18m 37s. The original and two repair intervals totaled 24m 24s of observed elapsed time. Independent review and activation were separate. Exact active agent time is Unknown. [Source verification](../plan/source-review.md) · [Planning events](../events.jsonl)

**Signed** `/root/implement_u02`, original U02 implementer, November 9, 2026 (America/Chicago). This is my post-closure assessment of the exact reviewed leaf source and its recorded integrated delivery and activation. [Leaf source review](../plan/source-review.md) · [Protected source delivery](../../83/attachments/source-delivery.md) · [Installed activation](../../96/attachments/activation-summary.md)
