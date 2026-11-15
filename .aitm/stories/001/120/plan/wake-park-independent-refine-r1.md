[10:01:47]
**REFINE_120: HOLD.** The leaf as accepted will not fit four implementation agent hours. My supported estimate is about 6.0 hours (range 5.0 to 7.5). Split out the native carrier installers, scheduler first, as described below.

**What I could not check:** this session had no shell or file-read tools. I checked the source only against the anchors you supplied at `ab9db800`. I did not open `sources/hooks.py`, `monitor_control.py` or `cli.py`, did not trace the #117 to #118 dependency chain, and did not re-fetch the provider docs. JIT must confirm all of those directly.

## Dependencies
- **Declared predecessors:** #115 and #119 are both closed. #119 is Done, with the M09 destination limit that this leaf needs for postponing a stream.
- **M07 (#117) is not declared:** the Grok prompt-scoped proposal producer needs M07 admission. It is probably satisfied through #118, which is one of #119's prerequisites, but I haven't verified that.
- **#121 needs less than the whole leaf:** it drives the scheduler and does native reconciliation. It needs the scheduler, ingress and acknowledgment contract, but not the installed carriers. The installers are first needed by the M15 rehearsal.

## Boundary validation against the plan
- **Ingress:** this matches the plan, with two gaps JIT must close:
  - **Peer UID:** macOS has no `SO_PEERCRED`, so the ctypes path needs `getpeereid` there and a Linux variant.
  - **Socket binding:** `socket.bind` takes a path, not a directory handle, so it can't bind relative to the directory pinned by `_pin_directory` (`ledger.py:278`). Binding would need `fchdir`, a bind-then-verify step or another approach. The macOS 104-byte socket path limit also has to hold for the real private state directory.
- **Scheduler:** the accepted contract has only `notify` and `take_due`. The refinement's rule that a crash between dequeue and scan must not erase a wake needs a lease or acknowledgment call, which the contract doesn't have. That is a contract addition, and JIT must accept it explicitly.
- **Explicit park:** the boundary is sound. It takes only the keyed session reference and can't mutate a delivery cursor or the workflow scope, which fits `ProjectDelivery` owning cursors (`monitor_writer.py:21`).
- **Carrier install:** the boundary is sound, but it is the part that breaks the cap. It covers three different native formats, idempotence, preserving foreign entries, rollback on a refused install, unchanged tracked files and qualification in isolated homes. The Codex evidence is only local help text from the alpha build 0.169.0-alpha.11.1, so its target carrier is still unpinned.

## Scope, privacy and acceptance
- **Scope:** Epic #2, C01, production cutover, live Claude capture and the separate Claude cost gap stay out. Qualifying the Claude hook wake is separate from cost qualification.
- **Privacy is adequate:** raw locators are resolved transiently, only keyed references are persisted, there must be no raw paths after a wake is retired, and the launcher embeds no paths. The open item is that nothing says where the "approved private settings" the launcher resolves live, or who writes them.
- **Acceptance is mostly observable.** Three tests need defining at JIT:
  - **Wake retirement:** acknowledgment belongs to #121, so test it here with a fake coordinator.
  - **Fairness:** "fairness when another project is blocked" needs a measurable quota assertion.
  - **"Cannot stall the provider":** needs an explicit timeout budget.

## Estimate (agent hours)
| Unit | Hours |
|---|---|
| Scheduler: states, coalescing, fairness, monotonic backoff, rebuild after reboot, lease and acknowledgment | 1.5 |
| Ingress: socket, ctypes peer UID, bounded parsing, locator resolution, keyed persistence, retirement | 1.25 |
| `monitor park`, generic `HookSender` and the stable launcher | 0.75 |
| Three installers plus `monitor hooks install` and qualification in isolated homes | 2.0 |
| Grok prompt-scoped proposal producer (M05 carrier plus M07 admission) | 0.5 |
| **Total** | **≈6.0** |

**Unexplained assumptions:**
- The existing registry, adapter and private-file primitives can be reused without changes.
- `sources/hooks.py` already exists.
- Each provider binary actually loads the nonblocking hook event the plan chooses.
- The Codex plugin installer can run in an isolated home without a separate trust step.

## Proposed split (the smallest extraction)
- **#120, reduced (≈3.5 h):** the scheduler with the lease and acknowledgment addition, private ingress, park, the generic `HookSender` and the launcher contract, tested against a socket in isolation. It fits the cap with little margin.
- **New leaf M10b (≈2.5 h), blocked by #120:** `monitor hooks install`, the three owned native descriptors, provider-specific producers including the Grok prompt-scoped proposal, and qualification in isolated homes.

**What changes downstream:**
- #121 stays blocked only by the reduced #120.
- The M15 rehearsal must add M10b as a predecessor.
- The accepted plan's M10 file list and checklist need re-partitioning and a new plan-origin binding for M10b.
- The installer tests ("approved install with unchanged tracked files", running each installer twice, and the provider-not-stalled check against an installed carrier) move to M10b.

JIT must still independently accept the exact plan for each part: APIs, state tables, crash points, input budgets, test names, and installer ownership and rollback.
