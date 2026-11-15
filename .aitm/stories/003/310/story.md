---
schema: "aitm.story/v0"
id: 310
title: "Create verified journal-only publication candidates"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/310"
parent: 100
children: []
blocking: [119]
blocked-by: [300]
created: "2026-11-15T11:51:18Z"
updated: "2026-11-15T11:51:34Z"
last-branch: "planning"
estimate: {"agent-hours": 1.25, "size": "S"}
priority: null
origin: ".aitm/stories/001/119/plan/2026-11-15-119-destination-writes-split.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind":"accepted-parent-plan-amendment","source-story":119,"key":"M09a-VerifiedJournalCandidate","publication":"8dc31ef187963dde928b474e64e3b690e78eef90","raw-sha256":"3c05590d7d951bba947396d1d725ae3a9735b7b255336f499e3b3ce14a331163"}
---

# Create verified journal-only publication candidates

Project 24 Rank 229.9. Implement the M09a contract from the [accepted split](../../001/119/plan/2026-11-15-119-destination-writes-split.md), independently reviewed at the exact linked revision. The implementation estimate of 1.25 hours is provisional pending independent Refine and JIT. The existing recovery fence remains #122.

## Independent Refine

Passed at 1.25 implementation hours. JIT will freeze complete committed row identity and verify candidate isolation. [Verdict](plan/independent-refine-r1.md).

## Independent JIT

Recovery passed at 1.25 implementation hours. The exact plan pins the journal SQL, schema gates and non-persisted identities. [Verdict](plan/independent-jit-r2.md).

## Local Test

Exact locked validation passed for the read-only candidate and destination-isolation path. [Evidence](plan/local-publication-test.json).

## Independent source and recovery

Initial source review held on tests for future schema, full-row substitution and noncanonical-but-decodable stored bytes. The updated test-only candidate returned to Test. [Initial source receipt](plan/publication-independent-source-r1-receipt.json).

## Exact recovery

The refusal tests passed on the exact local and signed hosted candidate. Independent source recovery returned **PASS**. [Source receipt](plan/publication-independent-source-r2-receipt.json) · [Signed Test](plan/publication-signed-hosted-r2.json).
