# #116 M06 independent source re-review

Claude Opus 5.5, medium effort, completed an independent local review on November 10, 2026. Candidate head `198b75431f5a929ffd7178b2d17e463e717d956e`, tree `8f3aeb384b7b89ae573b5c563bd05f6c30656760`, trunk base `37a22922f072e39c35434ae645a1c20692b8da01`. [Signed hosted evidence](https://github.com/kburson/aitm/actions/runs/42875770798/attempts/1).

# AITM #116 M06 independent re-review: head `198b7543`, tree `8f3aeb38`

**Verdict: HOLD.** The repair resolves both earlier blockers as they were written. It also adds a new problem: a source-wide capture change can now get stuck in the queue forever. That is blocking finding A below.

This review uses only the supplied packet. I ran no tools and didn't replay CI. The signed evidence names head `198b7543`, tree `8f3aeb38` and base `37a22922`. It reports status `pass` for all six jobs, with `tested` set to merge commit `60817ecb`. Its count of 676 tests equals the earlier 671 plus the 5 new tests in this diff. I'm relying on that evidence as given and did not check the signature.

## Earlier blockers

| # | Earlier blocker | Status |
|---|---|---|
| 1 | Historical boundary chosen as the fence | **Resolved for completed native requests.** There is one gap the packet can't settle (see "Evidence needed before PASS"). |
| 2 | A brief lack of proof turned into a permanent rejection | **Resolved.** |

**How blocker 1 was fixed:**
- **The fence must come after a current, complete frontier.** Before a change is applied, the writer records the stream's newest complete position as its frontier (`_native_delta` with `arm=True`, `:680-684`). That read starts from the latest epoch's `observed` checkpoint (`:715-721`).
- **Only the first newer boundary qualifies.** `_verify_next` (`:748-762`) accepts only the first boundary with an ordinal above `frontier.last_ordinal`, and the file must have grown past the frontier.
- **Nothing can go backwards.** `_epoch` rejects a lower ordinal, and a frontier earlier than the last epoch's `observed` position (`:806-811`).
- **Old proofs can't be reused.** Proofs are keyed per capture change and stream, must match the current armed frontier by identity (`:780`), and are cleared on re-arm or completion (`:736-737`, `:786-790`).
- **Claude late revisions are handled.** A revision keeps its original ordinal (`lineage` requires `record.boundary.ordinal == prefix.ordinal`). Any revision at or below `last_ordinal` is filtered out (`:751`), so it can't become a fence. It is judged by its original span, which keeps admitted work eligible after a disable.

**How blocker 2 was fixed:**
- An `OSError` from the I/O inside `_native_delta`, from `locate` or from the root check now becomes `BoundaryUnavailable` (`:653-656`, `:945-950`, `:315-319`).
- Missing, ambiguous or discontinuous proof also raises `BoundaryUnavailable` (`:663`, `:679`, `:757`, `:761`).
- `apply_pending` keeps the command queued in those cases (`:1025-1028`). The parametrized test covers both the I/O and the missing-proof paths.

## Blocking finding A: an idle, finished or deleted stream permanently stalls every source-wide capture change on that edge

**Code evidence**
- `known` is every stream that has ever had an epoch on the edge (`:938-940`). Nothing ever retires a stream.
- `_apply` needs a locator for every known stream (`:956-957`). It then needs `_verify_next` to succeed for every armed frontier (`:984-987`).
- `_verify_next` raises `BoundaryUnavailable` unless the file grew and a new boundary appeared (`:753-757`).
- A held command blocks every later capture command on the same edge (`held_edges`, `:1015`, `:1027`).
- While anything is pending on the edge, `_require_direct_proof` also refuses `enroll_stream` and direct `set_permission` (`:834-835`).

**Scenario**
1. Project P enables capture on source S. Desktop session A is enrolled, then finishes. Session B is enrolled and stays active.
2. The owner runs `monitor capture disable`. The writer arms frontiers for A and B and saves them.
3. B keeps producing new boundaries. A never writes another row, so its `_verify_next` raises `BoundaryUnavailable` on every pass.
4. The disable stays `queued` forever, and B's new usage is still eligible.
5. Any later re-enable or disable on the edge is skipped behind the stuck command.

The same happens in these cases:
- A's file is deleted (for example, by transcript cleanup). Discovery can't find it, so `known - by_stream` is never empty.
- A's file is rotated or replaced. The continuity check fails on every pass (`:679`).
- A's new rows carry a different client version. They are filtered out (`:688-691`), so no qualified boundary ever appears.

The test `..._across_restart` treats this behaviour as correct: it applies only once both logs have grown.

Waiting is right only when proof is temporarily unavailable. For a quiet stream, the proof will never exist, so waiting means the owner's disable is never applied while the other streams keep being admitted.

**Needed**
- **Fence a quiet stream at its frontier.** When the stream has a complete, stable tail at its armed frontier and nothing new after it, place the fence at the frontier itself (ordinal `last_ordinal + 1`, half-open). Every later row has a higher ordinal, and Claude revisions keep their original ordinal, so this is sound.
- **Handle missing streams explicitly.** A stream that is gone for good needs a proven final state instead of waiting forever.
- **Add tests.** One should disable with one idle stream and one active stream. Another should disable after an enrolled stream's file is removed.

## Evidence needed before PASS: first-after-frontier ordering for requests in progress

`last_ordinal` is the highest of three values: `checkpoint.provider.ordinal`, the boundaries the arm read observed, and the earlier `last_ordinal` (`:695-698`). Nothing checks that the selected boundary's row physically sits after the frontier offset.

The risk is a request that has started but not finished when the frontier is recorded:
- a Desktop turn whose begin rows are written but whose usage row isn't yet, or
- a Claude row that hasn't reached the commit frames yet.

If its boundary ordinal is above `provider.ordinal`, it can become the next fence even though it predates the frontier. On a re-enable, that makes a span that started during the disabled interval eligible.

The packet doesn't show the Codex checkpoint ordinal or how Claude commit frames are cut, so I can't confirm or rule this out. Two ways to clear it:
- Show that `provider.ordinal` covers every scanned row, and add a test that records a frontier in the middle of a turn, for both Desktop and Claude.
- Or only accept fence rows the verify read scanned at or after `frontier.checkpoint.cursor.offset`.

## Assessment by area

- **First qualified boundary after the frontier:** passes for completed requests and Claude revisions. Requests in progress are the open item above.
- **Durable arm and exact retries:**
  - Passes. The arm is saved in `pending_capture` before any proof is read (`:1019-1024`), and the test survives a writer restart.
  - Retries apply the same decision only when ordinal, ref, both frontiers and direction all match (`:798-805`).
  - The receipt and epochs are written in one `_save`, and the pending entry is cleared in that same write.
- **Physical continuity:** passes.
  - The scanner authenticates the prior prefix (`_verify_prior`).
  - Locator and incarnation must match, and the offset can't go backwards (`:670-679`).
  - The file is probed before and after the read (`:648-662`), and the tail must be complete when the frontier is recorded.
- **Transient vs proven-invalid:** blocker 2 is fixed. Finding A is the opposite mistake: a condition that will never clear is treated as temporary.
- **All-stream atomicity:**
  - Passes for safety. All proofs are computed before any epoch is written (`:984-989`), and a mismatched pending set is rejected.
  - Fails for liveness (finding A).
- **Half-open interval eligibility:** passes. `span_disposition` ignores fences at or after `end`, takes the state from the last fence at or before `start`, and returns UNKNOWN when a fence inside the span changes state (`:901-912`).
- **Root authorization:**
  - Passes. `_check_capture_root` runs before any read and again in `_epoch`, so a replaced root is never reread (the test enforces this with a `read_delta` that fails if called).
  - The namespace, key, platform, surface and version checks are kept.
- **Scope boundaries:**
  - Kept: no service, no adoption and no CLI change in this diff.
  - Changes against the pickup: the `apply_pending(..., boundary_verifier)` seam is now `locate`, and `verify_boundary` takes an armed frontier. Later scheduler leaves must follow the new shape.
  - `view(_confirm_publication=True)` is called, but its definition isn't in this diff. CI implies it already exists, but I couldn't review it here.

## Non-blocking risks

- **Two commands on one edge could both be armed.** The command path never checks for an existing pending entry on the same edge with a different command ID (the direct path does, `:834`). If `iter_pending` order isn't stable, two commands on one edge could both be armed. The command that applies second would then be rejected as stale, so the owner's latest intent could lose.
- **Unfiltered `locate` results reject a disable.** Locators for unenrolled streams raise `ConflictError` and record a rejection (`:954-955`) instead of being ignored. A `locate` that returns everything discovery finds would therefore reject the disable, leaving capture enabled.
- **A replaced root rejects a disable.** `_check_capture_root` raises `ConflictError` when the root's identity changed, so the disable is recorded as rejected and permission stays enabled. Reads are still refused, so the impact is low.
- **Adapter errors can reject.** A `ValueError` escaping the adapter (for example, `run`'s "Claude commit prefix moved backwards") becomes a rejection instead of a hold.
- **Nested Claude streams never become eligible.** They are filtered out by `stream_ref` (`:692`). This fails closed, but it should be stated explicitly in scope.

## Earlier non-blocking items

- **Unenrolled streams during a disable:** partly addressed. `locate` now receives the known streams, but extra locators still cause a rejection.
- **One idle stream stalls an edge:** now worse and blocking (finding A).
- **`darwin` config queued but doomed:** not addressed.
- **`root.absolute()` keeping `..` / unresolved monitor-root comparison:** not addressed.

**Verdict: HOLD on finding A.** The in-progress ordering evidence is also needed before PASS.
