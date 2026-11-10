# Fresh full-file retrieval audit

Compared the numbered Read output with the exact FUR lines identified by each native response. This audit retains ranges and results only.

| Round | Raw input SHA-256 | Actual contiguous reads | Verified lines |
| --- | --- | --- | ---: |
| 1 | `sha256:1b9afd6e13275d1a35ef3be66c8ca98ac4186d0ce94f49257909b2731bb5c20f` | 1–20, 21–40, 20–20 | 40 |
| 2 | `sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0` | 1–20, 21–40, 41–42 | 42 |
