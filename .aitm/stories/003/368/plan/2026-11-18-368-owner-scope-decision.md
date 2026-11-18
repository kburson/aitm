# #368 owner scope decision

The owner directed this close on 2026-11-17: "Do that. Close 368 and unblock 355."

The investigation is complete. The deliverable is the Opus-accepted HOLD from the queue-inclusive hosted run. A PASS of the three original gates was not met, and this decision does not relabel that HOLD as a PASS.

## Accepted result

[Queue-inclusive findings](2026-11-17-368-queue-inclusive-run-findings.md), artifact SHA-256 `e5b0a68a1c222db44adce3490a9331b8eea22506bb7198544f89bda3f5c9d360`. Opus 5.5 at high effort accepted the HOLD in review `review-878d48dc52fb7e3aa45b7e4d0000888f` with no required changes. [Machine receipt](../attachments/2026-11-17-368-queue-inclusive-run-receipt.json). [Failure excerpts](../attachments/2026-11-17-368-product-failure-evidence.json). [Hosted run 44090243525/1](https://github.com/kburson/aitm/actions/runs/44090243525/attempts/1).

The hosted runner observed all 30 assigned outcomes and all 74 direct native-child lifecycles. Ancestry readbacks matched, and the eight targeted denials returned EPERM. Fourteen tests passed through teardown. Sixteen failed. Fifteen IDs failed transcript discovery: directory open is denied on `/`, `/Users`, and `/Users/Shared`, so the pinned locator unpacks an empty result. The native process-custody test failed because the worker was UID 550 and its direct parent was UID 0. The same 30 tests passed outside that sandbox in 6.2 seconds (`diagnostics.local_suite_control` on the receipt: passed 30, failed 0, Python 3.13.9, pytest 9.2.0, pluggy 1.7.0).

The disposable local guest could exercise local isolation. Its DTrace inventory had no usable process provider, so that route ran zero assigned product tests.

## Claims that stay unqualified

These claims remain written here and stay outside #351:

- A strict trusted verdict for the pinned suite under the listing-denial and separate-UID parent policy.
- Protected local execution with a usable process observer.
- A separate-user sandbox that can run this suite.
- Resistance to unreviewed candidate code.
- Post-run custody on the hosted strict route.
- Candidate inventory and impact completeness.

An exact-head repeat of the hosted policy hits the same transcript-discovery and parent-UID conditions. No further sandbox revision is authorized on #368.

## Scope #355 carries forward

#355 delivers the cooperative advisory run described by the accepted #353 finding:

- a separate pytest process
- the operating-system exit of that process
- a complete receipt matched to the #354 list
- the receipt labeled advisory

#353 and #354 remain the accepted prerequisites. #368 stops blocking #355. #351 stays open until #355 delivers that advisory command.
