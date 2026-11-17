# #368 live macOS runner and tracing findings

**HOLD at the runner’s tracing prerequisite for the exact reviewed comment-only closure.** The live guest passed the offline configuration and protected worker filesystem checks. Stock DTrace could not start the required process observer. Candidate-code resistance remains unqualified. No product tests ran.

This attempt resumed after the owner accepted the license and authorized setup. It used the same isolated macOS 26.6.2 guest, build `25G83`, with APFS and SIP enabled. The VM readback showed zero network adapters and zero directory shares. The [accepted plan](2026-11-16-368-protected-local-observation-plan.md) and [prior license checkpoint](2026-11-16-368-qualification-results.md) record the scope and provenance. [Machine receipt](../attachments/2026-11-16-368-live-tracing-receipt.json) at SHA-256 `8ce2d863cd77d50a5304a93461a08244b6fcc7798d0b2f48690738d3e7418bed`.

## Live isolation

The verified diagnostic medium mounted read-only. Hardware interfaces reported no active links. The four IPv6 default entries were interface-scoped, link-local `utun` entries. Five unscoped route lookups checked both address families and returned a negative routing diagnostic. The worker also ran under a sandbox that denied network operations. The root controller admitted the staged binary and launched UID 502 for the filesystem checks.

The worker could read the admitted input and write to its scratch directory. It was denied writes to representative configuration, assignment, runtime and test source. It was denied read and write access to the raw evidence, verdict and controller sentinels, and the sandbox denied a write to the world-writable sentinel outside scratch. The controller verified all nine preflight content hashes. This establishes the bounded isolation controls that were exercised. The tracing prerequisite still governs overall runner admission.

Two earlier helper runs stopped on route interpretation. The first treated every displayed default row as an external route. The second treated exit status zero as proof of a usable route even when Darwin returned `not in table`. The final pinned helper checks the row scope, hardware links and the route response. Its parser controls accepted the captured negative response and refused both a positive interface and an ambiguous error.

## Tracing stop

The root controller launched stock DTrace for the planned benign process create, exec, exit and user-space trace check. It refused the program during compilation with `proc:::create` matching an unstable set, so the tracer emitted zero rows and the benign trace child was never launched. A separate root `dtrace -l` inventory exposed 16 entries, three from `dtrace` and 13 from `profile`. It exposed zero `proc` or `syscall` entries. The DTrace diagnostic reported SIP enabled and warned that some features were unavailable. The evidence establishes the limit of this exact guest configuration.

The accepted plan stops before an instrumented Python build when the early tracing prerequisite fails. Consequently, live outcome calibration and assignment admission remain unqualified. The previous static replay evidence identifies the 30 archived IDs. This attempt ran zero of them and recorded zero live assignment outcomes.

## Evidence and disposition

The controller exported the logs and hashes from the guest. The host mounted the guest data volume read-only, matched the exported manifest, and detached the disk. The machine receipt pins the guest identity, test inputs, trace program, raw trace and provider list. The guest remains shut down with private evidence retained. The resumed wall-clock charge was 0.225 hours, bringing the conservatively charged admission total to 0.708 hours of the 2.5-hour preflight limit.

When the initial guest process returned zero after its deliberate shutdown, my console checks tried to relaunch the scratch app without its required arguments and generated crash alerts. The corrected launcher returns a usage status for that invocation. I used the same guest identity for the successful reboot and live preflight.

Keep #368 open and #355 blocked. To resume under this plan, an approved macOS runner and observer configuration must expose and demonstrate the required live process and user-space probes with the documented trust boundary. Candidate-code resistance remains outside the bounded proof.
