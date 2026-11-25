# Disposable Codex Desktop qualification setup

Created a disposable Desktop chat in a separate standalone Git repository with no remote. The setup uses the candidate wheel from PR #460 and a private scratch effort database. The hook command checks the pinned wrapper before running it. The wrapper returns on mismatched thread input before importing the effort code or opening SQLite, then checks the wheel digest before loading it. A foreign-thread synthetic probe exited successfully and created no callback trace.

| Staged artifact | SHA-256 |
| --- | --- |
| Hook configuration | `639312a0f76fa82a0fd39615c7492c0284bcada2029902bd343c14de95c0c2a4` |
| Qualification wrapper | `e97336cdc5999a7b7d67b3ab2f304933ae67353f21ecd64894841aab83c740f6` |
| Candidate wheel | `5a85d89277cba1f4ec4901ac6fbff6a78feff24b0b72e1b368e4607843a1bdc5` |

The five scratch-only callbacks are staged for Desktop review. The original chat's hook configuration and trust were left untouched. The scratch database has zero enrolled attempts at setup and contains no live callback evidence yet. Qualification remains pending human review of the hooks in the disposable chat and a fresh owner turn that dispatches one benign app subagent. The readback helper checks callback identities, exact retained settlement, byte-identical story-switch and restart replay, and the absence of a Git remote. It currently reports no callbacks observed.
