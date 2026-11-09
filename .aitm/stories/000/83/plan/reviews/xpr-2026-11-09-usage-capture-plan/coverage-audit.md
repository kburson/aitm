# Fresh full-file retrieval audit

Compared the numbered Read output with the exact FUR lines identified by each native response. This audit retains ranges and results only.

| Round | Raw input SHA-256 | Actual contiguous reads | Verified lines |
| --- | --- | --- | ---: |
| 1 | `sha256:d4c46b81bb889277cd5a8563251317bfa15788081e9471c4a014d473eb378cdb` | 1–20, 21–40, 41–60, 61–80, 81–100, 101–120, 121–140, 141–150 | 150 |
| 2 | `sha256:07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5` | 1–20, 21–40, 41–60, 61–80, 81–100, 101–120, 121–140, 141–160, 161–180, 181–190 | 190 |
