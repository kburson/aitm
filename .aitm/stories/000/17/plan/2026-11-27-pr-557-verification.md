# PR #557 local verification

Base `0438d1fa749ec46b9798f4068bd0e36c548c02ef`, head `31947a26e24d355b31e2c8a750d839ff57c7f26a`, synthetic merge `b2ba4247bd15d4a031d796a189cac327720b5c5c`, tree `efb28b36c292615c33ba2e66d0278d69b881925a`.

The installed describe test first failed because local completion left publication pending. The focused C09 suite then passed for default publication without a flag, two-clone disjoint replay, authored and related-story conflicts, policy conflict, both lost-ack outcomes and retry. Conflict resolution verifies the exact shared tip and preserves the original recovery ref. The macOS full unique Core collection contains 756 unit tests and 61 integration tests out of 817. The floor remains 92%. Ruff check and format check passed. Hosted repository run #46053667930 and separate Core run #46053667908 were triggered for the exact draft candidate.

## Revised candidate after source review

Head `a15df65a40c543e4d82f0413a492bb577e05290c`, synthetic merge `419e056ade08020993bf2263102b5e34e7d34bd3`, tree `36573bd265c210655cfd3f6b7195725976c5b8dc`. [Round 1](2026-11-27-pr-557-source-sar-r1.md) requested changes on the preceding candidate. Four race scenarios reproduced failures when their strengthened assertions ran against that earlier source. The revised candidate keeps a completed local result on conflicted retry, distinguishes selecting the shared prefix from publication of a discarded operation, keeps the exact replacement request with separate durable supersession evidence, retains deferred action IDs during disjoint replay without dispatch, and refuses corrupt or uncovered journal input with recovery retained. Both hosted runs started again from draft. Repository run #46055141986 and Core run #46055142337 qualify only this new candidate.
