# Scratch-only Desktop route diagnostic preflight

The disposable Desktop repository has five modified commands for a diagnostic wrapper pinned by SHA-256. The wrapper records event name, whether the session matches the exact disposable chat, and whether a turn ID is present before applying the session filter. Its post-capture record adds the private adapter status. Raw identifiers and prompt content never enter the trace. The diagnostic uses a separate private scratch store selected to #457 and the same pinned wheel as the prior run.

The previous wrapper failed the local rejection-trace check. The new wrapper passed the same check, plus malformed input and a missing-enrollment Stop check. The missing enrollment produced an adapter error in the trace and a successful wrapper exit with empty output. These checks use synthetic inputs and establish diagnostic behavior only.

The installed build reported all five changed project commands as modified and requiring review. The exact scratch project is still trusted. The primary chat's hook approval remains untouched. Live Desktop runs are pending approval of the modified scratch commands. Capture and settlement behavior in product code has not changed.
