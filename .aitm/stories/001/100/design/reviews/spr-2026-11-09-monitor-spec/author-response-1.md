# Author response to SPR round 1

All nine required findings were accepted and addressed. The revised spec SHA-256 is `8d1cb75bba54a38c2344fd9024a839e132b60f6d77475aaae7946c4f746454fe`.

| Finding | Disposition |
| --- | --- |
| 1. Handoff | Seal the current generation and exact next native boundary, distinguish retries from competing proposals, specify chained stale-anchor handoff and hold resolution. |
| 2. Registration | Enforce per-stream effective boundaries, preserve justified pre-disable revisions, stop revoked reads, and exclude disabled intervals on re-enrollment. |
| 3. Legacy view | Record a verified ledger sequence as the initial publication baseline. Require normal ACKs for later writes and preserve independent replay fencing. |
| 4. Older restore | Reconcile later trusted scope, publication and export receipts before affected replay. Surface irrecoverable spans and allow an explicitly verified prospective baseline. |
| 5. Saturation | Bound each destination and reserve capacity for independent streams. Expose and replay a shared stream stalled at a replayable boundary. |
| 6. Revisions | Require proven supersession and lineage comparison in both the destination and ACK. Hold incomparable data and preserve the published revision on stale delivery. |
| 7. Reports | Use the immutable native start boundary or stored legacy time. Pin interval, rate card and basis to the report view. |
| 8. Grok | Define missing and conflicting evidence, constrain folded overlap, and qualify concurrent, interrupted, forked, rewound and late data before admitting affected usage. |
| 9. Linux | Define initial Linux architecture and filesystem qualification, user-manager lifetime, exact runtime and heartbeat proof, and fail-closed preconditions. |

The revised verification cases explicitly cover registration changes, competing handoffs, first-report parity, older restores, queue exhaustion, stale revisions and pinned pricing.
