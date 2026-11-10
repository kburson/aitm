# Full-file retrieval audit

Verified the actual numbered Claude Read tool results against the exact
Git input for each round before native finalization. The reads cover
every physical line, without missing lines or mismatched content.
The extra empty element sometimes reported at EOF after a terminating
newline is outside the authored line count.

| Round | Raw input digest | Verified lines | Sanitized read evidence |
| --- | --- | ---: | --- |
| 1 | `sha256:8c99b0029127336f941c5ba79baee0e26ebb2a3627a43b8397b5bab5f05307dc` | 457 | [24 Read results](read-audit-round-1.json) |
| 2 | `sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928` | 488 | [25 Read results](read-audit-round-2.json) |

The [task-scoped instructions](review-instructions.md) were committed in the isolated review checkout before launch. Their raw SHA-256 is `fb68a7e78f108f4361b9903d2c6b6d06e8df81610dc7340e29c1370ed8a3c4b2`. Private transcript bodies and provider handles are kept outside planning. Retrieval coverage establishes the bytes returned by Read. It does not attest reviewer attention or independent execution authority.
