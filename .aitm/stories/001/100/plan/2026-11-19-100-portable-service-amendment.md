# Portable service amendment

Owner direction on 2026-11-19. The monitor that tracks agent cost stays one Python program. The host supplies CPython 3.13. Linux and macOS run that same program. This amendment supersedes the M15 sentences that require a LaunchAgent or a systemd user unit, and the service registration that is an Apple plist. The accepted plan excerpt on #125 stays as the record of the original leaf.

## Service

`ServiceSupervisor` starts `python -I` on the approved wheel and passes the project root. The `#!/bin/sh` launcher at `bin/aitm-usage` may remain as a convenience script. The service does not require that script. The script is not a compiled product binary.

The registration file is the JSON record the supervisor writes for the running child. It holds the argument list, the interpreter path, the start time, and the heartbeat socket. `RunAtLoad` and `KeepAlive` are not fields in that record. An Apple plist, including a binary operation log, is not the registration.

The running service is that record plus a fresh heartbeat from the same user. On Linux the process walk reads `/proc/<pid>`. On Darwin the process walk reads `proc_pidinfo` and `proc_pidpath`. A scope hook from a Grok session the person started still passes that walk. The supervisor does not launch Grok.

The supervisor does not call `/bin/launchctl` and does not load a user manager. Login restart, a LaunchAgent, and a systemd user unit are a later epic. An absent user manager is not a failure of #125.

Refuse an insecure private directory. Refuse a second service, or a legacy writer, that still holds the writer guard. The production activation path still refuses without the M16 cutover receipt.

## Tests

Product tests of this service run on the Linux runner. A developer machine may be a Mac, and that Mac runs the same program. #128 remains the qualification of the Mac Codex Desktop carrier. #129 remains the Linux carrier qualification. This amendment adds no blocker edge to #374 or #377. #374 removes `launchctl`. This amendment replaces the plist that removal would otherwise leave in place.

The systemd-bus and linger check leaves this leaf. The leaf proves the JSON registration, start, stop, and restart, that a stale pid does not certify readiness, and that a second service or legacy writer is refused.

## Unchanged

Cost accounting, journals, scope markers, reports, exports, and the qualified carriers stay as accepted. #125 stays blocked by #121, #124, #304, and #320. #125 still blocks #126. #320 still owns the native wake-hook installers. Those installers are provider hook files, not this service registration. Epic #100 stays in develop. Its children stay as recorded. No new story is opened.
