---
schema: "aitm.story/v0"
id: 335
title: "[M11f] Authenticate Grok scope marker receipts"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/335"
parent: 100
children: []
blocking: [121]
blocked-by: [182, 329]
created: "2026-11-15T22:59:53Z"
updated: "2026-11-15T23:00:08.136893+00:00"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "M", "scope": "provisional"}
priority: null
origin: ".aitm/stories/001/121/plan/2026-11-15-121-grok-scope-marker-amendment.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "source-story": 121, "key": "M11f", "publication": "07e17d80f7f4aa2ee6b2295b52c6225eae129f5b", "raw-sha256": "745f65c5e8549a9b7cdbbe30876b13b1c4551831771772c116dad3c62b68168d"}
---

# [M11f] Authenticate Grok scope marker receipts

[Native issue](https://github.com/kburson/aitm/issues/335) · [Accepted parent plan](../../001/121/plan/2026-11-15-121-grok-scope-marker-amendment.md)

Rank 249.75, provisional Estimate 3.75 implementation hours. #182 and #329 are verified closed. Obtain independent Refine and JIT for the writer and verifier. #121 owns the coordinator consumer.

[Refinement proposal](plan/2026-11-15-335-grok-scope-marker-refine.md) enters independent review against the current native owner, publisher and verifier source.

[Exact JIT](plan/2026-11-15-335-grok-scope-marker-jit.md) is submitted for independent acceptance.

[Independent JIT](plan/marker-independent-jit.md) passed with eight binding conditions and four verified source checks for exact trunk. Develop uses the three accepted paths.

## Test

The exact candidate passed 1,502 locked local tests. The focused regressions cover one-use publication, exact native marked and project-only hookless paths, physical ancestry, stale and wrong authority, the read-only receipt callback and prefix substitution. [Exact local Test](plan/marker-local-test.json) · [PR #336](https://github.com/kburson/aitm/pull/336).

[Signed hosted Test](plan/marker-signed-hosted-test.json) verified the same exact candidate and inherited controls. Independent source review is submitted.

[First source attempt](plan/marker-independent-source-r1-receipt.json) returned no accepted verdict. The exact test and review packet are preserved for recovery.

## Source review recovery

The exact candidate passed 1,504 locked local tests. The regressions cover revocation after a native read, original owner custody, and the typed duplicate hook refusal. [Exact local Test](plan/marker-source-r2-local-test.json) · [PR #336](https://github.com/kburson/aitm/pull/336).

[Signed hosted Test](plan/marker-source-r2-signed-hosted-test.json) verified the same exact candidate and inherited controls. Independent source review is submitted.

[Independent source recovery verdict](plan/marker-independent-source-r2.md) returned **HOLD** on the exact signed candidate. [Receipt](plan/marker-independent-source-r2-receipt.json).

The corrected candidate passed 1,508 locked local tests. A signed replacement or revocation before bind leaves the original attempt unbound. A competing descriptor cannot acquire the publication lock through first scope application. [Exact local Test](plan/marker-corrected-local-test.json) · [PR #336](https://github.com/kburson/aitm/pull/336).

[Exact signed hosted Test](plan/marker-corrected-signed-hosted-test.json) passed with the inherited controls. The corrected source packet is ready. The ordinary source attempts were consumed and another paid review requires authorization. Packet SHA-256 `dd24d475b472589a6a4b20864dfbb5cc4f3b011d77023c51dbdc5eda192365e8`.
