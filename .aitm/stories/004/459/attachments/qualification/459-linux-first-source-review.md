# Story #459 Linux-first source and CI qualification

Claude Sonnet 5.5 approved the Linux-first workflow and documentation delta
on exact head `47d82b1c038fd24bc2350dad073e86dbb35f9dbc`, reviewed tree
`a7c0e6b8cc2e7e2f253967616a0bbe5307275665`, and base `0f8c6ff70b5112bd3a17af3a2ab5665e347a416c`.
The exporter and its tests are byte-identical to the independently approved
product source at `51d19ac11c8c515abf95664058b577e5bc2a7452`.

The Linux authenticated PR gate passed on tested merge `d48225442d0fd969acff9d2d12131adc0ebbc3c8`.
Ubuntu passed 236 installed-wheel effort tests. Windows passed its three
targeted checks for canonical bytes and the installed CLI. The macOS native
workflow selected no job. The previous macOS runner cancellations remain
historical evidence. The owner's revised delivery direction allows this PR
to proceed with the matched Ubuntu and Windows results. The 39 native macOS
tests passed locally as supplemental evidence.

[Owner direction](../../plan/2026-11-26-linux-first-ci.md) · [Original product review](459-independent-source-review.md) · [Authenticated Linux CI](459-linux-first-ci.json) · [Platform readback](459-linux-first-platform-checks.json).
