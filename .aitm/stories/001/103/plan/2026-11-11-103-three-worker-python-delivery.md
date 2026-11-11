# #103 Three-worker Python CI delivery

The owner directed delivery of the qualified three-worker Python
workflow with the eight-minute limit. PR #197 stays open and #159
stays blocked by #157 and #158. The
[prior qualification](../../172/attachments/2026-11-11-172-parallel-python-hosted-qualification.md)
compared the full product and CLI suite against its signed serial reference.

## Production candidate

[PR #246](https://github.com/kburson/aitm/pull/246) runs the full product
and CLI suite with three pytest-xdist workers and `worksteal` on the
existing qualified runner. The dev lock pins pytest-xdist 3.8.0 and
execnet 2.1.2. Private fixture roots remain in place. The observer emits
one receipt per worker and one controller receipt. Before product
coverage is combined, reconciliation requires the exact expected
workers, matching inventories, and matching phase reports. Child exits
are associated with their raw PID-linked coverage. The existing collector
still checks the complete inventory, coverage floors, wheel and evidence.
The literal-base lane remains serial. Both Python jobs retain the
480-second cap.

Literal base `21b06b2b8be47adcf4c3c747ba7c0a6469196f79`, head
`60205b332d88c322e1c75d7b81f5e17b4f97cf11`, GitHub test merge
`3dc52a809f980d19a2928bba93ef7d968e7cb327`, and exact tree
`fb51558994097a3e488010061a0b3b53c1b24f41`. The initial PR event was
superseded by a documentation-only follow-up before final validation.

The parallel subprocess regression reproduced the missing worker
receipts before the fix. Eleven observer tests passed with the fix,
including actual serial and xdist subprocesses and rejection of
incomplete or inconsistent worker receipts. The local CI-helper lane
passed all 190 tests with 802 of 845 lines covered, including all 59
observer lines. Ruff and actionlint passed.

The local production implementation with three workers passed all 1,071
product and CLI tests. It matched the signed serial reference's exact
inventory, all 3,213 phase outcomes, and product line and branch coverage.
Both required subprocesses matched their PID-linked records, with 4,151
covered lines for `cli-help` and 6,318 for `service-one-shot`.

## Source inspection and hosted checkpoint

An independent Codex reviewer inspected the exact head and tree above
and found no actionable source findings. The reviewer checked the pinned
actionlint result, the changed shell block, fixture isolation, worker
receipts, and the untouched gate policy and collector. The review
confirmed that workflow triggers, concurrency, runner selection and job
limits were unchanged. This was source-only inspection. The #103
merge-authorizing review follows signed hosted CI on the exact candidate.

The [initial event](https://github.com/kburson/aitm/actions/runs/43095662569)
was followed by the [exact-head event](https://github.com/kburson/aitm/actions/runs/43095765407).
The latter queued with zero jobs. A single close/reopen on #246 retained
the same base, head and tree and produced test merge
`91018f05129b0ae96ead71f082ebfe21abf71ba3`. Its
[fresh event](https://github.com/kburson/aitm/actions/runs/43096622316)
was also queued with zero jobs at this checkpoint. The workflow is active
and Actions permissions are enabled. The queue cause remains unverified.
The eight-minute execution cap applies once a job starts.

Keep delivery held for the canonical exact-head signed CI result, the
independent merge-authorizing review and trusted verifier. After an
authorized merge, verify the exact trunk push, full inventory, product
coverage, both subprocess proofs, helper results and wheel evidence.
