# #368 local qualification findings

**HOLD at runner admission for the proposed exact reviewed comment-only closure.** Candidate-code resistance remains unqualified. The new offline guest installed successfully and booted into Apple Setup Assistant. The first-boot screen still displays the software license notice, and owner confirmation or completed setup was pending at 2026-11-17T02:46:12+00:00.

The [accepted plan](2026-11-16-368-protected-local-observation-plan.md) is pinned at SHA-256 `f4ed0b50d49da73ed5b4f541a26ee4e2d4b00cb2e01a1d20db2182691c7d346a`. The [machine receipt](../attachments/2026-11-16-368-qualification.json) records this checkpoint at SHA-256 `c7e9689d56d7a4f5e046398c2a5773f4b8958e7c72ddfc07b5109ba7daedd620`.

| Gate | Findings |
| --- | --- |
| Protected runner | Live host-side provisioning completed. The installer validated the VM with zero network adapters and zero directory-sharing devices. The VM reached the first-boot language screen and license notice. The fresh account, APFS and SIP readback, restricted worker and protected path controls all await guest setup. |
| Independent observer | Recovered the prior authenticated #146 source and matching archived hosted proof. The local OS process and USDT capability probe awaits guest setup and worker isolation preflight. Local independent outcome observation remains unqualified. |
| Scoped assignment | The exact archived 30 IDs and pinned source were rechecked statically. The trusted delivered CLI replay, mandatory and child applicability review, manifest and independent scoped assignment admission are pending. Zero assigned product tests ran. |
| Integrated proof | The positive, negative and replay controls await runner, observer and assignment admission. |

## Runner and observer evidence

The host is Apple Silicon and reports macOS 26.6.2 build `25G83`, APFS and SIP enabled. The disposable guest uses Apple Virtualization.framework with the Apple restore image for that same build. The framework reported install completion at 2026-11-17 02:40:33 UTC. The downloaded restore image is 19,772,231,540 bytes at SHA-256 `885503b7f4b06609e9a512f2befd40f59730640a3f1233e3892d60affdd51c95`. A manifest identifies the scratch VM controller, the read-only diagnostic disk, the benign USDT emitter and the preflight script. Apple’s official Virtualization interface supplied the supported restore image metadata. [Apple macOS VM installation](https://developer.apple.com/documentation/virtualization/installing-macos-on-a-virtual-machine)

The guest console observation establishes first boot and the license checkpoint. The owner was asked to review the notice, then either authorize continuation or complete setup with a disposable guest-only administrator. The guest is available at that prompt. The approved execution route uses guest-local root only for evidence custody, role setup and tracing with guest protections intact. The exact guest APFS/SIP, root and worker role readbacks and allowed and denied operations still require live evidence.

The authenticated [#146 hosted run](https://github.com/kburson/aitm/actions/runs/43366344563) was tied to commit `1419e3592d36cf90853664c2f22eb41bb26c1cef`. The downloaded archive and receipt matched the retained SHA-256 values in [#146 full-suite observations](../../../001/146/plan/full-suite-observation-findings.md). That proof qualifies its hosted configuration. This spike has prepared an isolated diagnostic to observe process creation, exec, exit and the USDT marker under the actual guest worker identity and reconcile OS wait status. The diagnostic has yet to run.

## Assignment evidence

The decompressed #344 inventory archive matched `812bc918dd9da7b413786454906d2ec8f486b5624bc8d1deecf9d546928d48e6` and contained 30 distinct IDs in the pinned Grok scope-receipt module. At commit `8218a69ad6d9d9f33c6383bd5a6cd4930bef21d7`, AST inspection found 22 archived nodes with direct or staged arguments for the imported `isolated_grok_capture` fixture. That fixture has two `/usr/bin/ssh-keygen` call sites. The six hosted mandatory IDs belong to other modules, and the local suite catalog has no module classification for this assignment. The receipt lists the two hosted native-child bindings and local overrides. This locates inputs for formal scope admission. Actual child launches, per-ID requirements and the test outcomes remain unobserved.

## Disposition and resumption

Keep #368 open and #355 blocked. Once the owner completes or authorizes guest setup, resume at runner admission. Read back guest APFS, SIP and the isolated configuration, then run the staged sentinel and tracing probe using the disposable guest roles. Build an instrumented runtime only after that check passes, and obtain independent approval of the exact assignment and executable closure before product execution. A PASS for the reviewed closure will still leave arbitrary candidate-code resistance outside the qualification.

The Parallels CLI created an empty stopped VM when asked for command help. It was removed by its exact UUID and the preexisting suspended VM was verified. The intended Apple Virtualization guest and its scratch evidence have been retained for resumption.
