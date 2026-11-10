# Full-file retrieval audit

Verified actual numbered Claude Read tool results against the exact Git
input for each round before native finalization. Each audit covers all
physical lines. The terminal newline's empty split element is not an
additional authored line.

| Round | Raw input digest | Verified lines | Sanitized read evidence |
| --- | --- | ---: | --- |
| 1 | `sha256:3549515f497a736d5cc101cb2f28aacc5c69f666936a3bdcd0d624ca1b133a07` | 774 | [20 Read results](read-audit-round-1.json) |
| 2 | `sha256:4500099ac8f04148f1f0f6ee8c2fc31c5e53cbdc16707bcc0fb16f931c97bd59` | 859 | [22 Read results](read-audit-round-2.json) |
| 3 | `sha256:ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7` | 875 | [22 Read results](read-audit-round-3.json) |

The [task-scoped instructions](review-instructions.md) were committed in the isolated worktree before launch. Raw SHA-256 `1cc33c9832432f50fd0b4c5189c023201874887ec20d93c06e8dfab8e862db6b`. Private transcript bodies and provider handles stay outside planning. Retrieval coverage establishes bytes returned by Read, without independently attesting attention or execution authority.
