---
schema: "aitm.story/v0"
id: 304
title: "Authenticate controlled live-source qualification on isolated hosts"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/304"
parent: 100
children: []
blocking: [121, 125, 128, 129]
blocked-by: [303]
created: "2026-11-15T02:38:03Z"
updated: "2026-11-15T02:38:32Z"
last-branch: "planning"
estimate: {"agent-hours": 3.8, "size": "M"}
priority: null
origin: ".aitm/stories/003/303/plan/2026-11-14-303-isolated-source-issuer-amendment.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 303, "key": "M08b6-Isolated-Issuer", "publication": "79aecafe17c5dc0417fd00c2ecd37cdfe3651d58", "raw-sha256": "cbfbf8a37edf0d4114380928d991a696629f9d5954f33374fd8c0e87ac87b377", "issue-body-sha256": "ba83d3fe27c8d1a3640c5730285ba75dafbe90bbeb7b7a13964bb64ef653b8bf"}
---

# Authenticate controlled live-source qualification on isolated hosts

## M08b6-Isolated-Issuer

Epic #100 first-release controlled qualification issuer. Requires delivered #303. Directly blocks #121, #125, #128 and #129.

Deliver the real isolated qualification authority for the closed policy and decision contract. Verify exact provider executable and capture-root custody on a real controlled installation, and bind an authenticated versioned generation with writer-enforced expiration, supersession and revocation at reserve and retry. Only accepted non-Claude isolated carrier tuples may receive a grant. Keep the first-release catalog closed until independently signed target qualification, and preserve all existing gates and history.

Requires its own independently accepted Refine and JIT, signed hosted validation, independent source review, delivery and Close. Epic #2, C01 and production cutover are excluded.

[Accepted amendment](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/303/plan/2026-11-14-303-isolated-source-issuer-amendment.md) SHA-256 `cbfbf8a37edf0d4114380928d991a696629f9d5954f33374fd8c0e87ac87b377`.

Project 24 Rank 229.065.

## Independent Refine

Passed at 3.5 implementation hours with a single real macOS arm64 Grok pilot. The exact independent JIT binds the native witness and currentness contract. [Refine](plan/isolated-issuer-independent-refine-r1.md).

## Independent JIT

Two exact JIT reviews held. The recovery closed four findings and left admission provenance and reserve/retry coverage sign-off pending. The confirmation draft includes the retained admission predicate, source callers, and a four-case hosted proof. The accepted Project estimate is 3.5 hours and the draft proposes 3.8 hours. A further independent JIT review requires explicit authorization. [First review](plan/isolated-issuer-independent-jit-r1.md) · [Recovery](plan/isolated-issuer-independent-jit-r2.md) · [Confirmation draft](plan/2026-11-14-304-controlled-source-issuer-jit-r3.md).

## Independent JIT confirmation and Develop

The authorized confirmation passed at 3.8 implementation hours. The delivered #300 tree equals the separately reviewed candidate, including its existing first-read-only coverage recorder. Exercise single-candidate reserve unconditionally and prove the prior #300 recorder remains the only reachable decision-consuming path. [Exact JIT](plan/isolated-issuer-independent-jit-r3.md) · [Receipt](plan/isolated-issuer-jit-r3-receipt.json).

## Local Test and real pilot

The exact local candidate passed locked validation and the real isolated macOS Grok scope read and revocation test. [Local evidence](plan/isolated-issuer-local-test.json).

## Signed hosted Test

The candidate passed exact signed hosted Test and the unchanged policy. [Signed receipt](plan/isolated-issuer-signed-hosted-receipt.json) · [Policy replay](plan/isolated-issuer-hosted-policy-replay.json).

## Independent source hold and exact recovery

The first source review held. The recovery candidate binds the live pilot to its CI head and tree, documents the exact base and test inventory, and proves issuer activation, reachability and private refusal under the existing gates. [Hold](plan/isolated-issuer-independent-source-r1.md) · [Exact retest](plan/isolated-issuer-local-recovery.json).

## Signed recovery Test

The corrected candidate passed exact signed hosted Test and the unchanged policy. [Signed receipt](plan/isolated-issuer-signed-hosted-receipt-r2.json) · [Replay](plan/isolated-issuer-hosted-policy-replay-r2.json).

## Exact source confirmation

Independent source recovery held on the inventory, audit comparison and lexical handler evidence. The test-only correction passed exact local and signed hosted verification. A further source review awaits authorization. [Recovery](plan/isolated-issuer-independent-source-r2-receipt.json) · [Exact confirmation](plan/isolated-issuer-exact-confirmation.json).

## Owner-authorized source review

The unchanged source delta was refreshed onto current trunk. It passed locked local Test, signed hosted Test and the exact controlled Grok pilot. Independent source returned **PASS**. [Source receipt](plan/isolated-issuer-independent-source-r3-receipt.json) · [Signed Test](plan/isolated-issuer-signed-hosted-final.json).

## Close

PR #309 merged to trunk after signed hosted Test and independent source review. Native state is Closed Completed and the Project is Done. [Delivery](plan/isolated-issuer-verified-delivery.json) · [Native Close](plan/isolated-issuer-native-close.json).
