# Platform requirements for AITM Usage

AITM separates portable effort reporting from the native usage monitor. The
package ships one pure-Python wheel. Building a report, reopening an immutable
artifact, exporting a Core fixture, and parsing saved provider records use
standard Python, SQLite where needed, and Git. Ubuntu runs the default signed
PR gate and the installed-wheel effort suite. This covers the full report
and export behavior for ordinary changes.

## Native requirements and their checks

| User requirement | Linux | macOS | Windows |
| --- | --- | --- | --- |
| Notice local transcript changes without scanning every payload. Recover safely when a watched directory disappears or events are dropped. | The monitor listens through inotify. The Linux suite exercises the watcher and recovery. | The monitor uses FSEvents and the native event loop. The focused macOS workflow exercises real events, dropped-event recovery, and callback teardown. | The portable effort commands are supported by fixtures. The native monitor has no Windows watcher. |
| Keep private state and writer custody safe when a directory or file changes. | Check Linux ACLs, use the account state directory, and publish with `renameat2`. | Check Darwin ACLs, use the account Application Support directory, and publish with `renameatx_np`. The focused macOS workflow checks the ACL and atomic rename paths on the host. | The native monitor's ACL and atomic-publication safeguards are unavailable on Windows. The portable effort CLI uses its separate storage and export boundary. |
| Capture claims about real Codex Desktop turn and child callbacks. | Parse saved hook payloads and retained transcripts in shared fixtures. | Verify actual callback delivery, shutdown, and recovery in the supported Desktop host when those integrations change. Use an app-enabled environment for that check. | Parse the same saved payloads and transcripts. A live Desktop claim needs evidence from the target client and host. |
| Reopen and export byte-identical results after installation or Git checkout. | The installed effort suite checks canonical bytes and digests. | The same wheel and shared fixtures apply. | Git checkout can convert LF to CRLF, and text stdout can alter line endings. The focused Windows job verifies a pinned rate-card digest and both report and Core export bytes through fresh CLI processes. |

## When to run a platform job

The macOS and Windows workflows run on PRs that touch the implementation or
tests behind their specific checks. They also support manual dispatch for a
change in a shared dependency or for release qualification. Apply native
evidence to the feature being qualified. For an ordinary portable change, the
Linux gate supplies the delivery evidence.

The daily hosted category sweep assigns shared cases to Linux and retains
Darwin for native and Darwin-only cases. The APFS shadow workflows are manual
diagnostics for historical comparisons, separate from the PR delivery gate.
The hosted macOS filesystem job covers filesystem behavior. Live Desktop
qualification needs an app-enabled host.

[Repository CI and verification](ci.md).
