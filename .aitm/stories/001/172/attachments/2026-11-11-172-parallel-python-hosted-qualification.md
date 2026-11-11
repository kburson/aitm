# #172 Hosted qualification of parallel Python execution

## Scope and provenance

The qualification used the exact #197 source at head
`2dd98bb7f5029188cf693e7c1317dd5fc0675e2b` and tested tree
`35ad17ad3121728482ba9acdfcdd8e724c56289f`. The reference is the
complete 445-second serial Python job in the [signed #197 run](https://github.com/kburson/aitm/actions/runs/43088954749/attempts/1).
The retained Python artifact `13889085192` was checked against its
GitHub SHA-256 digest. The serial and parallel hosted jobs report the
same macOS runner image version `20261102.0473.1`.

The [qualification workflow](https://github.com/kburson/aitm/commit/714b97972e5247ae021aeab8428669f6512442d6)
ran on a dedicated branch in AITM. It used separate hosted runner
instances for each matrix job, an eight-minute cap per job, and no
Actions dependency cache. Python used the exact source lock plus pinned
`pytest-xdist` 3.8.0 and `execnet` 2.1.2 in the trial environment.
The harness retained the complete helper suite, wheel smoke, and artifact
upload. Each worker had its own evidence file. The reconciler required
matching collection lists, controller and worker phase reports, and raw
PID-linked child coverage. Native test fixtures used a private temp root
outside coverage and artifact output.

The representative selection used the accounting, export, and Grok
pricing modules, plus the two required child-proof cases. The 68 selected
product and CLI IDs were derived independently from the serial inventory
using those declared targets. This is a predeclared selection sample for
the TIA runtime target. Separate hosted shard assignment and production
selector qualification remain in the accepted #133 work.

The [first harness attempt](https://github.com/kburson/aitm/actions/runs/43093499809)
passed the selected product tests, then failed on a malformed checksum
input in the trial script. The run was cancelled and replaced after the
checksum command passed locally. The corrected workflow supplied the
qualification measurements.

## Results

| Workload | Runner | Workers | Product and CLI IDs | Complete elapsed time |
| --- | --- | ---: | ---: | ---: |
| Serial reference | Hosted macOS | 1 | 1,071 | 7m 25s |
| Full | Hosted macOS | 2 | 1,071 | 5m 22s |
| Full | Hosted macOS | 3 | 1,071 | 2m 59s |
| Representative selection | Hosted macOS | 3 | 68 | 1m 05s |
| Full | Local macOS | 8 | 1,071 | 1m 13s |
| Representative selection | Local macOS | 8 | 68 | 23s |

The hosted measurements run from job start through artifact upload.
From workflow creation through job completion, the hosted three-worker
full job took 3m 04s and the selected job took 1m 11s. The local
measurements include dependency validation, test execution, evidence
collection, all 182 helper tests, and wheel smoke. Eight local workers
used 80% of ten available cores. Hosted runners reported three cores.

Both full hosted jobs and the full local job matched every serial test
ID and all 3,213 phase outcomes. Product and helper coverage matched
the exact executed, missing, and excluded line sets and branch arcs.
Totals were 10,655 of 11,604 product lines and 3,079 of 3,816 product
branches, plus 778 of 821 helper lines and 231 of 262 helper branches.
Both subprocess labels had successful exits, distinct observed PIDs,
and matching per-label coverage counts of 4,151 and 6,318 lines.

Both selected runs matched the exact 68-ID subset and all 204 phase
outcomes. Their measured product lines and branch arcs were contained
in the full reference. Helper coverage and subprocess evidence matched.
The comparison refused scratch receipts with a missing phase, an extra
executed line, or a changed subprocess coverage count.

[Hosted run](https://github.com/kburson/aitm/actions/runs/43093752137/attempts/1)
· [Measurement and parity receipt](parallel-python-qualification-receipt.json).

The representative selection met the three-minute target in both
environments. The full hosted three-worker sample had one second of
margin against a three-minute job target. Repeat measurements are
required to establish a sustained runtime envelope across other changes
and runner loads. All trial jobs stayed below the existing eight-minute
cap. The evidence is for qualification only. #197 remains open at its
prior head and #159 remains blocked by #157 and #158.
