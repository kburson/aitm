# #116 M06 liveness pickup review round 2

Claude Opus 5.5, high effort, completed the independent local pickup review on November 10, 2026.

# Verdict: HOLD

I reviewed only the supplied packet and used no tools. One blocking finding stands in the way of a PASS. It is narrow and needs a one-paragraph edit. Everything else is either resolved or can wait for implementation tests or later integration.

## Blocking finding

**B1. A disable can be rejected because of the source's state, and the edge then stays enabled.** The plan says "a substituted approved root or a mismatched approved provider tuple is rejected." A capture command names only a project and a source, so both conditions come from the source side. Rejecting a disable leaves the project/source edge's permission on. Physical root refusal blocks reads only while the substitution lasts. Here is a concrete case:
1. Codex is upgraded and the installed tuple no longer matches.
2. The owner's disable is rejected.
3. The owner rolls Codex back, the tuple matches again, and capture resumes on an edge the owner tried to revoke.

This conflicts with the parent's rule that revoked source permission ends reads. It also tells the owner "rejected" for something they are entitled to do.

**Fix:** a disable must never be rejected because of source-side conditions. Either:
- **Preferred:** apply it the same way as a proven discontinuity. Each affected stream keeps its prior verified prefix and gets an open-ended gap, and permission is committed as disabled. Or:
- **Acceptable:** hold it, since pending-disable read limits already fail closed.

Rejection stays available for:
- invalid typed input or envelopes;
- an unknown project or source;
- an enable against a substituted root or mismatched tuple.

Add a test: disable with a mismatched tuple, then restore the tuple, and no reads resume.

## Raw reads after revocation (the controlling requirement)

The parent controls here. Two rules apply:
- **Parent:** "Revoked source permission ends further reads for that project."
- **Approved M06:** "A revoked … root yields no new reads to repair a revision, even when already-staged authorized proof can settle."

A capture disable is exactly the revocation of a project/source permission. The previous reviewer's suggestion that "rows before the fence stay readable after the change commits" contradicts both rules, and the revised plan is right to reject it.

The revised plan keeps the part of Finding 7 that fits: during the pending period, reads are limited per stream at the persisted fence, and the absent-stream case affects only that stream.

One consequence has to be stated for the later work. Rows below the fence that were never read before the disable applied will never be read. They must show up as a coverage gap, not as silent undercounting. This belongs to the later owner of staged settlement (see "Later integration" below), not to M06. The fence that M06 persists, plus the stream cursor at application time, is enough to work out that interval.

## The eight earlier findings

| # | Status | Note |
|---|---|---|
| 1 Unfinished tail waits forever | **Resolved** | A physical arm plus an explicit gap is reached even when the process is dead or the final row stays partial. Waiting on the tail is gone. Gapping an open span that crosses the fence follows the parent's rule for unsplittable spans. The readers' start points look obtainable: Codex `_Turn.start` and the scanner's first held row exist. The original ordinal of a Claude provisional request is not visible in `request_prefix`. That is a check at pickup (see "Before implementation"). |
| 2 Idle stream can never qualify | **Resolved (no longer applies)** | The fence no longer depends on either reader settling. Quiet plus active streams are tested for both providers. |
| 3 One fence rule | **Resolved, better than suggested** | The arm never moves. A temporary failure keeps the arm, and a permanent one takes the gap path. The reviewer's "set it up again" would have moved the fence later. |
| 4 Absolute row number | **Resolved** | `_lines` starts at `start = 0`, and its `start`/prefix values are used directly as absolute cursor offsets and digests from the start of the file. Its ordinals are therefore already absolute, and the plan pins this down with a nonzero-resume test. Refusing an origin for an empty, unrecognized file is right: `source-origin` needs a startup digest that an empty file cannot provide. |
| 5 Strict absence walk | **Resolved** | The plan adopts the strict walk, the check after traversal, matching on any file type, and no persistence or reuse. |
| 6 Typed interface | **Resolved** | The registry, not the callback, classifies each stream. Native proof is the only input the direct calls accept. Each proof variant has its own namespace. The `apply_pending` change is stated explicitly. |
| 7 Read blocking during a pending disable | **Resolved** | The pending-period part is adopted. The part about reading after commit is correctly declined (see above). |
| 8 One pending command per edge | **Resolved, with a check** | This depends on a durable submission order actually existing (see "Before implementation"). |

The other areas you asked about:
- **Exact direct proof:** sound. Only writer-owned native proof reaches `set_permission`/`enroll_stream`, and fence references cannot act as scope markers.
- **Later ownership:** intact. Scope, staged settlement, qualification, the scheduler, migration and operations all stay with M07 and later.
- **Budget:** the cap is conservative. 4.0 − 1.7 = 2.3, and active time is at most wall time. The scope is now dense for 2.3 hours, so the reopen trigger is likely to be what decides it.

## Clarifications for the same edit (not blocking)

- **Stream first armed in a later pass:** say whether its fence sits at that later position (which the parent allows) or whether the stretch from its prior prefix to that fence becomes a gap.
- **Absence walk:** also match the original file's inode anywhere in the installation. Otherwise a Codex session that was archived and then left out by the callback gets permanently gapped as "absent."
- **Modules touched:** name the adapter modules this changes (scanner, Codex reader, Claude reader), and keep their existing tests in the green run.
- **Persistent holds:** a stream that stays duplicated, unreadable or `ValueError` holds the command indefinitely and starves later commands on that edge. Accept that as fail-closed, and say that the status shows a sanitized unavailable reason.

## Before implementation (stop and reopen planning if any fails)

- Claude can supply a provisional request's original ordinal from existing checkpoint and ledger state, without changing the cursor or checkpoint format.
- The inbox really has a persisted submission sequence that stays stable across exact retries. If it doesn't, assign one under the publication lock. Ordering by modification time or UUID does not count.
- The arm position is always at or after every persisted stream cursor. Anything lower is treated as a discontinuity.

## Tests to add

- Disable with a mismatched tuple or substituted root, then restore it, and no capture resumes.
- A new stream that appears while a disable is pending is not enrolled.
- A partial row from an active writer that completes after arming stays in the gap.
- An archived or moved Codex file is not proven absent while its inode still exists.

## Later integration (M07 and beyond)

- Collection and arming are serialized under the coordinator lease.
- Unread rows below the fence at the moment a disable applies are reported as a coverage gap.
- Settlement uses only evidence that was already staged.
