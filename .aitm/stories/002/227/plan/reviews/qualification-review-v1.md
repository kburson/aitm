# #227 independent qualification review

**Verdict — changes requested.** Signed 2026-11-11 UTC by Codex `/root/pickup186`, a separate reviewer from the implementer. The evidence qualifies the exact historical parity and live capability findings. Two fixture corrections are required for the complete C01 handoff.

| Reviewed artifact | SHA-256 |
| --- | --- |
| `qualification.md` | `96e94f3346c9c0f51c672f287542b9bdd2ef426233819454222c83e33fe762bc` |
| `qualification.json` | `de3aa2b01368dbba28cfef1dea60080549a4ff8f40faa853f13e48e082d12765` |
| `shared-fixtures.json` | `7590d3fbd1648819c8de5a5e864b5d89b2d3fe54dbb788716fdc92992e8f035b` |

Reviewed against the exact accepted Design, Plan and JIT and the parent C01 section. [Accepted C01](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c01-freeze-input-and-parity-evidence)

## Required corrections

1. Supply the inputs needed to replay the portable cases from the published fixture. The manifest contains actor, story, phase and interval bounds. The executable helper separately supplies the project, story ancestry and states, logical turn, role, attempt and coverage. Add shared defaults, explicit graph and lifecycle input, and an explicit logical turn shared by the in-turn tool and its enclosing turn. Keep the held admission and usage-assurance conditions explicit. These inputs let C03, C05 and C06 reproduce the same case without inheriting private scratch helper behavior.
2. Exercise the Actual delta and unchanged Cost with both timing variants through the same read view. The current check folds baseline and extended timing separately, then invokes Cost twice against the same unchanged usage-only tree. It proves the arithmetic and a fixed selected usage result. Build the two local views with the respective admitted timing variants and identical selected usage evidence, then assert the Actual delta and exact unchanged Cost across those views.

## Verified evidence

- Independently rebuilt the two pinned snapshot and validation pairs and the #181 HTML in memory using the delivered source tree. All five raw outputs and SHA-256 values match. The validation files bind the exact snapshot bytes. #181 has 10,605,711 ms of partial Actual, consisting of 13,754 direct and 10,591,957 descendant milliseconds. #111 has 774,000 ms implementation elapsed and Unknown all-phase elapsed. Both use no usage selector.
- Matched all 27 claimed timing receipt hashes against the raw Git blobs and delivered reader's admitted registrations at the #181 pin. Verified the #111 seed digest. All nine recorded Project Actual values match the projected values under decimal half-even rounding, and all retain partial coverage and blank Cost.
- The test log records 61 passing dashboard tests. Independent arithmetic agrees with all six cases. The unauthenticated timing test passes a pre-held gap to the fold, as the evidence says. C03 retains native admission qualification and C05/C06 retain production projection qualification.
- Live GitHub and Project readbacks show #203 Closed Completed and Done, with PR #211 merged at `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`. #204, #209, #210, #119–#124 and Core #51 remain open. Independently ran the current-source monitor report with installed distribution metadata and a disposable UUID and reproduced exit 1 and `monitor-report-unavailable`. Fenced usage publication, exact pricing report and compatible receiver are still required for automatic Cost. [Native disposition delivery](https://github.com/kburson/aitm/pull/211) · [Fenced reports](https://github.com/kburson/aitm/issues/123) · [Compatible export](https://github.com/kburson/aitm/issues/124) · [Core usage ingress](https://github.com/kburson/aitm/issues/51)
