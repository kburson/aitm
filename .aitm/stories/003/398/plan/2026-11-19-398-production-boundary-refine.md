# #398 bounded production input refinement

## Outcome and scope

Qualify the existing `packages/aitm-usage/tests/test_grok.py` target against a change to the private `_headless_tokens` decoder. This is an advisory experiment with traceable test evidence on GitHub-hosted Ubuntu. Scope is one production function, three draft candidate trees, and an isolated qualification harness. Required CI, map, gate, policy, verifier, protection, pinned #355 entry point, and trunk retain their roles. Deliver findings under #370.

The exact reference is trunk `f2ff2b6f073fa769261b44fb0c05a055da7eb1c9`. Prior work #393 qualified a test-body edit. A shared Grok adapter or fixture change required full. #383 supplies the existing staged-index, HEAD, and PR resolver. This experiment uses the PR input and leaves those adapters unchanged.

## Candidate ownership and conservative rule

`_headless_tokens` receives a record only through `_NativeWalk.check_headless`. The guard returns before calling it unless an optional `read_headless` callback returns a matching completed record with complete usage. `GrokAdapter._read_delta` and `GrokAdapter._capture_material` pass that callback to the walk. Monitor callers and cross-suite fixtures use the adapter or construct its reader without supplying a headless callback. The replay test's `_batch` passes a callback when testing headless corroboration. Sharing the adapter or importing `grok_source` does not execute the gated decoder. Audit runtime evidence in both the product and helper groups, including child coverage under the repository's subprocess coverage configuration. Hold the qualification if a decoder line is observed outside the target or in an unattributed context.

Declare the candidate against the exact reviewed base. Permit one regular-file modification with bytes outside the existing decoder function body unchanged. Admit only the reviewed constructor refactor body and the separately identified seeded control. The candidate body can neither introduce new dependencies nor modify callers, argument flow, use of mutable state, or other definitions. Shared, mixed, renamed, unreviewed, or out-of-boundary edits select full. Invalid or stale Git identity is unavailable and incomplete evidence holds the result.

## Evaluation plan

| Case | Expected decision and observation |
| --- | --- |
| Positive production edit | Replace the positional constructor in `_headless_tokens` with equivalent keyword arguments in evaluation order. Select the entire existing replay suite. Its outcomes must match the exact full run, with a material lane-time saving. |
| Seeded production regression | Swap cache-read and cache-creation keys in the same reviewed body so the total stays valid but the categories disagree. The existing replay assertion fails in the selected and full lanes, with no additional failures. |
| Related shared change | Change the shared `GrokAdapter` docstring. Select full because this is outside the decoder boundary. |
| Negative controls | Refuse wrong tested tree and stale head. Reject a truncated full phase receipt. |

Use #383's exact resolver, verify both ordered merge parents, and recheck the snapshot digests after execution. Use the base-owned path map as a read-only comparator. Collect actual pytest IDs at execution. Compare complete per-node outcomes on the same tested trees and runner per case. Capture setup, selection, and elapsed workload time with matched product coverage instrumentation and independent scratch. Keep interpreter provisioning and job queue outside the lane timers. Preserve test contexts for the decoder and require it to be reached by the replay suite. The result qualifies this declared change only.

## Estimate

Retain Size M and 3.5 implementation agent-hours. Allow 0.75 for refinement and boundary proof, 1.0 for shadow cases and harness adaptation, and 1.75 for hosted replay, reconciliation and reporting. Reconsider scope before adding shared production paths or extending the acceptance matrix beyond this bounded pilot.
