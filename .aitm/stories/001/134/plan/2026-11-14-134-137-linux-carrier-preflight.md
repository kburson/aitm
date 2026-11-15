# Linux native carrier Refine preflight for #134 and #137

The local Docker Desktop Linux arm64 VM ran the pinned provider executables from integrity-checked official npm archives in disposable, unprivileged, read-only containers. The four archive bytes were independently checked against the registry's SHA-512 integrity before extraction. ARM and x86-64 ELF types were corroborated from the extracted binaries. The Grok arm64 version output identifies build `50ca579fa996`.

| Exact official package | Executable SHA-256 | Observed evidence |
| --- | --- | --- |
| `@openai/codex@0.167.0-alpha.3.2-linux-arm64` | `e7f91e14eab4ba3a0f65047c1757b593409d4ce791ccb6ac65c67c970dfed76f` | Linux arm64 no-model launch and device login help passed |
| `@openai/codex@0.167.0-alpha.3.2-linux-x64` | `c8242fc9e1bac7c6d661a228cecfaf50e6db74da219e4a9ca8912827e11607f0` | Official archive and executable verified; launch pending |
| `@xai-official/grok-linux-arm64@1.0.77` | `b30eee14a656124ef3c9da8577b5e783ef2cffabeb2b679c5c49633e77eed574` | Linux arm64 no-model launch and device login help passed |
| `@xai-official/grok-linux-x64@1.0.77` | `b702950aa5827d855e493278ab6215a4e0f5bceb5bba6c6243a9f55cdd143b0a` | Official archive and executable verified; launch pending |

The two arm64 version and help probes ran offline with no host provider account state in the containers. Both exact builds recognized device-code sign-in. A local scratch launcher was verified in its offline check mode for each provider. It uses separate, user-owned mode-0700 state directories, one read-only binary, and the pinned image. The login route uses each provider's device-code command and requires the account owner to complete sign-in in the browser. No authorizations, model requests, native receipt, durable cursor, usage totals or target qualification resulted from preflight. The supported sign-in procedures are documented by [OpenAI](https://learn.chatgpt.com/docs/auth#login-on-headless-devices) and [Grok Build](https://docs.x.ai/build/enterprise#device-code).

For #134 the next evidence is the controlled CLI command and its adjoining request under the exact device-signed-in session, then anchored restart and archive replay. For #137 it is the exact authenticated prompt receipt and successful hook/completion join for two distinct turns across resume, followed by token reconciliation, cursor replay and a hookless control. Both stories remain in Refine until evidence and independent acceptance. Final real-host arm64 and x86-64 release qualification remains #129.
